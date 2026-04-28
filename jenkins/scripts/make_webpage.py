"""Generate index.html for cms-reco-profiling.web.cern.ch.

Strategy: instead of pre-rendering every link server-side, this script walks
the EOS results tree once, builds a JSON manifest of available data, and
emits an HTML page that embeds the manifest and renders it client-side.

A broken results .txt no longer kills the entire page. Each release ×
workflow × step cell is built inside its own try/except, so the worst case
is "this one cell has no preview" rather than "all 50 releases blank because
one TimeDiff trailer was truncated".

The inline shell still calls `python3 make_webpage.py <RELEASE> > index.html`
exactly as before; only the *contents* of index.html change.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


# Step → human-readable labels used in the rendered page.
# `long`  : section heading inside a workflow's <ul>
# `short` : bracketed link label, e.g. "[Short Summary Time and Memory(AOD)]"
# `plot`  : descriptive token used in the family-level summary plot heading
STEP_META = {
    "step2": {"long": "step2_RAW(DIGI)",    "short": "DIGI",    "plot": "RAW_DIGI"},
    "step3": {"long": "step3_AOD(RECO)",    "short": "AOD",     "plot": "RECO_AOD"},
    "step4": {"long": "step4_MiniAOD(PAT)", "short": "MINIAOD", "plot": "PAT_MiniAOD"},
    "step5": {"long": "step5_NanoAOD",      "short": "NANOAOD", "plot": "NanoAOD"},
}


# ── Filesystem helpers (each returns "" / [] / None on missing/unreadable) ───
def safe_listdir(path: str) -> list[str]:
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []


def safe_last_tokens(path: str, min_count: int) -> list[str] | None:
    """Read last line of `path`, split on whitespace; return tokens iff >= min_count."""
    try:
        with open(path) as f:
            lines = f.readlines()
    except OSError:
        return None
    if not lines:
        return None
    toks = lines[-1].split()
    return toks if len(toks) >= min_count else None


# ── Sorting & family helpers ────────────────────────────────────────────────
def release_sort_key(release: str) -> tuple:
    return (release.split("_")[1:4], 10 - len(release.split("_")), len(release))


def family_of(release: str) -> str:
    return "_".join(release.split("_")[:3])


# ── Manifest builders ───────────────────────────────────────────────────────
def build_step_cell(release: str, gcc: str, workflow: str, step: str) -> dict:
    """Per-step manifest cell. Each side-effect is isolated."""
    cell: dict[str, Any] = {}

    # IgProf navigator + .res files (the cgi-bin dir is populated by main.py --igprof)
    cgi_dir = (f"/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/"
               f"{release}/{workflow}/{step}")
    if os.path.isdir(cgi_dir):
        cell["has_igprof_navigator"] = True
        igprof = []
        for res in safe_listdir(_common.result_subdir("RES", release, gcc, workflow)):
            if step not in res:
                continue
            if "cpu" in res:
                igprof.append({
                    "profiler": "cpu", "ig_number": "",
                    "cgi_bin": "cpu_endjob", "res": res,
                })
            elif "mem" in res:
                try:
                    snap = res.split("_")[2].split(".")[0]
                except IndexError:
                    continue
                igprof.append({
                    "profiler": "mem", "ig_number": snap,
                    "cgi_bin": f"mem_live.{snap}", "res": res,
                })
        cell["igprof"] = igprof

    # TimeDiff trailer preview ("Job total: X s/ev ==> Y s/ev") — toks[2], toks[5]
    tp = _common.result_subdir("TimeDiff", release, gcc, workflow, f"{step}.txt")
    if os.path.isfile(tp):
        cell["has_timediff"] = True
        toks = safe_last_tokens(tp, 6)
        if toks:
            cell["timediff_preview"] = {"old": toks[2], "new": toks[5]}

    # CompProd trailer preview ("oldSize newSize ...") — toks[1], toks[2]
    cp = _common.result_subdir("CompProd", release, gcc, workflow, f"{step}.txt")
    if os.path.isfile(cp):
        cell["has_compprod"] = True
        toks = safe_last_tokens(cp, 3)
        if toks:
            cell["compprod_preview"] = {"old": toks[1], "new": toks[2]}

    # IgProf comparison HTMLs (currently usually empty — those steps are
    # commented out in the inline shell, but render survives if dir is filled)
    pages = safe_listdir(_common.result_subdir("comp_igprof", "html", release, workflow, step))
    if pages:
        cig = []
        for p in pages:
            if "cpu" in p:
                label = "cpu"
            else:
                parts = p.split("_")
                snap = parts[1].split(".")[1] if len(parts) >= 2 and "." in parts[1] else "?"
                label = f"mem.{snap}"
            cig.append({"file": p, "label": label})
        cell["compigprof"] = cig

    # EventSize circle availability
    json_path = _common.result_subdir(
        "circles", "web", "data",
        f"{release}_{workflow}_{step}_eventSize.json",
    )
    if os.path.isfile(json_path):
        cell["has_eventsize_circle"] = True

    return cell


def build_workflow(release: str, gcc: str, workflow: str) -> dict:
    wf: dict[str, Any] = {}
    cmdlog_files = safe_listdir(_common.result_subdir("cmdlog", release, gcc, workflow))
    wf["has_cmdlog"] = "cmdLog_profiling.txt" in cmdlog_files

    tms_files = safe_listdir(_common.result_subdir("Time_Mem_Summary", release, gcc, workflow))
    steps_seen = sorted({s.split(".")[0] for s in tms_files if s.split(".")[0] in STEP_META})

    wf["steps"] = {}
    for step in steps_seen:
        try:
            wf["steps"][step] = build_step_cell(release, gcc, workflow, step)
        except Exception as e:
            wf["steps"][step] = {"error": str(e)}
    return wf


def build_release(release: str) -> dict:
    cmdlog_path = _common.result_subdir("cmdlog", release)
    archs = safe_listdir(cmdlog_path)
    rel: dict[str, Any] = {
        "family": family_of(release),
        "family_short": "_".join(release.split("_")[1:3]),
        "gcc": archs[0] if archs else None,
        "workflows": {},
    }
    if not rel["gcc"]:
        return rel
    for workflow in safe_listdir(os.path.join(cmdlog_path, rel["gcc"])):
        try:
            rel["workflows"][workflow] = build_workflow(release, rel["gcc"], workflow)
        except Exception as e:
            rel["workflows"][workflow] = {"error": str(e), "steps": {}}
    return rel


def group_summary_plots(plots: list[str], releases: dict) -> dict[str, list[str]]:
    """Family-name → matching summary_plot_html filenames."""
    families = sorted({r["family"] for r in releases.values() if r.get("family")})
    out: dict[str, list[str]] = {f: [] for f in families}
    for plot in plots:
        for fam in families:
            if fam in plot:
                out[fam].append(plot)
                break
    return out


def group_eventsize_plots(plots: list[str], releases: dict) -> dict[str, list[str]]:
    """family_short ('16_0') → eventsize plot filenames."""
    shorts = sorted({r["family_short"] for r in releases.values() if r.get("family_short")})
    out: dict[str, list[str]] = {s: [] for s in shorts}
    for plot in plots:
        for s in shorts:
            if s in plot:
                out[s].append(plot)
                break
    return out


def build_manifest(recent_release: str) -> dict:
    cmdlog_path = _common.result_subdir("cmdlog")
    cmssw_list = sorted(safe_listdir(cmdlog_path), key=release_sort_key)

    releases: dict[str, dict] = {}
    for cmssw in cmssw_list:
        try:
            releases[cmssw] = build_release(cmssw)
        except Exception as e:
            releases[cmssw] = {
                "error": str(e), "workflows": {},
                "family": family_of(cmssw), "family_short": "_".join(cmssw.split("_")[1:3]),
                "gcc": None,
            }

    summary_html = safe_listdir(_common.result_subdir("summary_plot_html"))
    hist = safe_listdir(_common.result_subdir("circles", "web", "hist"))

    return {
        "recent_release": recent_release,
        "recent_family": family_of(recent_release),
        "result_address": _common.RESULT_ADDRESS,
        "step_meta": STEP_META,
        "summary_plots_by_family": group_summary_plots(summary_html, releases),
        "eventsize_plots_by_family_short": group_eventsize_plots(
            [p for p in hist if "Eventsize" in p], releases),
        "recent_plots": [p for p in hist if "Recent" in p],
        "releases": releases,
    }


# ── HTML shell + client renderer ─────────────────────────────────────────────
HTML_HEAD = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CMS Reco Profiling</title>
<style>
  body { font-family: sans-serif; margin: 1em; line-height: 1.4; }
  details > summary { font-size: 1.4em; font-weight: bold; cursor: pointer; padding: 0.2em 0; }
  h2 { font-size: 1.3em; margin-top: 0.5em; }
  h3 { font: normal bold 1.0em Georgia, serif; color: navy; margin: 0.3em 0; }
  .preview-time { font-size: small; color: green; }
  .preview-size { font-size: small; color: red; }
  ul { padding-left: 1.5em; }
  hr { margin: 0.8em 0; }
  a { text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div id="root"></div>
"""

HTML_TAIL = """</body>
</html>
"""

# Plain ES5 — no module loader, no external deps. Indentation isn't
# semantically significant; raw string keeps backslashes intact.
CLIENT_RENDER_JS = r"""
const ADDR = MANIFEST.result_address;
const STEP_META = MANIFEST.step_meta;
const STEPS = ['step2', 'step3', 'step4', 'step5'];

function el(tag, props) {
  const e = document.createElement(tag);
  if (props && props.html != null) e.innerHTML = props.html;
  else if (props && props.text != null) e.textContent = props.text;
  for (let i = 2; i < arguments.length; i++) {
    const c = arguments[i];
    if (c != null) e.appendChild(c);
  }
  return e;
}

function detectStep(name) {
  for (let i = 0; i < STEPS.length; i++) if (name.indexOf(STEPS[i]) >= 0) return STEPS[i];
  return null;
}

function emitFamilyHeader(details, family, familyShort) {
  details.appendChild(el('h2', { html: family + '_X' }));

  const sumPlots = MANIFEST.summary_plots_by_family[family] || [];
  for (const p of sumPlots) {
    const step = detectStep(p);
    if (!step) continue;
    const meta = STEP_META[step];
    const wfPart = (p.split('_')[4] || '').split('.')[0];
    details.appendChild(el('h3', { html:
      'Summary of ' + family + '_X(' + meta.plot + ')(' + wfPart + ') ' +
      '<a target="_blank" href="' + ADDR + 'summary_plot_html/' + p +
      '">[Short Summary Time and Memory(' + meta.short + ')]</a>'
    }));
  }
  details.appendChild(el('hr'));

  const evPlots = MANIFEST.eventsize_plots_by_family_short[familyShort] || [];
  for (const p of evPlots) {
    const step = detectStep(p);
    if (!step) continue;
    const meta = STEP_META[step];
    const parts = p.split('_');
    const wfPart = (parts[3] || '').split('.')[0];
    details.appendChild(el('h3', { html:
      'EventSize Summary(' + meta.plot + ')(' + wfPart + ') ' +
      '<a target="_blank" href="' + ADDR + 'circles/web/hist/' + p +
      '">[EventSize Summary(' + meta.short + ')]</a>'
    }));
  }
  details.appendChild(el('hr'));

  if (family === MANIFEST.recent_family) {
    for (const p of MANIFEST.recent_plots) {
      const step = detectStep(p);
      if (!step) continue;
      const meta = STEP_META[step];
      const wfPart = (p.split('_')[1] || '').split('.')[0];
      details.appendChild(el('h3', { html:
        'Recent8 Summary(' + meta.plot + ')(' + wfPart + ') ' +
        '<a target="_blank" href="' + ADDR + 'circles/web/hist/' + p +
        '">[Recent8 Summary(' + meta.short + ')]</a>'
      }));
    }
    details.appendChild(el('hr'));
  }
}

function emitStep(parentUl, release, gcc, workflow, step, cell) {
  const meta = STEP_META[step];
  const fromData = release + '/' + gcc + '/' + workflow + '/';
  const fromCgi  = release + '/' + workflow + '/' + step + '/';

  const stepLi = el('li', { html: '<strong>' + meta.long + '</strong>' });
  const sub = el('ul');

  sub.appendChild(el('li', { html:
    '<a href="' + ADDR + 'Time_Mem_Summary/' + fromData + step + '.txt">[getTimeMemSummary]</a> ' +
    '<a href="' + ADDR + 'Time_Mem_Summary/' + fromData + 'memory_report_' + step + '.txt">[memory_report]</a>'
  }));

  if (cell.has_igprof_navigator && cell.igprof) {
    for (const ig of cell.igprof) {
      sub.appendChild(el('li', { html:
        '<a href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/cgi-bin/igprof-navigator/releases/' +
          fromCgi + ig.cgi_bin + '">[' + ig.profiler + ' Profiler igprof' + ig.ig_number + ']</a>' +
        '<a href="' + ADDR + 'RES/' + fromData + ig.res + '">[txtLink]</a>'
      }));
    }
  }

  if (cell.has_timediff || cell.has_compprod) {
    const compLi = el('li', { html: 'Comparison :' });
    const compUl = el('ul');
    if (cell.has_timediff) {
      const prev = cell.timediff_preview;
      const span = prev
        ? ' <span class="preview-time">preview: ' + prev.old + ' s/ev ==> ' + prev.new + ' s/ev</span>'
        : '';
      compUl.appendChild(el('li', { html:
        '<a href="' + ADDR + 'TimeDiff/' + fromData + step + '.txt">[TimeDiff]</a>' + span
      }));
    }
    if (cell.has_compprod) {
      const prev = cell.compprod_preview;
      const span = prev
        ? ' <span class="preview-size">preview: ' + prev.old + ' ==> ' + prev.new + '</span>'
        : '';
      compUl.appendChild(el('li', { html:
        '<a href="' + ADDR + '/CompProd/' + fromData + step + '.txt">[CompareOutProd (edmEventSize)]</a>' + span
      }));
    }
    compLi.appendChild(compUl);
    sub.appendChild(compLi);
  }

  if (cell.compigprof && cell.compigprof.length) {
    const cigLi = el('li', { html: 'Igprof comparison :' });
    const cigUl = el('ul');
    for (const c of cell.compigprof) {
      cigUl.appendChild(el('li', { html:
        '<a href="' + ADDR + 'comp_igprof/html/' + fromCgi + c.file + '">[' + c.label + ' compare]</a>'
      }));
    }
    cigLi.appendChild(cigUl);
    sub.appendChild(cigLi);
  }

  // Circle / EventSize circle (suppressed for CMSSW_11_0 family or wf 136.889 — legacy gating)
  const family = MANIFEST.releases[release].family;
  if (family !== "CMSSW_11_0" && workflow !== "136.889") {
    const ds = release + '%2F' + gcc + '%2F' + workflow + '%2F' + step + '_circles';
    sub.appendChild(el('li', { html:
      'Circle (Pie chart) : ' +
      '<a href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/circles/piechart.php?' +
      'local=false&dataset=' + ds +
      '&resource=time_real&colours=default&groups=reco_PhaseII_private&threshold=0">[Circle]</a>'
    }));
    if (cell.has_eventsize_circle) {
      sub.appendChild(el('li', { html:
        'EventSizeCircle (pie chart) : ' +
        '<a href="https://cms-reco-profiling.web.cern.ch/cms-reco-profiling/results/circles/web/eventsize.php?' +
        'local=false&dataset=' + release + '_' + workflow + '_' + step + '_eventSize' +
        '&resource=size_uncom&colours=default&groups=Group_' + step + '_23Sep_v1' +
        '&threshold=0">[EventSize]</a>'
      }));
    }
  }

  stepLi.appendChild(sub);
  parentUl.appendChild(stepLi);
}

function render() {
  const root = document.getElementById('root');

  // Group releases by family, preserving Python's sort.
  const order = Object.keys(MANIFEST.releases);
  const familyOrder = [];
  const familyToReleases = {};
  for (const rel of order) {
    const fam = MANIFEST.releases[rel].family;
    if (!familyToReleases[fam]) {
      familyOrder.push(fam);
      familyToReleases[fam] = [];
    }
    familyToReleases[fam].push(rel);
  }

  for (const family of familyOrder) {
    const fst = MANIFEST.releases[familyToReleases[family][0]].family_short || '';
    const details = el('details');
    details.appendChild(el('summary', { text: family + '_X' }));
    emitFamilyHeader(details, family, fst);

    const wrapper = el('ul');
    for (const rel of familyToReleases[family]) {
      const info = MANIFEST.releases[rel];
      const gcc = info.gcc;
      if (!gcc) continue;
      for (const wf of Object.keys(info.workflows || {})) {
        const wfInfo = info.workflows[wf];
        const stepEntries = Object.keys(wfInfo.steps || {}).map(function (k) { return [k, wfInfo.steps[k]]; });
        if (!stepEntries.length) continue;

        const wfLi = el('li', { html: '<strong>' + rel + '(' + wf + ')</strong><br>' });
        const wfUl = el('ul');
        if (wfInfo.has_cmdlog) {
          wfUl.appendChild(el('li', { html:
            '<a href="' + ADDR + 'cmdlog/' + rel + '/' + gcc + '/' + wf + '/cmdLog_profiling.txt">[cmdLog]</a>'
          }));
        }
        for (const pair of stepEntries) {
          const step = pair[0];
          const cell = pair[1];
          if (cell && !cell.error) emitStep(wfUl, rel, gcc, wf, step, cell);
        }
        wfLi.appendChild(wfUl);
        wrapper.appendChild(wfLi);
      }
    }
    details.appendChild(wrapper);
    root.appendChild(details);
    root.appendChild(el('hr'));
  }
}

render();
"""


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: make_webpage.py <RECENT_RELEASE>")
    recent = sys.argv[1]
    manifest = build_manifest(recent)

    sys.stdout.write(HTML_HEAD)
    sys.stdout.write("<script>\n")
    sys.stdout.write("const MANIFEST = ")
    json.dump(manifest, sys.stdout)
    sys.stdout.write(";\n")
    sys.stdout.write(CLIENT_RENDER_JS)
    sys.stdout.write("\n</script>\n")
    sys.stdout.write(HTML_TAIL)


if __name__ == "__main__":
    main()
