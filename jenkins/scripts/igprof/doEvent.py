import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as io
import pandas as pd
import numpy as np
import sys
import yaml
import os

io.renderers.default = "browser"

data_path = '/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases'
cmssw = os.listdir(data_path)
cmssw.sort(key = lambda x: (x.split('_')[1:4],10-len(x.split('_')),len(x)))

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--release", type=str, help="CMSSW release", default=None)
parser.add_argument("--workflow", type=str, help="workflow", default=None)
args = parser.parse_args()

target_cmssw  = args.release
refer_cmssw = cmssw[cmssw.index(target_cmssw)-1]
workflow = args.workflow

for step in ['step3','step4','step5']:
	if not os.path.isdir("data/{0}/{1}/{2}".format(target_cmssw,workflow,step)):
		continue
	for data in ['.'.join(x.split('.')[:-1]) for x in os.listdir("data/{0}/{1}/{2}".format(target_cmssw,workflow,step))]:
		target_path = "data/{0}/{1}/{2}/{3}.csv".format(target_cmssw,workflow,step,data)
		refer_path  = "data/{0}/{1}/{2}/{3}.csv".format(refer_cmssw,workflow,step,data)
	
		if os.path.isfile(target_path) and os.path.isfile(refer_path):
	
			target_df = pd.read_csv(target_path)
			refer_df = pd.read_csv(refer_path)
			os.makedirs("{0}/{1}/{2}".format(target_cmssw,workflow,step),exist_ok=True)
			html_name = "{0}/{1}/{2}/{3}.html".format(target_cmssw,workflow,step,data)
			main_title= "Igprof_{3} Comaprison : {1} VS {0} ({2})".format(target_cmssw,refer_cmssw,step,data)
	
			target_df.columns=["name","target_cumulative","target_pct","targe_spontaneous"]
			refer_df.columns=["name","refer_cumulative","refer_pct","refer_spontaneous"]
			
			target_df = target_df.rename_axis('target_rank').reset_index()
			refer_df = refer_df.rename_axis('refer_rank').reset_index()
			
			merged_df = pd.merge(target_df,refer_df,left_on='name',right_on='name',how='inner')
			merged_df["target_cumulative"] = merged_df["target_cumulative"].round(3)
			merged_df["refer_cumulative"] = merged_df["refer_cumulative"].round(3)
			merged_df["Delta"] = (merged_df.apply(lambda x: (x.target_cumulative-x.refer_cumulative)/x.refer_spontaneous, axis='columns')*100).round(2).astype(str)+'%'
			
			print(merged_df["target_cumulative"].sum(),merged_df["refer_cumulative"].sum())
			
			fig = make_subplots(
				rows=2, cols=1,
				row_heights=[0.5,0.5],
				vertical_spacing=0.05,
				specs=[[{"type":"table"}],
				       [{"type":"xy"}]]
			)
			
			fig.add_trace(go.Table(
			    columnorder = [1,2,3,4,5,6,7,8,9],
			    columnwidth = [30,30,30,30,30,30,30,30,200],
			    header=dict(values=list(["index","Rank(Old)","Rank(New)","Percent(Old)","Percent(New)","Cumulative(Old)","Cumulative(New)","Delta","name"]),
			                fill_color=['black','#4b778d','#28b5b5','#4b778d','#28b5b5','#4b778d','#28b5b5','#194350','#194350'],
					#height = 40,
					font=dict(color='white',size=12),
			                align='center'),
			    cells=dict(values=[merged_df.index,merged_df.refer_rank,merged_df.target_rank,merged_df.refer_pct,merged_df.target_pct,merged_df.refer_cumulative,merged_df.target_cumulative,merged_df.Delta,merged_df.name])),
			        	#fill_color='white',
					#font=dict(color='black',size=12),
				       	#height = 90)),
			                #align=['center','center','center','right','right','right','right','right','left'])),
					row=1,col=1
			)
			
			fig.add_trace(go.Bar(name="old",x=merged_df.index[:50],y=merged_df.refer_cumulative[:50],hovertext=merged_df.name[:50]),
					row=2,col=1
			)
			
			fig.add_trace(go.Bar(name="new",x=merged_df.index[:50],y=merged_df.target_cumulative[:50],hovertext=merged_df.name[:50]),
					row=2,col=1
			)
			
			
			fig.update_layout(
				height=1000,
				width=2000,
				title = {
				'text':main_title,
				'x':0.5,
				'y':0.98,
			        'xanchor':'center',
			        'yanchor':'top',
			        'font':dict(size=20)},
				legend=dict(
			        orientation="h",
			        yanchor="bottom",
			        y=0.5,
			        xanchor="right",
			        x=1
			))
			
			fig.update_xaxes(title_text="index",row=2,col=1)
			fig.update_yaxes(title_text="cumulative",row=2,col=1)
			
			io.write_html(fig,html_name)
