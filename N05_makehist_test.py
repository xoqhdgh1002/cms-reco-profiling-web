print("Makes plots")
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
import N02_test
import sys

b = N02_test.TimeMem()

cmssw = [sys.argv[1][:-1]+str(x+1) for x in range(int(sys.argv[1][-1]))]
old_cmssw = sys.argv[1].split("_")
old_cmssw[2] = str(int(old_cmssw[2])-1)
del old_cmssw[-1]
cmssw.insert(0,"_".join(old_cmssw))

plt.rc('xtick',labelsize=20)
plt.rc('ytick',labelsize=20)

print("Evt after map distribution ####")
print("### Y3 ###")

## RSS
fig,axs = plt.subplots(2,3,figsize=(30,20))

color = ["k","r","g","b"]

rss_bins = numpy.linspace(3000,6000,50)
vsize_bins = numpy.linspace(4000,14000,50)
time_bins = numpy.linspace(0,400,100)

if sys.argv[2]=="4":
	rss_bins = numpy.linspace(1500,2200,100)
	vsize_bins = numpy.linspace(2200,3400,50)
	time_bins = numpy.linspace(0,80,100)

for i in cmssw:
	path="/eos/cms/store/user/cmsbuild/profiling/data/"+i+"/slc7_amd64_gcc900/23434.21/step"+sys.argv[2]+"_TimeMemoryInfo.log"
	a = b.Get_TimeMem(path)
	vsize = a["vsize"]
	rss = a["rss"]
	time = a["time"]
	evt = a["event"]
	axs[0,0].plot(evt,rss,'-o',color=color[cmssw.index(i)],alpha=0.7,label=i)
	axs[0,1].plot(evt,vsize,'-o',color=color[cmssw.index(i)],alpha=0.7,label=i)
	axs[0,2].plot(evt,time,'-o',color=color[cmssw.index(i)],label=i)
	axs[1,0].hist(rss,bins=rss_bins,color=color[cmssw.index(i)],histtype="step",linewidth=3,label=i)
	axs[1,1].hist(vsize,bins=vsize_bins,color=color[cmssw.index(i)],alpha=0.9,histtype="step",linewidth=3,label=i)
	axs[1,2].hist(time,bins=time_bins,color=color[cmssw.index(i)],alpha=0.9,histtype="step",linewidth=3,label=i)

axs[0,0].set_title('(RSS)Memory Profile',fontsize=30)
axs[0,0].set_xlim([0,101])
axs[0,0].set_xlabel('ith event',fontsize=25)
axs[0,0].set_ylabel('Memory(MB)',fontsize=25)

axs[0,0].legend(loc="best",prop={'size' :20})
axs[0,0].grid()

axs[0,1].set_title('(VSIZE)Memory Profile',fontsize=30)
axs[0,1].set_xlim([0,101])
axs[0,1].set_xlabel('ith event',fontsize=25)
axs[0,1].set_ylabel('Memory(MB)',fontsize=25)

axs[0,1].legend(loc="best",prop={'size' :20})
axs[0,1].grid()

axs[0,2].set_title('average CPU Time Profile',fontsize=30)
axs[0,2].set_xlim([0,101])
axs[0,2].set_yscale('log')
axs[0,2].set_xlabel('ith event',fontsize=25)
axs[0,2].set_ylabel('time (seconds)',fontsize=25)

axs[0,2].legend(loc="best",prop={'size' :20})
axs[0,2].grid()

axs[1,0].set_title('(RSS)Memory Profile',fontsize=30)
axs[1,0].set_ylabel('ith event',fontsize=25)
axs[1,0].set_xlabel('Memory(MB)',fontsize=25)
axs[1,0].grid()

axs[1,1].set_title('(VSIZE)Memory Profile',fontsize=30)
axs[1,1].set_ylabel('ith event',fontsize=25)
axs[1,1].set_xlabel('Memory(MB)',fontsize=25)
axs[1,1].ticklabel_format(useOffset=False)
axs[1,1].grid()

axs[1,2].set_title('CPU Time Profile',fontsize=30)
axs[1,2].set_ylabel('ith event',fontsize=25)
axs[1,2].set_xlabel('time (seconds)',fontsize=25)
axs[1,2].grid()

plt.tight_layout()
plt.show()
fig = plt.gcf()
plt.savefig('Summary_'+"_".join(sys.argv[1].split("_")[:-1])+'_step'+sys.argv[2]+'.png')
