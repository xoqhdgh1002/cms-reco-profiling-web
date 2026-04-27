"""Render index.html for cms-reco-profiling.web.cern.ch.

Reads everything that previous pipeline stages staged under RESULT_PATH and
emits a single static HTML document on stdout. The inline shell redirects
the output to index.html and xrdcopies to <webroot>/web/.

Output preserves the historical structure: per-version <details> sections,
followed by per-workflow nested lists with links to summary plots, RES files,
igprof navigators, comparison previews, circles pie charts, etc.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


# ── Per-step labelling ───────────────────────────────────────────────────────
# step token  -> (workflow-section title token, summary-plot label, eventsize-plot label, recent8 label)
STEP_META = {
    "step2": ("step2_RAW(DIGI)",     "RAW_DIGI",     "RAW_DIGI",     "RAW_DIGI"),
    "step3": ("step3_AOD(RECO)",     "RECO_AOD",     "RECO_AOD",     "RECO_AOD"),
    "step4": ("step4_MiniAOD(PAT)",  "PAT_MiniAOD",  "PAT_MiniAOD",  "PAT_MiniAOD"),
    "step5": ("step5_NanoAOD",       "NanoAOD",      "NanoAOD",      "NanoAOD"),
}
# Short label used in the summary-plot and event-size [bracketed link text].
SHORT_LABEL = {
    "step2": ("DIGI", "RAW"),
    "step3": ("AOD",  "AOD"),
    "step4": ("MINIAOD", "MINIAOD"),
    "step5": ("NANOAOD", "NANOAOD"),
}


def out(s: str = "") -> None:
    print(s)


def release_sort_key(release: str) -> tuple:
    return (release.split("_")[1:4], 10 - len(release.split("_")), len(release))


def family_of(release: str) -> str:
    return "_".join(release.split("_")[:3])


# ── Section emitters ─────────────────────────────────────────────────────────
def emit_summary_plot_links(family: str, plots: list[str]) -> None:
    """The 'Summary of <family>_X(<type>)(<wf>) [Short Summary ...]' block."""
    for plot in plots:
        if family not in plot:
            continue
        for step, (_, plot_label, _, _) in STEP_META.items():
            if step not in plot:
                continue
            wf = ".".join(plot.split("_")[4].split(".")[0:1])
            short = SHORT_LABEL[step][0]
            out('<span style=" font: normal bold 1.0em Georgia, serif ; color: navy;">')
            out(f'\t<h3>Summary of {family}_X({plot_label})({wf}) '
                f'<font size="2em"><a target=\'_blank\' '
                f'href="{_common.RESULT_ADDRESS}summary_plot_html/{plot}" '
                f'title="shortSummary">[Short Summary Time and Memory({short})]</a></font></h3>')
            break


def emit_eventsize_plot_links(family_short: str, plots: list[str]) -> None:
    """family_short: e.g. '14_0' (without 'CMSSW_' prefix)."""
    for plot in plots:
        if family_short not in plot:
            continue
        for step, (_, _, label, _) in STEP_META.items():
            if step not in plot:
                continue
            wf = plot.split("_")[3].split(".")[0]
            short = SHORT_LABEL[step][1]
            out('<span style=" font: normal bold 1.0em Georgia, serif ; color: navy;">')
            out(f'        <h3>EventSize Summary({label})({wf}) '
                f'<font size="2em"><a target=\'_blank\' '
                f'href="{_common.RESULT_ADDRESS}circles/web/hist/{plot}" '
                f'title="shortSummary">[EventSize Summary({short})]</a></font></h3>')
            break


def emit_recent_plot_links(plots: list[str]) -> None:
    for plot in plots:
        if "Recent" not in plot:
            continue
        for step, (_, _, _, label) in STEP_META.items():
            if step not in plot:
                continue
            wf = plot.split("_")[1].split(".")[0]
            short = SHORT_LABEL[step][1]
            out('<span style=" font: normal bold 1.0em Georgia, serif ; color: navy;">')
            out(f'        <h3>Recent8 Summary({label})({wf}) '
                f'<font size="2em"><a target=\'_blank\' '
                f'href="{_common.RESULT_ADDRESS}circles/web/hist/{plot}" '
                f'title="shortSummary">[Recent8 Summary({short})]</a></font></h3>')
            break


def emit_step_links(release: str, gcc: str, workflow: str, step: str, family: str) -> None:
    """All per-step links inside a workflow's <ul> (the deepest level)."""
    addr = _common.RESULT_ADDRESS
    from_data = f"{release}/{gcc}/{workflow}/"
    from_cgi = f"{release}/{workflow}/{step}/"

    out(f'\n\t\t\t<li><strong>{STEP_META[step][0]}</strong>')
    out('\n\t\t\t\t<ul>')
    out(f'\n\t\t\t\t<li>\n\t\t\t\t<a href="{addr}Time_Mem_Summary/{from_data}{step}.txt" '
        f'title="getTimeMemSummary">[getTimeMemSummary]</a>')
    out(f'\n\t\t\t\t<a href="{addr}Time_Mem_Summary/{from_data}memory_report_{step}.txt" '
        f'title="memory_report">[memory_report]</a>')

    # IgProf navigator + .res txt links.
    cgi_dir = f"/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/{from_cgi}"
    if os.path.isdir(cgi_dir):
        res_dir = _common.result_subdir("RES", release, gcc, workflow)
        if os.path.isdir(res_dir):
            for res in (r for r in os.listdir(res_dir) if step in r):
                if "cpu" in res:
                    cgi_bin, ig_number = "cpu_endjob", ""
                else:
                    snap = res.split("_")[2].split(".")[0]
                    cgi_bin, ig_number = f"mem_live.{snap}", snap
                profiler = res.split("_")[1].split(".")[0]
                out(f'\n\t\t\t<a href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/'
                    f'cgi-bin/igprof-navigator/releases/{from_cgi}{cgi_bin}" '
                    f'title="{profiler} time check">[{profiler} Profiler igprof{ig_number}]</a>'
                    f'<a href="{addr}RES/{from_data}{res}" title="txtLink">[txtLink]</a>')

    # Comparison block (TimeDiff + CompProd preview spans).
    timediff_path = _common.result_subdir("TimeDiff", release, gcc, workflow, f"{step}.txt")
    compprod_path = _common.result_subdir("CompProd", release, gcc, workflow, f"{step}.txt")
    has_timediff = os.path.isfile(timediff_path)
    has_compprod = os.path.isfile(compprod_path)

    if has_timediff or has_compprod:
        out('\n\t\t\t<li>Comparison :\n\t\t\t<ul>')

    if has_timediff:
        with open(timediff_path) as f:
            last = f.readlines()[-1]
        toks = last.split()
        out(f'\n\t\t\t\t<li>\n\t\t\t\t<a href="{addr}TimeDiff/{from_data}{step}.txt" '
            f'title="TimeDiff">[TimeDiff]</a>'
            f'<span style=" font: Arial; font-size: small; color: green;"> '
            f'preview: {toks[2]} s/ev ==> {toks[5]} s/ev </span>\n\t\t\t\t</li>')

    if has_compprod:
        with open(compprod_path) as f:
            last = f.readlines()[-1]
        toks = last.split()
        out(f'\n\t\t\t\t<li>\n\t\t\t\t<a href="{addr}/CompProd/{from_data}{step}.txt" '
            f'title="Compare_Out_Prod">[CompareOutProd (edmEventSize)]</a>'
            f'<span style=" font: Arial; font-size: small; color: red;"> '
            f'preview: {toks[1]} ==> {toks[2]} </span>\n\t\t\t\t</li>')

    if has_timediff or has_compprod:
        out('\n\t\t\t</ul>')

    # IgProf comparison HTMLs (currently unpopulated — those steps are
    # commented out in the inline shell, but the rendering survives in case
    # the directory is filled out-of-band).
    igprof_dir = _common.result_subdir("comp_igprof", "html", from_cgi)
    if os.path.isdir(igprof_dir):
        pages = os.listdir(igprof_dir)
        if pages:
            out('\n\t\t\t<li>Igprof comparison :\n\t\t\t<ul>')
            for page in pages:
                if "cpu" in page:
                    label = "cpu"
                else:
                    label = "mem." + page.split("_")[1].split(".")[1]
                title = page.split("_")[0]
                out(f'\n\t\t\t<li>\n\t\t\t<a href="{addr}comp_igprof/html/{from_cgi}{page}" '
                    f'title="{title} compare">[{label} compare]</a>\n\t\t\t</li>')
            out('\n\t\t\t</ul>')

    # Circle pie chart + EventSize circle (skipped for the deprecated CMSSW_11_0
    # branch and for workflow 136.889).
    if family != "CMSSW_11_0" and workflow != "136.889":
        circle_dataset = f"{release}%2F{gcc}%2F{workflow}%2F{step}_circles"
        out('\n\t\t\t<li>Circle (Pie chart) :\n\t\t\t'
            f'<a href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/'
            f'circles/piechart.php?local=false&dataset={circle_dataset}'
            f'&resource=time_real&colours=default&groups=reco_PhaseII_private&threshold=0" '
            f'title="Circle">[Circle]</a>\n\t\t\t</li>')

        eventsize_json = _common.result_subdir(
            "circles", "web", "data",
            f"{release}_{workflow}_{step}_eventSize.json")
        if os.path.isfile(eventsize_json):
            out('\n\t\t\t<li>EventSizeCircle (pie chart) :\n\t\t\t'
                f'<a href="https://cms-reco-profiling.web.cern.ch/cms-reco-profiling/'
                f'results/circles/web/eventsize.php?local=false&'
                f'dataset={release}_{workflow}_{step}_eventSize&'
                f'resource=size_uncom&colours=default&groups=Group_{step}_23Sep_v1'
                f'&threshold=0" title="EventSize">[EventSize]</a>\n\t\t\t</li>')

    out("\t\t</ul>")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: make_webpage.py <RECENT_RELEASE>")
    recent_rel = sys.argv[1]
    recent_family = family_of(recent_rel)

    cmdlog_path = _common.result_subdir("cmdlog")
    cmssw_list = sorted(os.listdir(cmdlog_path), key=release_sort_key)

    out("""<!DOCTYPE html>
<html>
<head>
</head>
<body>""")

    # Cache directory listings used inside the per-version block.
    summary_html_dir = os.listdir(_common.result_subdir("summary_plot_html"))
    hist_dir = os.listdir(_common.result_subdir("circles", "web", "hist"))
    eventsize_plots = [p for p in hist_dir if "Eventsize" in p]
    recent_plots = [p for p in hist_dir if "Recent" in p]

    mother_family = ""
    for cmssw in cmssw_list:
        family = family_of(cmssw)

        # On version-family boundary: close the previous <details>, open a new one.
        if family != mother_family:
            if mother_family:
                out("</details>")
                out('<hr size="3" noshade>')
            mother_family = family
            out(f"<details>\n\t<summary>{mother_family}_X</summary>")
            out(f'\t<h2>{mother_family}_X <font size="4em"></font></h2>')

            emit_summary_plot_links(mother_family, summary_html_dir)
            out('<hr size="2" noshade>\n<br>')

            family_short = "_".join(mother_family.split("_")[1:])
            emit_eventsize_plot_links(family_short, eventsize_plots)
            out('<hr size="2" noshade>\n<br>')

            if mother_family == recent_family:
                emit_recent_plot_links(recent_plots)
                out('<hr size="2" noshade>\n<br>')

        gcc = os.listdir(os.path.join(cmdlog_path, cmssw))[0]

        for workflow in os.listdir(os.path.join(cmdlog_path, cmssw, gcc)):
            tms_dir = _common.result_subdir("Time_Mem_Summary", cmssw, gcc, workflow)
            if not os.path.isdir(tms_dir):
                continue
            tms_files = os.listdir(tms_dir)
            if not tms_files:
                continue

            out(f"\n\t\t<li><strong>{cmssw}({workflow})</strong>\n\t\t<br>\n\t\t<ul>")

            cmdlog_dir = _common.result_subdir("cmdlog", cmssw, gcc, workflow)
            if "cmdLog_profiling.txt" in os.listdir(cmdlog_dir):
                out(f'\n\t\t\t<li>\n\t\t\t<a href="{_common.RESULT_ADDRESS}cmdlog/'
                    f'{cmssw}/{gcc}/{workflow}/cmdLog_profiling.txt" title="cmdLog">[cmdLog]</a>')

            steps_seen = [s.split(".")[0] for s in tms_files if s.split(".")[0] in STEP_META]
            for step in steps_seen:
                emit_step_links(cmssw, gcc, workflow, step, family)

            out("\t</ul>")

    out("</details>\n</body>\n</html>")


if __name__ == "__main__":
    main()
