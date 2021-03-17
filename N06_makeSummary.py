import sys
import N02_test

html="""<html>
<head>
<style>
table {
   border-collapse: collapse;
   border:0;
   text-align:center;
   width: 50%;
   table-layout:fixed;
}
th, td {
   text-align: center;
   width:230px;
   padding: 2px;
}
tr:nth-child(odd){background-color: #f2f2f2}
</style>
<title>Summary Time and Memory Test</title>
</head>
<body>

<h2>Summary : Time and Memory Test: """+sys.argv[1]+"""</h2>
<div style="overflow-x:auto;">
<table>
<tr></th><th> VERSION          </th><th> (RSS)MaxMemory(evt)</th><th> (VSIZE)MaxMemory(evt)</th><th> AverageTime</th><th> MaxTime(evt)</th></tr>
"""

b = N02_test.TimeMem()

cmssw = [sys.argv[1][:-1]+str(x+1) for x in range(int(sys.argv[1][-1]))]
for i in cmssw:
	path="/eos/cms/store/user/cmsbuild/profiling/data/"+i+"/slc7_amd64_gcc900/23434.21/step"+sys.argv[2]+"_TimeMemoryInfo.log"
	a = b.Get_TimeMem(path)
	vsize = a["vsize"]
	rss = a["rss"]
	time = a["time"]
	evt = a["event"]

	html+="""<tr></td><td> """+i+""" </td><td> """+str(max(rss))+"""("""+str(1+evt[rss.index(max(rss))])+""")"""+""" </td><td> """+str(max(vsize))+"""("""+str(1+evt[vsize.index(max(vsize))])+""")"""+""" </td><td> """+str(sum(time[1:])/len(time[1:]))+""" </td><td> """+str(max(time[1:]))+"""("""+str(1+evt[time.index(max(time[1:]))])+""")"""+""" </td></tr>
"""

target = sys.argv[1].split("_")
target = "_".join(target[:-1])

html+="""</table>
</div>
<figure><img src="Summary_"""+target+"""_step"""+sys.argv[2]+""".png" alt="The Pulpit Rock" width="1500"></figure>
</body>
</html>"""

htmlfile = open("summary_table_"+target+"_step"+sys.argv[2]+".html","w")
htmlfile.write(html)
htmlfile.close()
