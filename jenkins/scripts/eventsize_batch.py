"""Run edmEventSize on each step's .root and convert to JSON.

Output filename: <release>_<arch>_<step>_eventSize.json (produced by
make_eventsize-json.py). Inline shell xrdcopies `*.json` from cwd to
results/circles/web/data/.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

JSON_BUILDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_eventsize-json.py")


def main() -> None:
    args = _common.make_parser("edmEventSize batch + JSON conversion").parse_args()
    release, arch, wf = args.release, args.architecture, args.workflow

    for step in ("step3", "step4", "step5"):
        root_path = _common.step_file(release, arch, wf, step, ".root", base=args.profile_data)
        if not os.path.isfile(root_path):
            continue
        os.system(f"edmEventSize -o eventSize_{step}.txt -F {root_path}")
        os.system(f"python3 {JSON_BUILDER} eventSize_{step}.txt")


if __name__ == "__main__":
    main()
