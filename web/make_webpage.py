import sys

path = "http://btae.web.cern.ch/btae/Service_Work/test/cms-reco-profiling-web/"
html_text = """
        <li><strong>cmssw_11_3_0_pre{}</strong>
        <br>
	<ul>""".format(sys.argv[1])
main = "CMSSW_11_3_0_pre"
cmssw=main+sys.argv[1]

for i in ["step3","step4"]:
	html_text += """
		<li><strong>{0}_AOD(RECO):</strong>
		<a href="{1}{2}" title="getTimeMemSummary">[getTimeMemSummary]</a>
		<a href="http://btae.web.cern.ch/btae/{3}" title="CPU time check">[CPU Profiler igprof]</a>
		<a target='_blank' href="{1}{4}" title="txtLink">[txtLink]</a>
		<a href="http://btae.web.cern.ch/btae/{5}" title="MEM check">[Memory Profiler igprof.1]</a>
		<a href="{1}{6}">[txtLink]</a>
		<a href="http://btae.web.cern.ch/btae/{7}" title="MEM check">[Memory Profiler igprof.50]</a>
		<a href="{1}{8}">[txtLink]</a>
		<a href="http://btae.web.cern.ch/btae/{9}" title="MEM check">[Memory Profiler igprof.99]</a>
		<a href="{1}{10}">[txtLink]</a>
	
		<ul>
			<li>Comparison:
		
			<ul type='disc'>
				<li>
				<a href="{1}{11}" title="TimeDiff">[TimeDiff]</a><span style=" font: Arial; font-size: small; color: green;">preview:81.8939 s/ev ==> 75.8557 s/ev  </span>
				</li>
				<li>
				<a href="{1}{12}" title="Compare_Out_Prod">[CompareOutProd (edmEventSize)]</a><span style=" font: Arial; font-size: small; color: red;">preview:  19856471 -> 19462609    </span>
				</li>
			</ul>
		
			<li>
			<a href="{1}{13}" title="CPU compare">[CPU compare]</a>
			</li>
			<li>
			<a href="{1}{14}" title="MEM compare">[MEM ig1 compare]</a>
			</li>
			<li>
			<a href="{1}{15}" title="MEM compare">[MEM ig99 compare]</a>
			</li>
			<li>Circle (Pie chart):
			<a href="http://btae.web.cern.ch/btae/{16}" title="Circle">[Circle]</a>
			</li>
		</ul>
	""".format(i,path,
	"Time_Mem_Summary/"+cmssw+"_"+i+".txt",
	"cgi-bin/igprof-navigator/igprof_"+cmssw+"_"+i+"_CPU",
	"res/RES_"+cmssw+"_"+i+"_CPU.res",
	"cgi-bin/igprof-navigator/igprof_"+cmssw+"_"+i+"_MEM.1",
	"res/RES_"+cmssw+"_"+i+"_MEM.1.res",
	"cgi-bin/igprof-navigator/igprof_"+cmssw+"_"+i+"_MEM.50",
	"res/RES_"+cmssw+"_"+i+"_MEM.50.res",
	"cgi-bin/igprof-navigator/igprof_"+cmssw+"_"+i+"_MEM.99",
	"res/RES_"+cmssw+"_"+i+"_MEM.99.res",
	"TimeDiff/TimeDiff_"+main+str(int(sys.argv[1])-1)+"_pre"+sys.argv[1]+"_"+i+".txt",
	"CompProd/CompProd_"+main+str(int(sys.argv[1])-1)+"_pre"+sys.argv[1]+"_"+i+".txt",
	"comp_igprof/comp_"+cmssw+"_"+i+"_CPU",
	"comp_igprof/comp_"+cmssw+"_"+i+"_MEM_1",
	"comp_igprof/comp_"+cmssw+"_"+i+"_MEM.99",
	"circles/web/piechart.html?local=false&dataset="+cmssw+'_'+i+"&resource=time_real&colours=default&groups=reco_PhaseII&threshold=0"
)
html_text+="""</ul>"""

print(html_text)
