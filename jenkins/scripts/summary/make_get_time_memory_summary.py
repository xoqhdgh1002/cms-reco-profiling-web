"""For one (release, arch, workflow), parse step{N}_TimeMemoryInfo.log and
write step{N}.txt summary in the working directory.

The inline shell xrdcopies `step*.txt` from cwd to EOS.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _common
import Log_check


def main() -> None:
    args = _common.make_parser("Time/Memory summary writer").parse_args()
    release, arch, wf = args.release, args.architecture, args.workflow

    log_parser = Log_check.TimeMem()

    for step in _common.steps_for(wf):
        tmi = _common.step_file(release, arch, wf, step, "_TimeMemoryInfo.log",
                                base=args.profile_data)
        if not os.path.isfile(tmi):
            continue
        log_parser.Get_TimeMem(tmi)
        log_parser.summary(f"{step}.txt")


if __name__ == "__main__":
    main()
