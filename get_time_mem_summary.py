import Log_check
import sys

b = Log_check.TimeMem()
txt="/eos/cms/store/user/cmsbuild/profiling/data/"+sys.argv[1]+"/slc7_amd64_gcc900/23434.21/step3_TimeMemoryInfo.log"
a = b.Get_TimeMem(txt)
vsize = a["vsize"]
rss = a["rss"]
time = a["time"]
evt = a["event"]

f = open("Time_Mem_Summary/"+sys.argv[1]+"_step3.txt","w")
f.write("Summary for "+str(len(vsize))+" events\n")
f.write("Max VSIZ "+str(max(vsize))+" on evt "+str(1+a.loc[a["vsize"].idxmax()]["event"])+" ; max RSS "+str(max(rss))+" on evt "+str(1+a.loc[a["rss"].idxmax()]["event"])+"\n")
if len(vsize)>0:
	f.write("Time av "+str(sum(time)/len(time))+" s/evt   max "+str(max(time))+" s on evt "+str(1+a.loc[a["time"].idxmax()]["event"])+"\n")
if len(vsize)>1:
	f.write("M1 Time av "+str(sum(time[1:])/len(time[1:]))+" s/evt   max "+str(max(time[1:]))+" s on evt "+str(1+a.loc[a["time"][1:].idxmax()]["event"])+"\n")
if len(vsize)>8:
	f.write("M8 Time av "+str(sum(time[8:])/len(time[8:]))+" s/evt   max "+str(max(time[8:]))+" s on evt "+str(1+a.loc[a["time"][8:].idxmax()]["event"])+"\n")
f.close()

txt="/eos/cms/store/user/cmsbuild/profiling/data/"+sys.argv[1]+"/slc7_amd64_gcc900/23434.21/step4_TimeMemoryInfo.log"
a = b.Get_TimeMem(txt)
vsize = a["vsize"]
rss = a["rss"]
time = a["time"]
evt = a["event"]

f = open("Time_Mem_Summary/"+sys.argv[1]+"_step4.txt","w")
f.write("Summary for "+str(len(vsize))+" events\n")
f.write("Max VSIZ "+str(max(vsize))+" on evt "+str(1+a.loc[a["vsize"].idxmax()]["event"])+" ; max RSS "+str(max(rss))+" on evt "+str(1+a.loc[a["rss"].idxmax()]["event"])+"\n")
if len(vsize)>0:
	f.write("Time av "+str(sum(time)/len(time))+" s/evt   max "+str(max(time))+" s on evt "+str(1+a.loc[a["time"].idxmax()]["event"])+"\n")
if len(vsize)>1:
	f.write("M1 Time av "+str(sum(time[1:])/len(time[1:]))+" s/evt   max "+str(max(time[1:]))+" s on evt "+str(1+a.loc[a["time"][1:].idxmax()]["event"])+"\n")
if len(vsize)>8:
	f.write("M8 Time av "+str(sum(time[8:])/len(time[8:]))+" s/evt   max "+str(max(time[8:]))+" s on evt "+str(1+a.loc[a["time"][8:].idxmax()]["event"])+"\n")
f.close()
