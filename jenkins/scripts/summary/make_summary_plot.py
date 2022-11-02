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
import os
import argparse

DATA_DIR = '/eos/cms/store/user/cmsbuild/profiling/data/'

parser = argparse.ArgumentParser()
parser.add_argument("--profile-data", type=str, default=DATA_DIR, help="profiling data location")
parser.add_argument("--release", type=str, help="CMSSW release", default=None)
parser.add_argument("--architecture", type=str, help="architecture for release", default=None)
parser.add_argument("--workflow", type=str, help="workflow", default=None)
args = parser.parse_args()

release = args.release
architecture = args.architecture
workflow = args.workflow

log_object = Log_check.TimeMem()

subplot_title=["Summary Table", "(RSS)Memory Profile", "(VSIZE)Memory Profile", "average CPU Time Profile", "(RSS)Memory Profile", "(VSIZE)Memory Profile", "CPU Time Profile"]

version = '_'.join(release.split('_')[:3])

if workflow == "140.56" or workflow == "159.03":
	steps = ['step2','step3','step4','step5']
else:
	steps = ['step3','step4','step5']

for step in steps:

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

	cmssw_version = []

	for cmssw in [x for x in os.listdir(DATA_DIR) if version in x]:

		architecture = os.listdir(os.path.join(DATA_DIR,cmssw))[0]
		path = os.path.join(DATA_DIR,cmssw,architecture,workflow,'{}_TimeMemoryInfo.log'.format(step))
		if not os.path.isfile(path):
			continue
		df = log_object.Get_TimeMem(path)
		hex_number = '#'+str(hex(random.randint(0,16777215)))[2:].zfill(6)
		x_axis = np.arange(len(df))

		fig.add_trace(go.Scatter(x=x_axis,y=df["rss"],mode="lines",line=dict(color=hex_number,width=1),legendgroup=cmssw,hovertext=cmssw,name=cmssw),row=2,col=1)
		fig.add_trace(go.Scatter(x=x_axis,y=df["vsize"],mode="lines",line=dict(color=hex_number,width=1),legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=2,col=2)
		fig.add_trace(go.Scatter(x=x_axis,y=df["time"],mode="lines",line=dict(color=hex_number,width=1),legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=2,col=3)
		fig.add_trace(go.Histogram(x=df["rss"],nbinsx=20,bingroup=1,marker_color=hex_number,opacity=0.50,legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=3,col=1)
		fig.add_trace(go.Histogram(x=df["vsize"],nbinsx=20,bingroup=2,marker_color=hex_number,opacity=0.50,legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=3,col=2)
		fig.add_trace(go.Histogram(x=df["time"],nbinsx=20,bingroup=3,marker_color=hex_number,opacity=0.50,legendgroup=cmssw,hovertext=cmssw,name=cmssw,showlegend=False),row=3,col=3)
		max_rss.append("{0}({1})".format(df['rss'].max(),df['event'][df['rss'].idxmax()]))
		max_vsize.append("{0}({1})".format(df['vsize'].max(),df['event'][df['vsize'].idxmax()]))
		max_time.append("{0}({1})".format(df['time'].max(),df['event'][df['time'].idxmax()]))
		avrg_time.append(str(round(df['time'].sum()/len(df['time']),4)))
		cmssw_version.append(cmssw)

	if len(cmssw_version) == 0:
		continue

	fig.add_trace(go.Table(header=dict(values=['VERSION', '(RSS)MaxMemory(evt)','(VSIZE)MaxMemory(evt)','AverageTime','MaxTime(evt)']),
		cells=dict(height=30,values=[cmssw_version,max_rss,max_vsize,avrg_time,max_time])),
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

	output = "{0}_{1}_{2}.html".format(version,step,workflow)
	io.write_html(fig,output)
