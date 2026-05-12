"""Extract the final 'Memory Report:' block from each step's TimeMemoryInfo.log.

Output filename: memory_report_step{N}.txt — must match the inline shell's
xrdcopy glob `memory_report_step*.txt`.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _common


def extract_last_memory_report(file_path: str) -> str | None:
    """Return the contiguous trailing block of 'Memory Report:' lines, or None."""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        lines = f.readlines()

    report_lines: list[str] = []
    seen = False
    for line in reversed(lines):
        if "Memory Report:" in line:
            report_lines.append(line.strip())
            seen = True
        elif seen:
            break

    if not report_lines:
        return None
    return "\n".join(reversed(report_lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="CMSSW Memory Report extractor")
    parser.add_argument("--release", required=True)
    parser.add_argument("--architecture", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--base-dir", default=_common.DATA_DIR)
    args = parser.parse_args()

    found_any = False
    for step in ("step3", "step4", "step5"):
        log_path = _common.step_file(
            args.release, args.architecture, args.workflow,
            step, "_TimeMemoryInfo.log", base=args.base_dir,
        )
        if not os.path.exists(log_path):
            continue

        report = extract_last_memory_report(log_path)
        if report is None:
            print(f"[{step}] 리포트 섹션을 찾을 수 없습니다.")
            continue

        out = f"memory_report_{step}.txt"
        with open(out, "w") as f:
            f.write(report)
        print(f"[{step}] 리포트 추출 완료 -> {out}")
        found_any = True

    if not found_any:
        print("결과: 생성된 리포트가 없습니다.")


if __name__ == "__main__":
    main()
