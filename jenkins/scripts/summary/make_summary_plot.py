"""Build per-step Plotly summary (table + time-series + histograms) covering
every release in the same X-version family.

Output filename: <version>_<step>_<workflow>.html — inline shell xrdcopies
`*.html` from cwd to summary_plot_html/.
"""

from __future__ import annotations

import os
import random
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


if __name__ == "__main__":
    main()
