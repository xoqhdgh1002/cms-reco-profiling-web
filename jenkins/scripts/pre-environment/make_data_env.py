import os
import sys
from shutil import copyfile
import yaml

data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'
results_path = '/eos/project/c/cmsweb/www/reco-prof/results/' 
cmssw = os.listdir(data_path)

workflow ={}

for result_dir in os.listdir(results_path):
	if result_dir == 'comp_igprof' or result_dir == 'summary_plot_html':
		continue
	for i in cmssw:
		gcc = os.listdir(data_path + i)[0]
		workflow[i] = {"gcc":gcc,"workflow":os.listdir(data_path + i +'/' + gcc)}
		for j in os.listdir(data_path + i + '/' + gcc):
			child_dir = results_path + result_dir + '/' + i + '/' + gcc + '/' + j
			os.makedirs(child_dir,exist_ok=True) 
			os.system("cp {0}{1}/{2}/{3}/cmdLog_profiling.sh {4}cmdlog/{1}/{2}/{3}/cmdLog_profiling.txt".format(data_path,i,gcc,j,results_path))

with open('../../yaml/data.yaml','w') as f:
	yaml.dump(workflow,f)

cmssw.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))
with open('../../list/data.list','w') as f:
        for i in cmssw:
                f.write(i + '\n')
f.close()
