import sys
import os
import yaml

local_path = '/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/'
result_path = '/eos/project/c/cmsweb/www/reco-prof/results/'
result_address = 'http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/results/'

cmssw_yaml = yaml.load(open(local_path + 'yaml/data.yaml','r'))
cmssw_list = open(local_path + 'list/data.list','r').readlines()
cmssw_list = [i.strip('\n') for i in cmssw_list]

mother_version = ''
data_type = {"step3":"step3_AOD(RECO)","step4":"step4_MiniAOD(PAT)","step5":"step5_NanoAOD"}

print("""<!DOCTYPE html>
<html>
<head>
</head>
<body>"""
)

for cmssw in cmssw_list:#Version Loop

	child_version = '_'.join(cmssw.split('_')[0:3])

	if mother_version != child_version:#Select First version in Categroy

		if mother_version != '':

			print("""<hr size=\"3\" noshade>""")

		mother_version = child_version
		print(
"""	<h2>{0}_X <font size="4em"></font></h2>""".format(mother_version)
		)

		for sum_plot in os.listdir(result_path + 'summary_plot_html'):#Summary plot Loop

			if mother_version in sum_plot:#Input Summary plot for same version
				print(
"""<span style=" font: normal bold 1.0em Georgia, serif ; color: navy;">"""
				)
				if "step3" in sum_plot:
					print(
"""	<h3>Summary of {0}_X(RECO_AOD)({1}) <font size="2em"><a target='_blank' href="{2}summary_plot_html/{3}" title="shortSummary">[Short Summary Time and Memory(AOD)]</a></font></h3>""".format(mother_version,'.'.join(sum_plot.split('_')[4].split('.')[0:1]),result_address,sum_plot)
					)
				if "step4" in sum_plot:
					print(
"""	<h3>Summary of {0}_X(PAT_MiniAOD)({1}) <font size="2em"><a target='_blank' href="{2}summary_plot_html/{3}" title="shortSummary">[Short Summary Time and Memory(AOD)]</a></font></h3>""".format(mother_version,'.'.join(sum_plot.split('_')[4].split('.')[0:1]),result_address,sum_plot)
					)
				if "step5" in sum_plot:
					print(
"""	<h3>Summary of {0}_X(NanoAOD)({1}) <font size="2em"><a target='_blank' href="{2}summary_plot_html/{3}" title="shortSummary">[Short Summary Time and Memory(AOD)]</a></font></h3>""".format(mother_version,'.'.join(sum_plot.split('_')[4].split('.')[0:1]),result_address,sum_plot)
					)
		print(
"""<hr size="2" noshade>
<br>"""
		)#End of Summary plot Loop

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
	gcc = cmssw_yaml[cmssw]['gcc']
	
	for workflow in cmssw_yaml[cmssw]['workflow']:#Workflow Loop
		TMS_file = os.listdir('{0}Time_Mem_Summary/{1}/{2}/{3}'.format(result_path,cmssw,gcc,workflow))

		if len(TMS_file) == 0:#Select empty TMS dir

			continue;

		print("""
		<li><strong>{0}({1})</strong>
		<br>
		<ul>""".format(cmssw,workflow))
		
		for step in [i.split('.')[0] for i in TMS_file]:

			from_data_path = "{0}/{1}/{2}/".format(cmssw,gcc,workflow)
			from_cgi_path = "{0}/{1}/{2}/".format(cmssw,workflow,step)
			print("""
			<li><strong>{}</strong>""".format(data_type[step]))
			print("""
				<ul>
				<li>
				<a href="{0}Time_Mem_Summary/{1}{2}.txt" title="getTimeMemSummary">[getTimeMemSummary]</a>""".format(result_address,from_data_path,step)
			)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			if os.path.isdir("/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/{}".format(from_cgi_path)):
				res_list = os.listdir("{0}RES/{1}".format(result_path,from_data_path))
				if len(res_list) != 0:
					for res in [i for i in res_list if step in i]:
						if "cpu" in res:
							cgi_bin = "cpu_endjob"
							ig_number = ""
						if "mem" in res:
							cgi_bin = "mem_live.{}".format(res.split('_')[2].split('.')[0])
							ig_number = str(res.split('_')[2].split('.')[0])
						print("""
				<a href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/cgi-bin/igprof-navigator/releases/{0}{1}" title="{2} time check">[{3} Profiler igprof{4}]</a><a href="{5}RES/{6}{7}" title="txtLink">[txtLink]</a>""".format(from_cgi_path,cgi_bin,res.split('_')[1].split('.')[0],res.split('_')[1].split('.')[0],ig_number,result_address,from_data_path,res)
						)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			if os.path.isfile("{0}TimeDiff/{1}{2}.txt".format(result_path,from_data_path,step)) or os.path.isfile("{0}CompProd/{1}{2}.txt".format(result_path,from_data_path,step)):

				print("""
			<li>Comparison :
			<ul>""")

			if os.path.isfile("{0}TimeDiff/{1}{2}.txt".format(result_path,from_data_path,step)):
				f = open("{0}TimeDiff/{1}{2}.txt".format(result_path,from_data_path,step))
				timediff = f.readlines()[-1]

				print("""
				<li>
				<a href="{0}TimeDiff/{1}{2}.txt" title="TimeDiff">[TimeDiff]</a><span style=" font: Arial; font-size: small; color: green;"> preview: {3} s/ev ==> {4} s/ev </span>
				</li>""".format(result_address,from_data_path,step,timediff.split()[2],timediff.split()[5])				)

			if os.path.isfile("{0}CompProd/{1}{2}.txt".format(result_path,from_data_path,step)):
				f = open("{0}CompProd/{1}{2}.txt".format(result_path,from_data_path,step))
				compprod = f.readlines()[-1]

				print("""
				<li>
				<a href="{0}CompProd/{1}{2}.txt" title="Compare_Out_Prod">[CompareOutProd (edmEventSize)]</a><span style=" font: Arial; font-size: small; color: red;"> preview: {3} ==> {4} </span>
				</li>""".format(result_address,from_data_path,step,compprod.split()[1],compprod.split()[2]))

			if os.path.isfile("{0}TimeDiff/{1}{2}.txt".format(result_path,from_data_path,step)) or os.path.isfile("{0}CompProd/{1}{2}.txt".format(result_path,from_data_path,step)):

				print("""
			</ul>""")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			if os.path.isdir("{0}comp_igprof/html/{1}".format(result_path,from_cgi_path)):
				comp_igprof = os.listdir("{0}comp_igprof/html/{1}".format(result_path,from_cgi_path))
				if len(comp_igprof) != 0:
					print("""
			<li>Igprof comparison :
			<ul>""")
				for igprof_page in comp_igprof:
					if "cpu" in igprof_page:
						igprof_type = "cpu"
					else:
						igprof_type = "mem." + igprof_page.split('_')[1].split('.')[1]
					print("""
			<li>
			<a href="{0}comp_igprof/html/{1}{2}" title="{3} compare">[{4} compare]</a>
			</li>""".format(result_address,from_cgi_path,igprof_page,igprof_page.split('_')[0],igprof_type)
					)
				if len(comp_igprof) != 0:
					print("""
			</ul>"""
)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
			if child_version != "CMSSW_11_0":
				print("""
			<li>Circle (Pie chart) :
			<a href="http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/{0}" title="Circle">[Circle]</a>
			</li>""".format("circles/piechart.php?local=false&dataset="+cmssw+"%2F"+gcc+"%2F"+workflow+"%2F"+step+"_circles&resource=time_real&colours=default&groups=package&threshold=0")
				)

			print(
"		</ul>"
)

		print(
"	</ul>"
)

print("""</body>
</html>""")
