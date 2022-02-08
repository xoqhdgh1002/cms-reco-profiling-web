import os
import yaml
import Log_check

data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'
result_path = '/eos/project/c/cmsweb/www/reco-prof/results/Time_Mem_Summary/'
Log = Log_check.TimeMem()

yaml_file = yaml.load(open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/yaml/data.yaml','r'))

for step in ['step3','step4','step5']:
	for cmssw in yaml_file:
		gcc = yaml_file[cmssw]['gcc']
		for workflow in yaml_file[cmssw]["workflow"]:
			file_path = data_path + "{0}/{1}/{2}/{3}_TimeMemoryInfo.log".format(cmssw,gcc,workflow,step)
			if workflow == "29234.21" or workflow == "136.889":
				continue
			if os.path.isfile(file_path):
				if os.path.isfile(result_path+"{0}/{1}/{2}/{3}.txt".format(cmssw,gcc,workflow,step)):
					continue
				Log.Get_TimeMem(file_path)
				Log.summary(result_path+"{0}/{1}/{2}/{3}.txt".format(cmssw,gcc,workflow,step))
