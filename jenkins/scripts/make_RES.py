import yaml
import os
import sys

yaml_file = yaml.load(open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/yaml/data.yaml','r'))

data_path = '/eos/cms/store/user/cmsbuild/profiling/data'

for step in ['step3','step4','step5']:
	for cmssw in yaml_file:
		for workflow in yaml_file[cmssw]['workflow']:
			gcc = yaml_file[cmssw]['gcc']
			data_dir = "{0}/{1}/{2}".format(cmssw,gcc,workflow)
			gz_list = [x for x in os.listdir("{0}/{1}/{2}/{3}".format(data_path,cmssw,gcc,workflow)) if "gz" in x and step in x]
			if len(gz_list)==0:
				continue
			print(cmssw,gcc,workflow,step)
			for gz in gz_list:
				if "CPU" in gz:
					if os.path.isfile("/eos/project/c/cmsweb/www/reco-prof/results/RES/{0}/{1}_cpu.res".format(data_dir,step)):
						continue
					os.system("source ./make_res.sh 0 {0}/{1}/{2} /eos/project/c/cmsweb/www/reco-prof/results/RES/{1}/{3}_cpu.res".format(data_path,data_dir,gz,step))
				elif "MEM" in gz:
					if os.path.isfile("/eos/project/c/cmsweb/www/reco-prof/results/RES/{0}/{1}_mem_{2}.res".format(data_dir,step,gz.split(".")[1])):
						continue
					os.system("source ./make_res.sh 1 {0}/{1}/{2} /eos/project/c/cmsweb/www/reco-prof/results/RES/{1}/{3}_mem_{4}.res".format(data_path,data_dir,gz,step,gz.split(".")[1]))
