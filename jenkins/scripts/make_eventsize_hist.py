import sys
import os
import yaml
import json
import shutil

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--workflow", type=str, help="workflow", default=None)
args = parser.parse_args()

workflow = args.workflow

data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'
result_path = '/eos/project/c/cmsweb/www/reco-prof/results/circles/web/data/'

cmssw_list = os.listdir(data_path)
cmssw_list.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))

steps = ['step3','step4','step5']
#------------------------------------------------------------------
for step in steps:

	csv = open("history_{0}.csv".format(step),'w')

	for cmssw in cmssw_list:

		gcc = os.listdir(data_path + cmssw)[0]
		TMI = '{0}{1}/{2}/{3}/{4}_TimeMemoryInfo.log'.format(data_path,cmssw,gcc,workflow,step)
		wf = workflow

		if os.path.isfile('{0}/{1}_{2}_{3}_eventSize.json'.format(result_path,cmssw,workflow,step)):
			with open('{0}/{1}_{2}_{3}_eventSize.json'.format(result_path,cmssw,workflow,step)) as f:
				json_data=json.load(f)
				events = json_data['total']['events']
				uncom = json_data['total']['size_uncom']/int(events)
				compr = json_data['total']['size_compr']/int(events)
				csv.write('{0},{1},{2}\n'.format(cmssw,uncom,compr))

	csv.close()
	shutil.move('history_{0}.csv'.format(step),'history_{0}_{1}.csv'.format(workflow,step))

	if len(open('history_{0}_{1}.csv'.format(workflow,step)).readlines()) == 0:
		os.remove('history_{0}_{1}.csv'.format(workflow,step))

