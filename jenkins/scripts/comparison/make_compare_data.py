import yaml
import os
import sys

data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'
cmssw = os.listdir(data_path)
cmssw.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--operator", type=str, help="operator", default=None)
parser.add_argument("--workflow", type=str, help="workflow", default=None)
parser.add_argument("--release", type=str, help="CMSSW release", default=None)
args = parser.parse_args()

new = args.release
old = cmssw[cmssw.index(new)-1]
new_architecture = os.listdir(os.path.join(data_path,new))[0]
old_architecture = os.listdir(os.path.join(data_path,old))[0]
workflow = args.workflow
operator = args.operator

result_path = "{0}/{1}/{2}/".format(new,new_architecture,workflow)

for step in ['step3','step4','step5']:
	
	new_data = os.path.join(data_path,new,new_architecture,workflow,'{}_TimeMemoryInfo.log'.format(step))
	old_data = os.path.join(data_path,old,old_architecture,workflow,'{}_TimeMemoryInfo.log'.format(step))

	os.makedirs(result_path,exist_ok = True)
	if os.path.isfile(new_data) and os.path.isfile(old_data):
		os.system("source ./{8} {0}{2}/{3}/{6}/{7} {0}{4}/{5}/{6}/{7} > {1}{7}.txt".format(
		data_path,result_path,
		old,old_architecture,
		new,new_architecture,
		workflow,step,operator))

