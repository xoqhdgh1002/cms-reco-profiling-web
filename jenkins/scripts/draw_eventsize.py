"""Plot per-event uncompressed/compressed size history.

Two flavours per step:
    Recent8EventSize_<workflow>_<step>.png  -- last 8 releases
    EventsizeSummary_<vers>_<workflow>_<step>.png  -- only releases in <vers>

Inline shell xrdcopies `*.png` from cwd to circles/web/hist/.

Usage:
    python3 draw_eventsize.py <RELEASE> <WORKFLOW>
"""

from __future__ import annotations

import csv
import os
import sys

import matplotlib.pyplot as plt


def read_history(csv_path: str) -> tuple[list[str], list[float], list[float]]:
    versions, uncom, compr = [], [], []
    with open(csv_path) as f:
        for row in csv.reader(f):
            versions.append(row[0].replace("CMSSW_", ""))
            uncom.append(round(float(row[1]), 1))
            compr.append(round(float(row[2]), 1))
    return versions, uncom, compr


def slice_for_job(job: str, version_window: str,
                  versions: list[str], uncom: list[float], compr: list[float]
                  ) -> tuple[list[str], list[float], list[float]]:
    if job == "A":
        return versions[-8:], uncom[-8:], compr[-8:]
    if job == "B":
        idxs = [i for i, v in enumerate(versions) if version_window in v]
        if not idxs:
            return [], [], []
        lo, hi = min(idxs), max(idxs) + 1
        return versions[lo:hi], uncom[lo:hi], compr[lo:hi]
    raise ValueError(job)


def render(version_short: str, workflow: str, step: str, job: str,
           versions: list[str], uncom: list[float], compr: list[float]) -> None:
    plt.rcParams["figure.figsize"] = (20, 10)
    plt.rc("font", size=20)
    plt.rc("axes", labelsize=20)
    plt.rc("xtick", labelsize=20)
    plt.rc("ytick", labelsize=20)
    plt.rc("legend", fontsize=20)

    fig, ax1 = plt.subplots()
    line1 = ax1.plot(versions, uncom, "--bo",
                     label=f"Average Uncompressed Size ({workflow})",
                     color="blue", linewidth=3, markersize=8)
    for x, y in zip(versions, uncom):
        ax1.text(x, y, y, fontsize=20, color="black",
                 horizontalalignment="right", verticalalignment="bottom")

    ax2 = ax1.twinx()
    line2 = ax2.plot(versions, compr, "--bo",
                     label=f"Average Compressed Size ({workflow})",
                     color="green", linewidth=3, markersize=8)
    for x, y in zip(versions, compr):
        ax2.text(x, y, y, fontsize=20, color="black",
                 horizontalalignment="left", verticalalignment="top")

    ax1.set_xlabel("CMSSW Version", fontsize=25)
    ax1.set_ylabel("Size/Event [kB]", fontsize=25)
    ax2.set_ylabel("Size/Event [kB]", fontsize=25)
    lines = line1 + line2
    ax1.legend(lines, [l.get_label() for l in lines])

    if job == "A":
        plt.savefig(f"Recent8EventSize_{workflow}_{step}.png")
    else:  # job == "B"
        plt.savefig(f"EventsizeSummary_{version_short}_{workflow}_{step}.png")
    plt.close()


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: draw_eventsize.py <RELEASE> <WORKFLOW>")
        sys.exit(-9)

    release = sys.argv[1]
    workflow = sys.argv[2]

    # version_short: "16_0" (used in output filename "EventsizeSummary_16_0_...")
    version_short = "_".join(release.split("_")[1:3])
    # version_window: "16_0_4" — used to filter releases inside the same patch series
    version_window = "_".join(release.split("_")[1:4])

    for step in ("step3", "step4", "step5"):
        csv_path = f"history_{workflow}_{step}.csv"
        if not os.path.isfile(csv_path):
            continue

        versions, uncom, compr = read_history(csv_path)
        if not versions:
            continue

        for job in ("A", "B"):
            v, u, c = slice_for_job(job, version_window, versions, uncom, compr)
            if not v:
                continue
            render(version_short, workflow, step, job, v, u, c)


if __name__ == "__main__":
    main()
