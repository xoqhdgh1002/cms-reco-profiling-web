"""Run a comparison shell (N03 timeDiff or N04 compareProducts) for the given
release vs the previous release in the data tree, write step{N}.txt under
<release>/<arch>/<workflow>/.

Inline shell then xrdcopies the <release>/ tree to either TimeDiff/ or CompProd/.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _common


def release_sort_key(release: str) -> tuple:
    """Sort releases by major.minor.patch tokens, mirroring the original."""
    return (release.split("_")[1:4], 10 - len(release.split("_")), len(release))


def previous_release(data_path: str, release: str) -> str:
    """The release immediately preceding `release` in the sorted data tree."""
    releases = sorted(os.listdir(data_path), key=release_sort_key)
    idx = releases.index(release)
    return releases[idx - 1]


def main() -> None:
    parser = _common.make_parser(
        "Run a comparison operator (N03/N04 shell) and emit step{N}.txt files.",
        need=("release", "workflow"),
        extra=[("--operator", dict(type=str, required=True,
                                   help="comparison shell: N03_timeDiffFromReport.sh "
                                        "or N04_compareProducts.sh"))],
    )
    args = parser.parse_args()

    data_path = args.profile_data
    new = args.release
    old = previous_release(data_path, new)
    workflow = args.workflow
    operator = args.operator

    new_arch = os.listdir(os.path.join(data_path, new))[0]
    old_arch = os.listdir(os.path.join(data_path, old))[0]

    out_root = os.path.join(new, new_arch, workflow)
    os.makedirs(out_root, exist_ok=True)

    for step in ("step3", "step4", "step5"):
        new_log = _common.step_file(new, new_arch, workflow, step,
                                    "_TimeMemoryInfo.log", base=data_path)
        old_log = _common.step_file(old, old_arch, workflow, step,
                                    "_TimeMemoryInfo.log", base=data_path)
        if not (os.path.isfile(new_log) and os.path.isfile(old_log)):
            continue

        # The comparison shells (N03/N04) take basenames without suffix and
        # add ".log" / ".root" themselves — match the historical contract.
        old_base = _common.step_file(old, old_arch, workflow, step, "", base=data_path)
        new_base = _common.step_file(new, new_arch, workflow, step, "", base=data_path)
        out = os.path.join(out_root, f"{step}.txt")
        os.system(f"source ./{operator} {old_base} {new_base} > {out}")


if __name__ == "__main__":
    main()
