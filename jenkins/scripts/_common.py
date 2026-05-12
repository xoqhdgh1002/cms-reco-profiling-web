"""Shared helpers for the release-analyze-reco-profiling scripts.

The Jenkins inline shell calls each script with `--release`, `--architecture`,
`--workflow` and reads outputs from the script's working directory before
xrdcopy'ing them to EOS. This module centralizes:

- The hardcoded EOS paths the scripts read/write
- The argparse surface every script duplicates
- The "skip this workflow at step X" gating that lives in the inline shell
  AND in several scripts
- Path-builder helpers so call sites don't keep concatenating strings

Anything user-visible (CLI flags, output filenames, exit semantics) is held
fixed — refactoring here must not change the contract observed by Jenkins.
"""

from __future__ import annotations

import argparse
import os
from typing import Iterable

# ── Filesystem layout ────────────────────────────────────────────────────────
# Source of profiling data, populated by `release-run-reco-profiling`.
DATA_DIR = "/eos/cms/store/user/cmsbuild/profiling/data"

# Web-publishing area, written via xrdcopy by the Jenkins inline shell.
RESULT_PATH = "/eos/project/c/cmsweb/www/reco-prof/results"

# Public URL prefix for everything under RESULT_PATH (used by make_webpage.py).
RESULT_ADDRESS = "http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/results/"

# ── Workflow gating ──────────────────────────────────────────────────────────
# These match the `if [ "$WORKFLOW" != ... ]` guards in the Jenkins inline shell.
# Keep them in sync with config.xml when the shell is eventually refreshed.
_NO_SUMMARY_WORKFLOWS = {"136.889", "140.047"}
_EXTENDED_STEP_WORKFLOWS = {"140.56", "159.03"}
_NO_EVENTSIZE_WORKFLOWS = _NO_SUMMARY_WORKFLOWS | _EXTENDED_STEP_WORKFLOWS


def steps_for(workflow: str) -> list[str]:
    """Steps to analyze for a given workflow.

    140.56 / 159.03 expose step2 (DIGI) in addition to the common 3/4/5.
    """
    if workflow in _EXTENDED_STEP_WORKFLOWS:
        return ["step2", "step3", "step4", "step5"]
    return ["step3", "step4", "step5"]


def skip_summary(workflow: str) -> bool:
    """True when the inline shell skips Time_Mem_Summary + summary_plot for this workflow."""
    return workflow in _NO_SUMMARY_WORKFLOWS


def skip_eventsize(workflow: str) -> bool:
    """True when the inline shell skips eventsize / igprof / comparison for this workflow."""
    return workflow in _NO_EVENTSIZE_WORKFLOWS


# ── Path helpers ─────────────────────────────────────────────────────────────
def data_dir(release: str, architecture: str, workflow: str, *, base: str = DATA_DIR) -> str:
    """Absolute path to the EOS data directory for a single (release, arch, wf)."""
    return os.path.join(base, release, architecture, workflow)


def step_file(release: str, architecture: str, workflow: str, step: str, suffix: str,
              *, base: str = DATA_DIR) -> str:
    """Path to <DATA>/<release>/<arch>/<wf>/<step><suffix>.

    Examples:
        step_file(r, a, w, 'step3', '.root')                  -> .../step3.root
        step_file(r, a, w, 'step3', '_TimeMemoryInfo.log')    -> .../step3_TimeMemoryInfo.log
    """
    return os.path.join(data_dir(release, architecture, workflow, base=base), f"{step}{suffix}")


def result_subdir(*parts: str) -> str:
    """Absolute path under RESULT_PATH built from path components."""
    return os.path.join(RESULT_PATH, *parts)


# ── argparse surface ─────────────────────────────────────────────────────────
def make_parser(description: str = "", *, need: Iterable[str] = ("release", "architecture", "workflow"),
                extra: Iterable[tuple[str, dict]] = ()) -> argparse.ArgumentParser:
    """Build the standard parser the inline shell expects.

    `need` selects which of release/architecture/workflow to expose; all default
    to None to preserve the historical "optional but expected" behaviour.

    `extra` is a list of (flag, kwargs) pairs for script-specific options.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--profile-data", type=str, default=DATA_DIR,
        help="profiling data location (default: %(default)s)",
    )
    if "release" in need:
        parser.add_argument("--release", type=str, default=None, help="CMSSW release")
    if "architecture" in need:
        parser.add_argument("--architecture", type=str, default=None, help="architecture for release")
    if "workflow" in need:
        parser.add_argument("--workflow", type=str, default=None, help="workflow")
    for flag, kwargs in extra:
        parser.add_argument(flag, **kwargs)
    return parser
