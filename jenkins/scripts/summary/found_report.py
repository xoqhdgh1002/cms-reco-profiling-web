import argparse
import os
import sys

def extract_last_memory_report(file_path):
    if not os.path.exists(file_path):
        return None

    report_lines = []
    found_report = False

    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        for line in reversed(lines):
            if "Memory Report:" in line:
                report_lines.append(line.strip())
                found_report = True
            elif found_report:
                break
    
    return "\n".join(reversed(report_lines)) if report_lines else None

def main():
    parser = argparse.ArgumentParser(description="CMSSW Memory Report Extractor")
    
    parser.add_argument("--release", required=True, help="CMSSW release")
    parser.add_argument("--architecture", required=True, help="Architecture")
    parser.add_argument("--workflow", required=True, help="Workflow ID")
    parser.add_argument("--base-dir", default="/eos/cms/store/user/cmsbuild/profiling/data", help="Base directory path")

    args = parser.parse_args()

    steps = ["step3", "step4", "step5"]
    found_any = False

    for step in steps:
        log_file_path = os.path.join(
            args.base_dir, 
            args.release, 
            args.architecture, 
            args.workflow, 
            f"{step}_TimeMemoryInfo.log"
        )

        if os.path.exists(log_file_path):
            last_report = extract_last_memory_report(log_file_path)

            if last_report:
                # 파일명에서 workflow 제거: memory_report_step3.txt
                output_filename = f"memory_report_{step}.txt"
                with open(output_filename, "w") as out_f:
                    out_f.write(last_report)
                
                print(f"[{step}] 리포트 추출 완료 -> {output_filename}")
                found_any = True
            else:
                print(f"[{step}] 리포트 섹션을 찾을 수 없습니다.")
        else:
            # 로그 파일 자체가 없는 경우 출력 (필요 없으면 생략 가능)
            pass

    if not found_any:
        print("결과: 생성된 리포트가 없습니다.")

if __name__ == "__main__":
    main()