import os
import sys

DATA_DIR = '/eos/cms/store/user/cmsbuild/profiling/data'

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--profile-data", type=str, default=DATA_DIR, help="profiling data location")
parser.add_argument("--release", type=str, help="CMSSW release", default=None)
parser.add_argument("--architecture", type=str, help="architecture for release", default=None)
parser.add_argument("--workflow", type=str, help="workflow", default=None)
args = parser.parse_args()

release = args.release
architecture = args.architecture
workflow = args.workflow

for step in ['step3','step4','step5']:
	file_path="{}/{}/{}/{}/{}.root".format(DATA_DIR,release,architecture,workflow,step)
	if os.path.isfile(file_path):
		os.system("edmEventSize -o eventSize_{0}.txt -F {1}".format(step,file_path))
		os.system("python3 make_eventsize-json.py eventSize_{}.txt".format(step))
