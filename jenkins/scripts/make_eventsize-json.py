"""Convert `edmEventSize` text output into JSON for the circles pie-chart UI.

Input:  edmEventSize text file. First line carries the path to the .root file
        (from which we recover release / arch / step). Second line is a
        column header, skipped. Subsequent lines are either:

            <collection>:<branch>  (TYPE)            <uncomp>  <comp>
        or:
            <collection>:<sub_branch>                <uncomp>  <comp>

        The first form starts a new module; the second is folded into the
        running module's totals.

Output: <release>_<arch>_<step>_eventSize.json with the structure expected
        by results/circles/web/eventsize.php.

Sizes are stored in kB and multiplied by nEvents (the per-event size
already comes through the file: edmEventSize prints byte-per-event values,
so multiplication restores the integral that the PHP UI expects).
"""

from __future__ import annotations

import json
import os
import sys


def find_release_spec_step(first_line_tokens: list[str]) -> tuple[str, str, str]:
    """Recover (release, arch, step) from the first-line CMSSW path token."""
    for tok in first_line_tokens:
        if "CMSSW" not in tok:
            continue
        parts = tok.split("/")
        for i, p in enumerate(parts):
            if "CMSSW" in p:
                release = p
                arch = parts[i + 2]
                step = parts[i + 3].replace(".root", "")
                return release, arch, step
    raise ValueError("no CMSSW path token found in first line")


def main(filename: str) -> None:
    modules: list[dict] = []
    total_uncom = 0.0
    total_compr = 0.0
    n_events = 0
    release = arch = step = ""

    with open(filename) as f:
        for line_idx, line in enumerate(f):
            tokens = line.split(" ")

            # Line 0: "...nEvents N" — last token is the event count.
            if line_idx == 0:
                n_events = int(tokens[-1].replace("\n", ""))
                release, arch, step = find_release_spec_step(tokens)
                continue
            # Line 1: column header.
            if line_idx == 1:
                continue

            # Defensive: trailing blank lines or short lines from edmEventSize.
            try:
                disc = tokens[1]
                size_uncom = float(tokens[-2])
                size_compr = float(tokens[-1].replace("\n", ""))
            except (IndexError, ValueError):
                break

            uncom_kb = (size_uncom / 1024.0) * n_events
            compr_kb = (size_compr / 1024.0) * n_events

            if "(" in disc:
                # Top-level module line: "collection:branch  (TYPE)  uncom  comp"
                collection = tokens[0].split(":")[0]
                type_label = disc.replace("(", "").replace(")", "")
                modules.append({
                    "events": n_events,
                    "label": collection,
                    "size_uncom": uncom_kb,
                    "size_compr": compr_kb,
                    "type": type_label,
                })
                print(modules[-1])

            total_uncom += uncom_kb
            total_compr += compr_kb

    output = {
        "modules": modules,
        # Resource labels embedded for the circles UI's resource picker.
        "resources": [
            {"size_uncom": "Average Uncompressed Size"},
            {"size_compr": "Average Compressed Size"},
        ],
        "total": {
            "events": str(n_events),
            "label": "step3_eventsize",   # historical literal — UI keys off this
            "size_uncom": total_uncom,
            "size_compr": total_compr,
            "type": "job",
        },
    }

    out_name = f"{release}_{arch}_{step}_eventSize.json"
    with open(out_name, "w") as fout:
        json.dump(output, fout, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing Input file!!")
        sys.exit(-9)
    main(sys.argv[1])
