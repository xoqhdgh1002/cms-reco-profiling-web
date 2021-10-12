import os
import sys
from shutil import copyfile

data_path = '/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/'
result_path = './' + sys.argv[1]
cmssw = os.listdir(data_path)

for i in cmssw:
	for j in os.listdir(data_path + i ):
		for k in os.listdir(data_path + i + '/' + j):
			child_dir = result_path + i + '/' + j + '/' + k
			os.makedirs(child_dir)
