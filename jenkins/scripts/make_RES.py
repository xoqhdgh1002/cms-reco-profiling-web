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
	data_dir = "{0}/{1}/{2}".format(release,architecture,workflow)
	gz_list = [x for x in os.listdir("{0}/{1}/{2}/{3}".format(DATA_DIR,release,architecture,workflow)) if "gz" in x and step in x]
	if len(gz_list)==0:
		continue
	print(release,architecture,workflow,step)
	for gz in gz_list:
		if "CPU" in gz:
			if os.path.isfile("/eos/project/c/cmsweb/www/reco-prof/results/RES/{0}/{1}_cpu.res".format(data_dir,step)):
				continue
			os.system("source ./make_res.sh 0 {0}/{1}/{2} /eos/project/c/cmsweb/www/reco-prof/results/RES/{1}/{3}_cpu.res".format(DATA_DIR,data_dir,gz,step))
		elif "MEM" in gz:
			if os.path.isfile("/eos/project/c/cmsweb/www/reco-prof/results/RES/{0}/{1}_mem_{2}.res".format(data_dir,step,gz.split(".")[1])):
				continue
			os.system("source ./make_res.sh 1 {0}/{1}/{2} /eos/project/c/cmsweb/www/reco-prof/results/RES/{1}/{3}_mem_{4}.res".format(DATA_DIR,data_dir,gz,step,gz.split(".")[1]))
