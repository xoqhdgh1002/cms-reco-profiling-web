import argparse
import os
import sys

def extract_all_memory_reports(file_path):
    """
    Extracts all Memory Report blocks from a log file.
    Consecutive 'Memory Report:' lines form one block; gaps between them separate blocks.
    Returns:
        {
            'initial': list of blocks (each block is a list of lines) -- per-core reports at job start,
            'final':   list of lines -- final summary report at job end
        }
    or None if no reports found.
    """
    if not os.path.exists(file_path):
        return None

    blocks = []
    current_block = []

    with open(file_path, 'r') as f:
        for line in f:
            if "Memory Report:" in line:
                current_block.append(line.strip())
            elif current_block:
                blocks.append(current_block)
                current_block = []

    if current_block:
        blocks.append(current_block)

    if not blocks:
        return None

    # Last block = final summary; everything before = initial per-core reports
    return {
        'initial': blocks[:-1],
        'final':   blocks[-1],
    }

def process_workflow(base_dir, release, architecture, workflow):
    steps = ["step3", "step4", "step5"]
    found_any = False

    for step in steps:
        log_file_path = os.path.join(
            base_dir,
            release,
            architecture,
            workflow,
            f"{step}.log"
        )

        if not os.path.exists(log_file_path):
            continue

        reports = extract_all_memory_reports(log_file_path)

        if not reports:
            print(f"  [{step}] Memory Report 섹션을 찾을 수 없습니다.")
            continue

        output_filename = f"memory_report_{workflow}_{step}.txt"
        with open(output_filename, "w") as out_f:

            # --- Initial per-core reports ---
            initial_blocks = reports['initial']
            if initial_blocks:
                core_idx = 1
                for block in initial_blocks:
                    chunk = []
                    for line in block:
                        chunk.append(line)
                        if "# deallocations calls" in line:
                            out_f.write(f"--- Initial Report (core {core_idx}) ---\n")
                            out_f.write("\n".join(chunk) + "\n\n")
                            core_idx += 1
                            chunk = []
                    if chunk:
                        out_f.write(f"--- Initial Report (core {core_idx}) ---\n")
                        out_f.write("\n".join(chunk) + "\n\n")
                        core_idx += 1

            # --- Final summary ---
            out_f.write("--- Final Summary ---\n")
            out_f.write("\n".join(reports['final']) + "\n")

        n_cores = sum(
            sum(1 for line in block if "# deallocations calls" in line)
            for block in reports['initial']
        )
        print(f"  [{step}] 추출 완료 -> {output_filename}  "
              f"(초기 리포트: {n_cores}개 코어, 최종 요약: 1개)")
        found_any = True

    return found_any

def main():
    parser = argparse.ArgumentParser(description="CMSSW Memory Report Extractor")

    parser.add_argument("--release",      required=True, help="CMSSW release")
    parser.add_argument("--architecture", required=True, help="Architecture")
    parser.add_argument("--workflow",     default=None,  help="Workflow ID (생략 시 전체 workflow 처리)")
    parser.add_argument("--base-dir", default="/eos/cms/store/user/cmsbuild/profiling/data",
                        help="Base directory path")

    args = parser.parse_args()

    release_dir = os.path.join(args.base_dir, args.release, args.architecture)
    if not os.path.exists(release_dir):
        print(f"디렉토리를 찾을 수 없습니다: {release_dir}")
        sys.exit(1)

    # --workflow 지정 시 해당 workflow만, 없으면 전체 순회
    if args.workflow:
        workflows = [args.workflow]
    else:
        workflows = sorted(os.listdir(release_dir))

    total_found = False
    for workflow in workflows:
        print(f"=== {workflow} ===")
        found = process_workflow(args.base_dir, args.release, args.architecture, workflow)
        if found:
            total_found = True

    if not total_found:
        print("결과: 생성된 리포트가 없습니다.")

if __name__ == "__main__":
    main()
