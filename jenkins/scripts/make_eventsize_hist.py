"""Build per-step history CSV across releases for one workflow.

Reads JSONs already published under RESULT_PATH/circles/web/data/ (made by
make_eventsize-json.py earlier) and emits history_<workflow>_<step>.csv with
one row per release: <release>,<avg_uncom_kB>,<avg_comp_kB>.

draw_eventsize.py consumes this CSV next.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


def release_sort_key(release: str) -> tuple:
    """Mirror the original sort: by major.minor.patch tokens then by name length."""
    return (release.split("_")[1:4], 10 - len(release.split("_")), len(release))


def main() -> None:
    args = _common.make_parser("Event-size release history CSV", need=("workflow",)).parse_args()
    workflow = args.workflow
    if not workflow:
        sys.exit("--workflow is required")

    data_root = args.profile_data
    json_root = _common.result_subdir("circles", "web", "data")

    releases = sorted(os.listdir(data_root), key=release_sort_key)

    for step in ("step3", "step4", "step5"):
        out = f"history_{workflow}_{step}.csv"
        rows: list[str] = []

        for release in releases:
            json_path = os.path.join(json_root, f"{release}_{workflow}_{step}_eventSize.json")
            if not os.path.isfile(json_path):
                continue
            with open(json_path) as f:
                data = json.load(f)
            events = int(data["total"]["events"])
            if events == 0:
                continue
            uncom = data["total"]["size_uncom"] / events
            compr = data["total"]["size_compr"] / events
            rows.append(f"{release},{uncom},{compr}\n")

        if not rows:
            continue
        with open(out, "w") as f:
            f.writelines(rows)


if __name__ == "__main__":
    main()
