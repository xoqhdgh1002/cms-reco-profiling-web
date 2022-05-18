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
			os.makedirs(child_dir, exist_ok=True)

with open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/yaml/data.yaml','w') as f:
	yaml.dump(workflow,f)

cmssw.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))
with open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/list/data.list','w') as f:
        for i in cmssw:
                f.write(i + '\n')
f.close()
