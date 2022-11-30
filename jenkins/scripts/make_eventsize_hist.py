import sys
import os
import yaml
import json
import re
import shutil


data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'
result_path = '/eos/project/c/cmsweb/www/reco-prof/results/circles/web/data/'

cmssw_list = os.listdir(data_path)
cmssw_list.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))

for run in [3,4]:
	
	steps = ['step3','step4','step5']
	#------------------------------------------------------------------
	for step in steps:
	
		csv = open("history_{0}.csv".format(step),'w')
	
		for cmssw in cmssw_list:
	
			gcc = os.listdir(data_path + cmssw)[0]
			for workflow in os.listdir(data_path + cmssw + '/' + gcc):
				TMI = '{0}{1}/{2}/{3}/{4}_TimeMemoryInfo.log'.format(data_path,cmssw,gcc,workflow,step)
				if os.path.isfile(TMI):
					with open(TMI) as f:
						flag = 0
						for i in f:
							flag += 1
							if flag == 10:
								break
	
							matching1 = re.compile('^the query is file dataset')
							matching2 = re.compile('.*Run{}.*'.format(run))

							if matching1.match(i): 
	
								if matching2.match(i):
	
									wf = workflow
	
									if os.path.isfile('{0}/{1}_{2}_{3}_eventSize.json'.format(result_path,cmssw,workflow,step)):
	
										with open('{0}/{1}_{2}_{3}_eventSize.json'.format(result_path,cmssw,workflow,step)) as f:
											json_data=json.load(f)
											events = json_data['total']['events']
											uncom = json_data['total']['size_uncom']/int(events)
											compr = json_data['total']['size_compr']/int(events)
							
											csv.write('{0},{1},{2}\n'.format(cmssw,uncom,compr))
											break
		
		f.close()
		shutil.move('history_{0}.csv'.format(step),'history_{0}_{1}.csv'.format(wf,step))
