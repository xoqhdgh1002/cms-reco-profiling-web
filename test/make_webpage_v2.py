import sys
import yaml
import os

path = "http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/"

yaml_file = yaml.load(open('data.yaml','r'))
sequential_file = open('cmssw.list','r')
cmssw_list = sequential_file.readlines()

data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'

cmssw_dict = dict()
for cmssw in cmssw_list:
	a = '_'.join(cmssw.split('_')[:3])
	for workflow in yaml_file[cmssw.strip('\n')]["workflow"]:
		if not a in cmssw_dict.keys():
			cmssw_dict['_'.join(cmssw.split('_')[:3])] = list()
		if not workflow in cmssw_dict[a]:
			cmssw_dict[a].append(workflow)
cmssw_check = list()

for cmssw in cmssw_list:
	category = '_'.join(cmssw.split('_')[:3])
	if not category in cmssw_check:
		cmssw_check.append(category)
		for a in cmssw_dict[category]:
			
		        print("""<hr size="3" noshade>
        <h2>{0}_X <font size="4em"></font></h2>

<span style=" font: normal bold 1.0em Georgia, serif ; color: navy;">
        <h3>Summary of {0}_X(RECO_AOD)({1}) <font size="2em"><a target='_blank' href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/results/summary_plot_html/{0}_step3_{1}.html" title="shortSummary">[Short Summary Time and Memory(AOD)]</a></font></h3>
        <h3>Summary of {0}_X(PAT_MINIAOD)({1}) <font size="2em"><a target='_blank' href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/results/summary_plot_html/{0}_step4_{1}.html" title="shortSummary">[Short Summary Time and Memory(PAT)]</a></font></h3>
</span>
<hr size="2" noshade>
<br>""".format(category,a))
	cmssw = cmssw.strip('\n')
	slc = yaml_file[cmssw.strip('\n')]["gcc"]
	for version in yaml_file[cmssw.strip('\n')]["workflow"]:
		print("""
	        <li><strong>{0}({1})</strong>
	        <br>
		<ul>""".format(cmssw,version))
		for i in ["step3","step4"]:
			timediff_path = "/eos/project/c/cmsweb/www/reco-prof/results/TimeDiff/{0}/{1}/{2}/{3}.txt".format(cmssw,slc,version,i)
			if os.path.isfile(timediff_path):
				f = open(timediff_path,'r')
				timediff = f.readlines()[-1]
		
			compprod_path = "/eos/project/c/cmsweb/www/reco-prof/results/CompProd/{0}/{1}/{2}/{3}.txt".format(cmssw,slc,version,i)
			if os.path.isfile(compprod_path):
				f = open(compprod_path,'r')
				compprod = f.readlines()[-1]

			datatype = "AOD(RECO)"
			if i == "step4":
				datatype = "MiniAOD(PAT)"
			data_dir = "{0}/{1}/{2}/{3}.txt".format(cmssw,slc,version,i)
			cgi_dir = "{0}/{1}/{2}/".format(cmssw,version,i)


			html_text = """
			<li><strong>{0}_{1}:</strong>
			<a href="{2}results/Time_Mem_Summary/{3}" title="getTimeMemSummary">[getTimeMemSummary]</a>
			<a href="{2}cgi-bin/igprof-navigator/releases/{4}cpu_endjob" title="CPU time check">[CPU Profiler igprof]</a>
			<a target='_blank' href="{2}results/RES/{4}cpu_endjob.res" title="txtLink">[txtLink]</a>
			<a href="{2}cgi-bin/igprof-navigator/releases/{4}mem_live.1" title="MEM check">[Memory Profiler igprof.1]</a>
			<a href="{2}results/RES/{4}mem_live.1.res">[txtLink]</a>
			<a href="{2}cgi-bin/igprof-navigator/releases/{4}mem_live.50" title="MEM check">[Memory Profiler igprof.50]</a>
			<a href="{2}results/RES/{4}mem_live.50.res">[txtLink]</a>
			<a href="{2}cgi-bin/igprof-navigator/releases/{4}mem_live.99" title="MEM check">[Memory Profiler igprof.99]</a>
			<a href="{2}results/RES/{4}mem_live.99.res">[txtLink]</a>
		<ul>
""".format(i,datatype,path,data_dir,cgi_dir)

			comp_igprof_path = "/eos/project/c/cmsweb/www/reco-prof/results/comp_igprof/html/{0}cpu_endjob.html".format(cgi_dir)

			if os.path.isfile(timediff_path):
				html_text+= """
			<li>Comparison:
		
			<ul type='disc'>
				<li>
				<a href="{0}results/TimeDiff/{1}" title="TimeDiff">[TimeDiff]</a><span style=" font: Arial; font-size: small; color: green;">preview: {2} s/ev ==> {3} s/ev </span>
				</li>
				<li>
				<a href="{0}results/CompProd/{1}" title="Compare_Out_Prod">[CompareOutProd (edmEventSize)]</a><span style=" font: Arial; font-size: small; color: red;">preview: {4} ==> {5} </span>
				</li>
			</ul>
			""".format(path,data_dir,timediff.split()[2],timediff.split()[5],compprod.split()[1],compprod.split()[2])

			if os.path.isfile(comp_igprof_path):
				html_text +="""
			<li>
			<a href="{0}result/comp_igprof/html/{1}cpu_endjob.html" title="CPU compare">[CPU compare]</a>
			</li>
			<li>
			<a href="{0}result/comp_igprof/html/{1}mem_live.1.html" title="MEM compare">[MEM ig1 compare]</a>
			</li>
			<li>
			<a href="{0}result/comp_igprof/html/{1}mem_live.99.html" title="MEM compare">[MEM ig99 compare]</a>
			</li>
	""".format(path,data_dir)
			html_text+="""
			<li>Circle (Pie chart):
			<a href="{0}{1}" title="Circle">[Circle]</a>
			</li>
		</ul>""".format(path,"circles/piechart.php?local=false&dataset="+cmssw+"%2F"+slc+"%2F"+version+"%2F"+i+"_circles&resource=time_real&colours=default&groups=package&threshold=0")

			print(html_text)
		print("""</ul>""")
