"""Parser for CMSSW step{N}_TimeMemoryInfo.log files.

Extracts per-event TimeEvent (CPU time) and PostProcessPath MemoryCheck
(VSIZE, RSS) records and joins them on event number. Produces the summary
text block written to step{N}.txt by `make_get_time_memory_summary.py`.

Public API preserved (TimeMem.Get_TimeMem, TimeMem.summary) since several
scripts import this module by name.
"""

from __future__ import annotations

import re

import pandas as pd


_TIME_EVENT = re.compile(r"^TimeEvent")
_MEMORY_HEADER = re.compile(r"%MSG-w MemoryCheck:  PostProcessPath")


class TimeMem:
    """Stateful parser. Call Get_TimeMem(path) then summary(out_path)."""

    def Get_TimeMem(self, input_data: str) -> pd.DataFrame:
        self.event1: list[int] = []   # event number from TimeEvent
        self.time:   list[float] = []  # wall-clock per event
        self.event2: list[int] = []   # event number from MemoryCheck
        self.vsize:  list[float] = []
        self.rss:    list[float] = []

        # State machine: when we see the MemoryCheck header line, the next
        # non-header line carries vsize/rss numbers.
        await_mem_values = False

        with open(input_data, "r") as fh:
            for line in fh:
                if _TIME_EVENT.match(line):
                    parts = line.split()
                    self.event1.append(int(parts[1]))
                    self.time.append(float(parts[3]))
                    continue

                if _MEMORY_HEADER.match(line):
                    parts = line.split()
                    if len(parts) < 10:
                        # Header without an explicit event number — reuse the
                        # most recent TimeEvent's id.
                        self.event2.append(self.event1[-1])
                    else:
                        self.event2.append(int(parts[9]))
                    await_mem_values = True
                    continue

                if await_mem_values:
                    parts = line.split()
                    self.vsize.append(float(parts[4]))
                    self.rss.append(float(parts[7]))
                    await_mem_values = False

        print(len(self.vsize), len(self.rss), len(self.event2), len(self.time))

        df_time = pd.DataFrame({"event": self.event1, "time": self.time})
        df_mem = pd.DataFrame({"event": self.event2, "vsize": self.vsize, "rss": self.rss})
        return pd.merge(df_time, df_mem, on="event", how="outer").sort_values(by="event")

    def summary(self, output_data: str) -> None:
        """Write the canonical step{N}.txt summary block.

        Format must stay byte-for-byte compatible — make_webpage.py renders
        it as plain text and downstream tooling greps it.
        """
        n = len(self.time)
        max_v = max(self.vsize)
        max_r = max(self.rss)
        evt_max_v = self.event2[self.vsize.index(max_v)]
        evt_max_r = self.event2[self.rss.index(max_r)]
        max_t = max(self.time)
        evt_max_t = self.event1[self.time.index(max_t)]

        # M1 = drop first event (warm-up). M8 = drop first 8 (more aggressive warm-up).
        max_t1 = max(self.time[1:])
        max_t8 = max(self.time[8:])
        evt_max_t1 = self.event1[self.time.index(max_t1)]
        evt_max_t8 = self.event1[self.time.index(max_t8)]

        with open(output_data, "w") as f:
            f.write(f"Summary for {n} events\n")
            f.write(f"Max VSIZ {max_v} on evt {evt_max_v} ; max RSS {max_r} on evt {evt_max_r}\n")
            f.write(f"Time av {sum(self.time) / n:0.5f} s/evt   max {max_t} s on evt {evt_max_t}\n")
            f.write(f"M1 Time av {sum(self.time[1:]) / (n - 1):0.5f} s/evt   "
                    f"max {max_t1} s on evt {evt_max_t1}\n")
            f.write(f"M8 Time av {sum(self.time[8:]) / (n - 8):0.5f} s/evt   "
                    f"max {max_t8} s on evt {evt_max_t8}")
