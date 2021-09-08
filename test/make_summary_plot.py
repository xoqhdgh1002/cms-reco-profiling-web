from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as io
import sys
import Log_check
import pandas as pd
import numpy as np
import random
import yaml

log_object = Log_check.TimeMem()

subplot_title=["Summary Table", "(RSS)Memory Profile", "(VSIZE)Memory Profile", "average CPU Time Profile", "(RSS)Memory Profile", "(VSIZE)Memory Profile", "CPU Time Profile"]

data_path = '/eos/cms/store/user/cmsbuild/profiling/data/'

yaml_file = yaml.load(open('data.yaml','r'))
sequential_file = open('cmssw.list','r')
cmssw_list = [x for x in sequential_file.readlines() if sys.argv[1] in x]

version = sys.argv[1]
cmssw_dict = dict()
for cmssw in cmssw_list:

	for workflow in yaml_file[cmssw.strip('\n')]["workflow"]:

		if not workflow in cmssw_dict.keys():

			cmssw_dict[workflow] = list()

		cmssw_dict[workflow].append(cmssw.strip('\n'))

for step in ['step3','step4']:

	for workflow in cmssw_dict.keys():

		fig = make_subplots(rows=3, cols=3, 
			row_heights=[0.2,0.4,0.4],
			subplot_titles=subplot_title, 
			start_cell="top-left",
			vertical_spacing=0.1,
			specs=[[{"colspan":3,"type":"table"},None,None],
				[{},{},{}],
				[{},{},{}]]
		)

		max_rss=[]
		max_vsize=[]
		max_time=[]
		avrg_time=[]


		for cmssw in cmssw_dict[workflow]:

			gcc = yaml_file[cmssw]["gcc"]
			path = "{0}{1}/{2}/{3}/{4}_TimeMemoryInfo.log".format(data_path,cmssw,gcc,workflow,step)
			df = log_object.Get_TimeMem(path)
			hex_number = '#'+str(hex(random.randint(0,16777215)))[2:].zfill(6)

			fig.add_trace(go.Scatter(x=df["event"],y=df["rss"],mode="lines",line=dict(color=hex_number),legendgroup=cmssw,hovertext=cmssw,name=cmssw),row=2,col=1)
			fig.add_trace(go.Scatter(x=df["event"],y=df["vsize"],mode="lines",line=dict(color=hex_number),legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=2,col=2)
			fig.add_trace(go.Scatter(x=df["event"],y=df["time"],mode="lines",line=dict(color=hex_number),legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=2,col=3)
			fig.add_trace(go.Histogram(x=df["rss"],nbinsx=20,bingroup=1,marker_color=hex_number,opacity=0.50,legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=3,col=1)
			fig.add_trace(go.Histogram(x=df["vsize"],nbinsx=20,bingroup=2,marker_color=hex_number,opacity=0.50,legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=3,col=2)
			fig.add_trace(go.Histogram(x=df["time"],nbinsx=20,bingroup=3,marker_color=hex_number,opacity=0.50,legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=3,col=3)
			max_rss.append("{0}({1})".format(df['rss'].max(),df['event'][df['rss'].idxmax()]))
			max_vsize.append("{0}({1})".format(df['vsize'].max(),df['event'][df['vsize'].idxmax()]))
			max_time.append("{0}({1})".format(df['time'].max(),df['event'][df['time'].idxmax()]))
			avrg_time.append(str(round(df['time'].sum()/len(df['time']),4)))

		fig.add_trace(go.Table(header=dict(values=['VERSION', '(RSS)MaxMemory(evt)','(VSIZE)MaxMemory(evt)','AverageTime','MaxTime(evt)']),
			cells=dict(height=30,values=[version,max_rss,max_vsize,avrg_time,max_time])),
			row=1,col=1)

		fig.update_layout(barmode='overlay')
		fig.update_layout(
		        height=1500,
		        width=1500,
		        title={
		        'text':"Summary of Time and Memory test : {0}_X_{1}".format(version,step),
		        'x':0.5,
		        'y':0.98,
		        'xanchor':'center',
		        'yanchor':'top',
		        'font':dict(size=20)},
		        legend=dict(
		        orientation="h",
		        yanchor="bottom",
		        y=0.78,
		        xanchor="right",
		        x=1
		))

		fig.update_xaxes(title_text="ith event",row=2,col=1)
		fig.update_xaxes(title_text="ith event",row=2,col=2)
		fig.update_xaxes(title_text="ith event",row=2,col=3)
		fig.update_xaxes(title_text="Memory(MB)",row=3,col=1)
		fig.update_xaxes(title_text="Memory(MB)",row=3,col=2)
		fig.update_xaxes(title_text="Time(s)",row=3,col=3)
		
		fig.update_yaxes(title_text="Memory(MB)",row=2,col=1)
		fig.update_yaxes(title_text="Memory(MB)",row=2,col=2)
		fig.update_yaxes(title_text="Time(s)",type="log",row=2,col=3)
		fig.update_yaxes(title_text="Number of events",row=3,col=1)
		fig.update_yaxes(title_text="Number of events",row=3,col=2)
		fig.update_yaxes(title_text="Number of events",row=3,col=3)


		io.write_html(fig,"{0}_{1}_{2}.html".format(version,step,workflow))
