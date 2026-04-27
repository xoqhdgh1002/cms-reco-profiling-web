"""Run igprof-analyse on each step's CPU/MEM .gz and write .res files.

Outputs go directly under RESULT_PATH/RES/<release>/<arch>/<workflow>/ via the
shared NFS/EOS mount (the inline shell does NOT xrdcopy these — see config.xml
section "make_RES.py" — so they must land there in-place).

Output naming preserved verbatim:
    step{N}_cpu.res
    step{N}_mem_<igprof-suffix>.res    (suffix = "1" / "200" / "399" / "")
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

MAKE_RES_SH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_res.sh")


def igprof_suffix(gz_name: str) -> str:
    """Extract the checkpoint suffix from a name like 'step3_igprofMEM.200.gz'."""
    # gz_name = "step{N}_igprofMEM.<suffix>.gz" or "step{N}_igprofMEM.gz"
    parts = gz_name.split(".")
    return parts[1] if len(parts) >= 3 else ""


def main() -> None:
    args = _common.make_parser("igprof-analyse runner").parse_args()
    release, arch, wf = args.release, args.architecture, args.workflow

    src_root = _common.data_dir(release, arch, wf, base=args.profile_data)
    out_root = _common.result_subdir("RES", release, arch, wf)
    os.makedirs(out_root, exist_ok=True)

    for step in ("step3", "step4", "step5"):
        gz_files = [f for f in os.listdir(src_root) if f.endswith(".gz") and step in f]
        if not gz_files:
            continue
        print(release, arch, wf, step)

        for gz in gz_files:
            src = os.path.join(src_root, gz)
            if "CPU" in gz:
                out = os.path.join(out_root, f"{step}_cpu.res")
                if os.path.isfile(out):
                    continue
                os.system(f"source {MAKE_RES_SH} 0 {src} {out}")
            elif "MEM" in gz:
                suffix = igprof_suffix(gz)
                out = os.path.join(out_root, f"{step}_mem_{suffix}.res")
                if os.path.isfile(out):
                    continue
                os.system(f"source {MAKE_RES_SH} 1 {src} {out}")


if __name__ == "__main__":
    main()
