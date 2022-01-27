import sqlite3
import sys
import pandas as pd
import yaml
import os

yaml_file = yaml.load(open('/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/test/yaml/cgi-bin.yaml','r'))

data_path = '/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases'

for step in ['step3','step4','step5']:
	for cmssw in yaml_file:
		for workflow in yaml_file[cmssw]["workflow"]:
			if not os.path.isdir("{0}/{1}/{2}/{3}/".format(data_path,cmssw,workflow,step)):
				continue
			file_list = os.listdir("{0}/{1}/{2}/{3}/".format(data_path,cmssw,workflow,step))
			if len(file_list) == 0:
				continue
			print(file_list)
			for datatype in file_list:
				if datatype in ["mem_live.25.sql3","mem_live.50.sql3","mem_live.200.sql3"] or not "sql3" in datatype:
					continue
				if "live" in datatype:
						csv = ".".join(datatype.split(".")[:2])
				elif "cpu_endjob" in datatype:
						csv = datatype.split(".")[0]
				else:
					continue

				path = "{0}/{1}/{2}/{3}/{4}".format(data_path,cmssw,workflow,step,datatype)
				print(path)
				if os.path.isfile(path):
					csv_name = "../comp_igprof/{0}/{1}/{2}/{3}.csv".format(cmssw,workflow,step,csv)

					if os.path.isfile(csv_name):
						continue
					print(csv_name)
					
					conn = sqlite3.connect(path)
					cur = conn.cursor()
					if datatype == "cpu_endjob":					
						cur.execute("SELECT summary.tick_period FROM summary")
						tick_period = cur.fetchone()[0]
					else:
						tick_period = 1

					cur.execute("SELECT symbols.name, mainrows.cumulative_count FROM symbols INNER JOIN mainrows ON mainrows.symbol_id IN (symbols.id)")
					spont = cur.fetchone()
					
					cur.execute("SELECT s.name,mr.id FROM mainrows mr INNER JOIN symbols s ON s.id IN(mr.symbol_id)")
					rows = cur.fetchall()
					
					child = []
					
					for row in rows:
					
						if "doEvent" in row[0]:
							cur.execute("""SELECT sym.name,
									myself.cumulative_count,
									c.pct
								FROM children c
								INNER JOIN mainrows mr ON mr.id IN (c.parent_id)
								INNER JOIN mainrows myself ON myself.id IN (c.self_id)
								INNER JOIN symbols sym ON sym.id IN (myself.symbol_id)
								WHERE c.parent_id = %s
								ORDER BY c.from_parent_count DESC;
								""" % row[1])
					
						child += cur.fetchall()

					print(len(child),os.path.isfile(path))
					if len(child) == 0:
						continue				
	
					child = pd.DataFrame(child)
					child.columns = ['name','cumulative','pct']
					child['cumulative'] = child['cumulative']*tick_period
					child.sort_values(by=['cumulative'],axis=0,ascending=False,inplace=True)
					child['spontaneous'] = spont[1]*tick_period 
					
					child = child[~child["name"].str.contains("edm::service::Timing::postModuleEvent")] 
					child = child[~child["name"].str.contains("edm::Event::commit_")]
					child = child[~child["name"].str.contains("edm::Event::~Event()")]
					child = child[~child["name"].str.contains("edm::Event::setProducer")]
					child = child[~child["name"].str.contains("edm::Event::setConsumer")]
					child = child[~child["name"].str.contains("edm::SystemTimeKeeper::startModuleEvent")]
					child = child[~child["name"].str.contains("edm::ModuleCallingContext::getStreamContext()")]
					child = child[~child["name"].str.contains("edm::service::MessageLogger::unEstablishModule")]
					
					child.to_csv(csv_name,index=False)
