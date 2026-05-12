"""Pre-create the result directory tree on EOS and stage cmdLog_profiling files.

Sweeps every (release, arch, workflow) found under DATA_DIR and ensures a
matching subtree exists under each RESULT_PATH/<category>/ that the rest of
the pipeline writes into. Also copies cmdLog_profiling.sh -> cmdLog_profiling.txt.

The original implementation called `cp` with `os.system` and missed the parent
mkdir, producing dozens of "cannot create regular file" errors per build. This
version uses `shutil.copy2` and creates the parent directory beforehand.
"""

from __future__ import annotations

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _common


def main() -> None:
    data_path = _common.DATA_DIR
    results_path = _common.RESULT_PATH

    if not os.path.isdir(data_path):
        sys.exit(f"profiling data root not found: {data_path}")
    if not os.path.isdir(results_path):
        sys.exit(f"web results root not found: {results_path}")

    cmssw_releases = sorted(os.listdir(data_path))

    # Categories that mirror the (release, arch, workflow) tree. comp_igprof
    # and summary_plot_html have flat layouts so they're skipped here.
    categories = [
        d for d in os.listdir(results_path)
        if d not in {"comp_igprof", "summary_plot_html"}
    ]

    for release in cmssw_releases:
        release_dir = os.path.join(data_path, release)
        archs = os.listdir(release_dir)
        if not archs:
            continue
        gcc = archs[0]  # one production arch per release; matches inline shell convention.

        workflows = os.listdir(os.path.join(release_dir, gcc))
        for workflow in workflows:
            for category in categories:
                target = os.path.join(results_path, category, release, gcc, workflow)
                os.makedirs(target, exist_ok=True)

            src = os.path.join(release_dir, gcc, workflow, "cmdLog_profiling.sh")
            dst = os.path.join(results_path, "cmdlog", release, gcc, workflow, "cmdLog_profiling.txt")
            if not os.path.isfile(src):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


if __name__ == "__main__":
    main()
