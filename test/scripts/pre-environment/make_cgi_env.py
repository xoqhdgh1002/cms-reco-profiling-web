import os
import sys
from shutil import copyfile
import yaml

data_path = '/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/'
#result_path = sys.argv[1] 
cmssw = os.listdir(data_path)

workflow = {}

for i in cmssw:
	workflow[i] = {'workflow':os.listdir(data_path +i)}
#	for j in os.listdir(data_path + i ):
#		for k in os.listdir(data_path + i + '/' + j):
#			child_dir = result_path + i + '/' + j + '/' + k
#			os.makedirs(child_dir, exist_ok=True)

with open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/yaml/cgi-bin.yaml','w') as f:
	yaml.dump(workflow,f)

cmssw.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))
with open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/list/cgi-bin.list','w') as f:
	for i in cmssw:
		f.write(i + '\n')
f.close()
