import os
import sys
import csv
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import gridspec
#import mplhep as hep

version = str(os.sys.argv[1])
spec = os.sys.argv[2]

def main(version,spec,step,job):
	X = [] # CMSSW Version
	AUS = [] # Average Uncompressed Size
	ACS = [] # Average Compressed Size
	version = version.replace("CMSSW_","")[:-5]

	with open('history_'+spec+'_'+step+'.csv','r') as hist:
		rd = csv.reader(hist)
		idx = 0
		for l in rd:
			X.append(l[0].replace("CMSSW_",""))
			AUS.append(round(float(l[1]),1))
			ACS.append(round(float(l[2]),1))
	if job == 'A':
		X = X[-8:]
		AUS = AUS[-8:]
		ACS = ACS[-8:]
	elif job == 'B':
		m = [i for i in range(len(X)) if str(version) in X[i]]
		X = X[min(m):max(m)+1]
		AUS = AUS[min(m):max(m)+1]
		ACS = ACS[min(m):max(m)+1]
		print(X)

	plt.rcParams["figure.figsize"] = (20,10)
	plt.rc('font', size=20)     
	plt.rc('axes', labelsize=20) 
	plt.rc('xtick', labelsize=20)
	plt.rc('ytick', labelsize=20) 
	plt.rc('legend', fontsize=20) 
	fig, ax1 = plt.subplots()
	line1 = ax1.plot(X,AUS, '--bo',label ="Average Uncompressed Size ("+spec+")", color ='blue',linewidth=3,markersize=8)
	for i, v in enumerate(X):
		ax1.text(v, AUS[i], AUS[i],
		     fontsize = 20,
		     color='black',
		     horizontalalignment='right',  # horizontalalignment (left, center, right)
		     verticalalignment='bottom')    # verticalalignment (top, center, bottom)

	ax2 = ax1.twinx()
	line2 = ax2.plot(X,ACS, '--bo',label ="Average Compressed Size ("+spec+")", color ='green',linewidth=3,markersize=8)
	for i, v in enumerate(X):
		ax2.text(v, ACS[i], ACS[i],
		     fontsize = 20,
		     color='black',
		     horizontalalignment='left',  # horizontalalignment (left, center, right)
		     verticalalignment='top')    # verticalalignment (top, center, bottom)

	ax1.set_xlabel("CMSSW Version", fontsize=25)
	ax1.set_ylabel("Size/Event [kB]", fontsize=25)
	ax2.set_ylabel("Size/Event [kB]", fontsize=25)
	lines = line1 + line2
	labels = [l.get_label() for l in lines]
	ax1.legend(lines, labels)

	if job == 'A':
		plt.savefig("Recent8EventSize_"+spec+"_"+step+".png")
		plt.close()
	if job == 'B':
		plt.savefig("EventsizeSummary_"+spec+"_"+step+".png")
		plt.close()
		
		



### I/O check
if len(os.sys.argv) < 2:
        print("Missing Input file!!")
        exit(-9)



### main code
if __name__=="__main__":

	for step in ['step3','step4','step5']:
		if os.path.isfile("history_{0}_{1}.csv".format(spec,step)):
			main(version,spec,step,'A')
			main(version,spec,step,'B')
