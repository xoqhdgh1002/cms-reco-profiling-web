from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as io
import sys
import Log_check 
import pandas as pd
import numpy as np
cmssw = [sys.argv[1][:-1]+str(x+1) for x in range(int(sys.argv[1][-1]))]
old_cmssw = sys.argv[1].split("_")
old_cmssw[2] = str(int(old_cmssw[2])-1)
del old_cmssw[-1]
cmssw.insert(0,"_".join(old_cmssw))

log_object = Log_check.TimeMem()
subplot_title=["Summary Table", "(RSS)Memory Profile", "(VSIZE)Memory Profile", "average CPU Time Profile", "(RSS)Memory Profile", "(VSIZE)Memory Profile", "CPU Time Profile"]

max_rss=[]
max_vsize=[]
max_time=[]
avrg_time=[]

fig = make_subplots(rows=3, cols=3, 
	row_heights=[0.2,0.4,0.4],
	subplot_titles=subplot_title, 
	start_cell="top-left",
	vertical_spacing=0.1,
	specs=[[{"colspan":3,"type":"table"},None,None],
		[{},{},{}],
		[{},{},{}]]
)

colors=["#000000","#6600CC","#FFCC00","#CC0000","#00FF00","#65000B"]

for i in range(len(cmssw)):
	path="/eos/cms/store/user/cmsbuild/profiling/data/"+cmssw[i]+"/slc7_amd64_gcc900/23434.21/step"+sys.argv[2]+"_TimeMemoryInfo.log"
	df = log_object.Get_TimeMem(path)

	fig.add_trace(go.Scatter(x=df["event"],y=df["rss"],mode="lines",line=dict(color=colors[i]),legendgroup="group"+str(i),name=cmssw[i]),row=2,col=1)
	fig.add_trace(go.Scatter(x=df["event"],y=df["vsize"],mode="lines",line=dict(color=colors[i]),legendgroup="group"+str(i),name=cmssw[i],showlegend=False),row=2,col=2)
	fig.add_trace(go.Scatter(x=df["event"],y=df["time"],mode="lines",line=dict(color=colors[i]),legendgroup="group"+str(i),name=cmssw[i],showlegend=False),row=2,col=3)
	fig.add_trace(go.Histogram(x=df["rss"],nbinsx=20,bingroup=1,marker_color=colors[i],opacity=0.50,legendgroup="group"+str(i),name=cmssw[i],showlegend=False),row=3,col=1)
	fig.add_trace(go.Histogram(x=df["vsize"],nbinsx=20,bingroup=2,marker_color=colors[i],opacity=0.50,legendgroup="group"+str(i),name=cmssw[i],showlegend=False),row=3,col=2)
	fig.add_trace(go.Histogram(x=df["time"],nbinsx=20,bingroup=3,marker_color=colors[i],opacity=0.50,legendgroup="group"+str(i),name=cmssw[i],showlegend=False),row=3,col=3)

	max_rss.append("{0}({1})".format(df['rss'].max(),df['event'][df['rss'].idxmax()]))
	max_vsize.append("{0}({1})".format(df['vsize'].max(),df['event'][df['vsize'].idxmax()]))
	max_time.append("{0}({1})".format(df['time'].max(),df['event'][df['time'].idxmax()]))
	avrg_time.append(str(df['time'].sum()/len(df['time'])))

fig.add_trace(go.Table(header=dict(values=['VERSION', '(RSS)MaxMemory(evt)','(VSIZE)MaxMemory(evt)','AverageTime','MaxTime(evt)']),
		cells=dict(height=30,values=[cmssw,max_rss,max_vsize,avrg_time,max_time])),
		row=1,col=1)

fig.update_layout(barmode='overlay')
fig.update_layout(
	height=1500,
	width=1500,
	title={
	'text':"Summary of Time and Memory test : "+sys.argv[1][:-1]+"X",
	'x':0.5,
	'y':0.98,
	'xanchor':'center',
	'yanchor':'top',
	'font':dict(size=20)},
	legend=dict(
	orientation="h",
	yanchor="bottom",
	y=1.02,
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
fig.update_yaxes(title_text="Time(s)",row=2,col=3)
fig.update_yaxes(title_text="Number of events",row=3,col=1)
fig.update_yaxes(title_text="Number of events",row=3,col=2)
fig.update_yaxes(title_text="Number of events",row=3,col=3)

io.write_html(fig,sys.argv[1][:-1]+"X_step"+sys.argv[2]+".html")
