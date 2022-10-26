import os
import yaml
import Log_check

DATA_DIR = '/eos/cms/store/user/cmsbuild/profiling/data/' 

def parse_args():

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--profile-data", type=str, default=DATA_DIR, help="profiling data location")
	parser.add_argument("--release", type=str, help="CMSSW release", default=None)
	parser.add_argument("--architecture", type=str, help="architecture for release", default=None)
	parser.add_argument("--workflow", type=str, help="workflow", default=None)
	args = parser.parse_args()
	return args

if __name__ == "__main__":

	Log = Log_check.TimeMem()

	args = parse_args()

	release = args.release
	architecture = args.architecture
	workflow = args.workflow

	if workflow == "140.56" or workflow == "159.03":
		steps = ['step2','step3','step4','step5']
	else:
		steps = ['step3','step4','step5']

	for step in steps:
	
		base = os.path.join(DATA_DIR,release,architecture,workflow)
		tmi = os.path.join(base,"{}_TimeMemoryInfo.log".format(step))
	
		if os.path.isfile(tmi):
			structure = os.path.join(release,architecture,workflow)
			os.makedirs(structure, exist_ok=True)
			Log.Get_TimeMem(tmi)
			Log.summary("{}.txt".format(step))
