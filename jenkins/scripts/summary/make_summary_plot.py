"""Build per-step Plotly summary (table + time-series + histograms) covering
every release in the same X-version family. Also build a family-level
MaxMemoryPreload (AllocMonitor) bar chart per Javier's 2025-11-26 request.

Output filenames (all land in summary_plot_html/ via the inline shell glob):
- <version>_<step>_<workflow>.html  → existing per-step plot
- <version>_maxmem.html             → new family-level peak-memory plot
"""

from __future__ import annotations

import os
import random
import re
import sys

import numpy as np
import plotly.graph_objects as go
import plotly.io as io
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _common
import Log_check


SUBPLOT_TITLES = [
    "Summary Table",
    "(RSS)Memory Profile", "(VSIZE)Memory Profile", "average CPU Time Profile",
    "(RSS)Memory Profile", "(VSIZE)Memory Profile", "CPU Time Profile",
]


def family_releases(version_prefix: str, base: str) -> list[str]:
    """Releases in the same version family (e.g. all 'CMSSW_14_0' tags)."""
    return [r for r in os.listdir(base) if version_prefix in r]


def _release_sort_key(release: str) -> tuple:
    """Sort key matching the rest of the pipeline (pre0..pre6 < base < patch1..)."""
    parts = release.split("_")
    try:
        major = int(parts[1]); minor = int(parts[2]); patch = int(parts[3])
    except (IndexError, ValueError):
        major = minor = patch = -1
    suffix = parts[4] if len(parts) >= 5 else ""
    if suffix.startswith("pre"):
        try: sub = -1000 + int(suffix[3:])
        except ValueError: sub = -500
    elif suffix.startswith("patch"):
        try: sub = int(suffix[5:])
        except ValueError: sub = 500
    elif suffix == "":
        sub = 0
    else:
        sub = 750
    return (major, minor, patch, sub, release)


_MAX_MEM_RE = re.compile(r"max memory used:\s*(-?\d+)")


def _read_max_memory_bytes(path: str) -> int | None:
    """Last 'max memory used: <bytes>' value in the file, or None."""
    try:
        with open(path) as f:
            text = f.read()
    except OSError:
        return None
    matches = _MAX_MEM_RE.findall(text)
    if not matches:
        return None
    try:
        return int(matches[-1])
    except ValueError:
        return None


# Per-step style for the trend lines. Different markers so the three traces
# remain distinguishable in B/W or for readers who don't see hue. Javier
# (2025-12-XX) asked for line+marker traces grouped per workflow so a
# gradual rise vs. sudden jump in peak memory is visible at a glance.
_STEP_STYLE = {
    "step2": {"colour": "#94a3b8", "symbol": "diamond",       "label": "step2"},
    "step3": {"colour": "#2563eb", "symbol": "circle",        "label": "step3 (RECO/AOD)"},
    "step4": {"colour": "#16a34a", "symbol": "square",        "label": "step4 (PAT/MiniAOD)"},
    "step5": {"colour": "#f97316", "symbol": "triangle-up",   "label": "step5 (NanoAOD)"},
}


def write_family_maxmem_plot(version_prefix: str, profile_data: str) -> None:
    """Family-level line+marker Plotly chart of MaxMemoryPreload values.

    For every release in the family × workflow it has × step it analyses,
    pull the trailing 'max memory used:' from
    RESULT_PATH/Time_Mem_Summary/<rel>/<arch>/<wf>/memory_report_step{N}.txt
    (already populated by found_report.py + the inline-shell xrdcopy).

    Renders one subplot per workflow, x=release ordered by version,
    y=peak memory in GB. Each step is a separate trace with its own marker
    symbol so a sudden jump or gradual rise across releases is obvious.
    Output: <version_prefix>_maxmem.html in cwd; the inline-shell xrdcopy
    of `*.html` puts it in summary_plot_html/.
    """
    rows = []
    for cmssw in family_releases(version_prefix, profile_data):
        cmssw_path = os.path.join(profile_data, cmssw)
        if not os.path.isdir(cmssw_path):
            continue
        archs = os.listdir(cmssw_path)
        if not archs:
            continue
        arch = archs[0]
        arch_path = os.path.join(cmssw_path, arch)
        if not os.path.isdir(arch_path):
            continue
        for workflow in os.listdir(arch_path):
            for step in _common.steps_for(workflow):
                mem_path = _common.result_subdir(
                    "Time_Mem_Summary", cmssw, arch, workflow,
                    f"memory_report_{step}.txt")
                if not os.path.isfile(mem_path):
                    continue
                value = _read_max_memory_bytes(mem_path)
                if value is None:
                    continue
                rows.append({
                    "release": cmssw, "workflow": workflow, "step": step,
                    "max_used_gb": value / 1e9,
                    "key": _release_sort_key(cmssw),
                })
    if not rows:
        return

    # Group rows by workflow, sort releases within each workflow by version.
    workflows = sorted({r["workflow"] for r in rows})
    fig = make_subplots(
        rows=len(workflows), cols=1,
        subplot_titles=[f"Workflow {wf}" for wf in workflows],
        vertical_spacing=0.10,
    )

    # Track which steps have been added to the legend so the same step in
    # different subplots reuses one legend entry.
    legend_seen: set[str] = set()

    for i, wf in enumerate(workflows, 1):
        wf_rows = [r for r in rows if r["workflow"] == wf]
        # All releases that appeared in any step of this workflow,
        # ordered by version. None gaps mean "this step wasn't analysed
        # for that release"; connectgaps keeps the line continuous.
        rels = sorted({r["release"] for r in wf_rows}, key=_release_sort_key)
        for step in ("step2", "step3", "step4", "step5"):
            ys = []
            present = False
            for rel in rels:
                hit = next((r for r in wf_rows
                            if r["release"] == rel and r["step"] == step), None)
                if hit:
                    present = True
                    ys.append(hit["max_used_gb"])
                else:
                    ys.append(None)
            if not present:
                continue
            style = _STEP_STYLE[step]
            show_legend = step not in legend_seen
            legend_seen.add(step)
            fig.add_trace(go.Scatter(
                x=rels, y=ys,
                mode="lines+markers",
                name=style["label"],
                legendgroup=step,
                showlegend=show_legend,
                line=dict(color=style["colour"], width=2),
                marker=dict(symbol=style["symbol"], size=10,
                            color=style["colour"],
                            line=dict(color="white", width=1)),
                connectgaps=True,
                hovertemplate=("<b>%{x}</b><br>" + style["label"] +
                               ": %{y:.3f} GB<extra></extra>"),
            ), row=i, col=1)

    # Layout: title on top, legend in a single row directly below the title
    # but still above all subplots. The extra top margin keeps the legend
    # from overlapping the first workflow's plot area.
    fig.update_layout(
        title=dict(
            text=f"Max Memory (AllocMonitor) trend — {version_prefix}_X",
            x=0.5, xanchor="center", font=dict(size=18),
        ),
        height=340 * len(workflows) + 160,
        width=1400,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.04,
            xanchor="center", x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
        ),
        margin=dict(l=70, r=30, t=140, b=40),
        hovermode="x unified",
    )
    for i in range(1, len(workflows) + 1):
        fig.update_yaxes(title_text="Peak memory (GB)", row=i, col=1, rangemode="tozero")
        fig.update_xaxes(tickangle=-45, row=i, col=1)

    out = f"{version_prefix}_maxmem.html"
    io.write_html(fig, out)


def main() -> None:
    args = _common.make_parser(
        "Per-version summary plot builder",
        need=("release", "workflow"),
    ).parse_args()
    release, workflow = args.release, args.workflow
    base = args.profile_data

    log_parser = Log_check.TimeMem()
    version_prefix = "_".join(release.split("_")[:3])  # e.g. CMSSW_14_0

    for step in _common.steps_for(workflow):
        fig = make_subplots(
            rows=3, cols=3,
            row_heights=[0.2, 0.4, 0.4],
            subplot_titles=SUBPLOT_TITLES,
            start_cell="top-left",
            vertical_spacing=0.1,
            specs=[
                [{"colspan": 3, "type": "table"}, None, None],
                [{}, {}, {}],
                [{}, {}, {}],
            ],
        )

        cmssw_versions: list[str] = []
        max_rss: list[str] = []
        max_vsize: list[str] = []
        max_time: list[str] = []
        avg_time: list[str] = []

        for cmssw in family_releases(version_prefix, base):
            arch = os.listdir(os.path.join(base, cmssw))[0]
            tmi = _common.step_file(cmssw, arch, workflow, step, "_TimeMemoryInfo.log", base=base)
            if not os.path.isfile(tmi):
                continue

            df = log_parser.Get_TimeMem(tmi)
            if len(df["event"]) == 0:
                continue

            color = "#" + format(random.randint(0, 0xFFFFFF), "06x")
            x_axis = np.arange(len(df))

            common_line = dict(mode="lines", line=dict(color=color, width=1),
                               legendgroup=cmssw, hovertext=cmssw, name=cmssw)
            fig.add_trace(go.Scatter(x=x_axis, y=df["rss"], **common_line), row=2, col=1)
            fig.add_trace(go.Scatter(x=x_axis, y=df["vsize"], showlegend=False, **common_line), row=2, col=2)
            fig.add_trace(go.Scatter(x=x_axis, y=df["time"], showlegend=False, **common_line), row=2, col=3)

            common_hist = dict(marker_color=color, opacity=0.50,
                               legendgroup=cmssw, hovertext=cmssw, name=cmssw, showlegend=False)
            fig.add_trace(go.Histogram(x=df["rss"], nbinsx=20, bingroup=1, **common_hist), row=3, col=1)
            fig.add_trace(go.Histogram(x=df["vsize"], nbinsx=20, bingroup=2, **common_hist), row=3, col=2)
            fig.add_trace(go.Histogram(x=df["time"], nbinsx=20, bingroup=3, **common_hist), row=3, col=3)

            max_rss.append(f"{df['rss'].max()}({df['event'][df['rss'].idxmax()]})")
            max_vsize.append(f"{df['vsize'].max()}({df['event'][df['vsize'].idxmax()]})")
            max_time.append(f"{df['time'].max()}({df['event'][df['time'].idxmax()]})")
            avg_time.append(str(round(df["time"].sum() / len(df["time"]), 4)))
            cmssw_versions.append(cmssw)

        if not cmssw_versions:
            continue

        fig.add_trace(
            go.Table(
                header=dict(values=["VERSION", "(RSS)MaxMemory(evt)", "(VSIZE)MaxMemory(evt)",
                                    "AverageTime", "MaxTime(evt)"]),
                cells=dict(height=30, values=[cmssw_versions, max_rss, max_vsize, avg_time, max_time]),
            ),
            row=1, col=1,
        )

        fig.update_layout(
            barmode="overlay",
            height=1500, width=1500,
            title=dict(
                text=f"Summary of Time and Memory test : {version_prefix}_X_{step}",
                x=0.5, y=0.98, xanchor="center", yanchor="top", font=dict(size=20),
            ),
            legend=dict(orientation="h", yanchor="bottom", y=0.78, xanchor="right", x=1),
        )

        for col in (1, 2, 3):
            fig.update_xaxes(title_text="ith event", row=2, col=col)
        fig.update_xaxes(title_text="Memory(MB)", row=3, col=1)
        fig.update_xaxes(title_text="Memory(MB)", row=3, col=2)
        fig.update_xaxes(title_text="Time(s)", row=3, col=3)
        fig.update_yaxes(title_text="Memory(MB)", row=2, col=1)
        fig.update_yaxes(title_text="Memory(MB)", row=2, col=2)
        fig.update_yaxes(title_text="Time(s)", type="log", row=2, col=3)
        for col in (1, 2, 3):
            fig.update_yaxes(title_text="Number of events", row=3, col=col)

        out = f"{version_prefix}_{step}_{workflow}.html"
        io.write_html(fig, out)

    # Family-level MaxMemoryPreload chart. Idempotent — every (release, wf)
    # invocation rewrites the same <family>_maxmem.html with the latest data.
    write_family_maxmem_plot(version_prefix, base)


if __name__ == "__main__":
    main()
