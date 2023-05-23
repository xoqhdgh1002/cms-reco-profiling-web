import os
import json
#import string

def findVersion(firstline):
	for idx in range(len(firstline)):
		if 'CMSSW' in firstline[idx]:
			flist = firstline[idx].split("/")
			for seq in range(len(flist)):
				if 'CMSSW' in flist[seq]:
					version = flist[seq]
					spec = flist[seq+2]
					step = flist[seq+3].replace(".root","")
	return version, spec, step


def main(filename):

	## Variables Initialization
	modules = []
	resources = []
	total = {}
	output = {}
	cnt = 0
	total_uncom = 0.0
	total_compr = 0.0

	with open(filename) as f:
		## lineloop
		for l in f:
			## avoiding lastline
			try:		
				vl = l.split(" ")
				#print(vl)

				## nEvents
				if cnt == 0:
					nEvents = vl[-1].replace("\n","")
					version, spec, step = findVersion(vl)
					cnt = cnt + 1
					continue

				if cnt == 1:
					cnt = cnt - 2
					continue

				## Normalline discriminator
				disc = vl[1]
				modulesDict = {}
				#print(disc)

				## Mainline clusters
				if '(' in disc:
					## Preprocessing
					collections = vl[0].split(":")
					collection = collections[0]
					#cl = collections[0]
					cl = vl[1]
					size_uncom = vl[-2]
					size_compr = vl[-1].replace("\n","")
					cl = cl.replace("(","").replace(")","")
		
					## Making dictionary
					modulesDict['events'] = int(nEvents)
					modulesDict['label'] = collection

					### SIZE * nEvents (because of overlapping division) / kB unit
					modulesDict['size_uncom'] = (float(size_uncom)/1024.)*int(nEvents)
					modulesDict['size_compr'] = (float(size_compr)/1024.)*int(nEvents)
					modulesDict['type'] = cl
					print(modulesDict)

					## Sum for total
					total_uncom = total_uncom + (float(size_uncom)/1024.)*int(nEvents)
					total_compr = total_compr + (float(size_compr)/1024.)*int(nEvents)

				else:
					size_uncom = vl[-2]
					size_compr = vl[-1].replace("\n","")

					## Sum for total
					total_uncom = total_uncom + (float(size_uncom)/1024.)*int(nEvents)
					total_compr = total_compr + (float(size_compr)/1024.)*int(nEvents)

				if len(modulesDict) != 0:
					modules.append(modulesDict)

			except:
				break

		## make resources
		size_uncomDict = {}
		size_comprDict = {}
		size_uncomDict['size_uncom'] = "Average Uncompressed Size"
		size_comprDict['size_compr'] = "Average Compressed Size"
		resources.append(size_uncomDict)
		resources.append(size_comprDict)

		## make total
		total['events'] = nEvents
		total['label'] = "step3_eventsize"
		total['size_uncom'] = total_uncom
		total['size_compr'] = total_compr
		total['type'] = "job"

		## merge modules
		output['modules'] = modules
		output['resources'] = resources
		output['total'] = total

		## Output
		fileModules = open(version+"_"+spec+"_"+step+"_eventSize.json","w")
		
		## dump and save
		json.dump(output, fileModules, ensure_ascii=False, indent=4 )
		## save history
		historySaver(version,spec,step,total_uncom,total_compr,nEvents)
		return 0

def historySaver(version,spec,step,total_uncom,total_compr,nEvents):
	with open('history_'+spec+'_'+step+'.csv','r') as hist:
		rd = csv.reader(hist)
		for l in rd:
			if version in l[0]:
				print("job duplicated. history did not saved")
				return 0
			else:
				continue
	with open('history_'+spec+'_'+step+'.csv','a',newline='') as hist:
		print("first "+version+" "+spec+" run! history will be saved")
		wr = csv.writer(hist)
		wr.writerow([version,total_uncom/int(nEvents),total_compr/int(nEvents)])
		return 0
### I/O check
if len(os.sys.argv) < 2:
	print("Missing Input file!!")
	exit(-9)


### define I/O
filename = os.sys.argv[1]
#output = os.sys.argv[2]


### main code
if __name__=="__main__":
	main(filename)

### EOF

