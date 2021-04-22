import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as io
import pandas as pd
import numpy as np
import sys

target_cmssw = sys.argv[1]
refer_cmssw = target_cmssw[:-1]+str(int(target_cmssw[-1])-1)
step = sys.argv[2]
data = sys.argv[3]

if len(sys.argv)==4:
	target_df = pd.read_csv("/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/comp_igprof/{0}_step{1}_{2}.csv".format(target_cmssw,step,data))
	refer_df = pd.read_csv("/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/comp_igprof/{0}_step{1}_{2}.csv".format(refer_cmssw,step,data))
	html_name = "comp_igprof/html/{0}vs{1}_step{2}_{3}.html".format(target_cmssw,refer_cmssw,step,data)
	main_title="Igprof_{3} Comaprison : {0} VS {1} (Step {2})".format(target_cmssw,refer_cmssw,step,data)
else:
	target_df = pd.read_csv("/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/comp_igprof/{0}_step{1}_{2}.{3}.csv".format(target_cmssw,step,data,sys.argv[4]))
	refer_df = pd.read_csv("/eos/user/b/btae/www/Service_Work/test/cms-reco-profiling-web/comp_igprof/{0}_step{1}_{2}.{3}.csv".format(refer_cmssw,step,data,sys.argv[4]))
	html_name = "comp_igprof/html/{0}vs{1}_step{2}_{3}.{4}.html".format(target_cmssw,refer_cmssw,step,data,sys.argv[4])
	main_title="Igprof_{3}.{4} Comaprison : {0} VS {1} (Step {2})".format(target_cmssw,refer_cmssw,step,data,sys.argv[4])

target_df.columns=["name","target_cumulative","target_pct","targe_spontaneous"]
refer_df.columns=["name","refer_cumulative","refer_pct","refer_spontaneous"]

target_df = target_df.rename_axis('target_rank').reset_index()
refer_df = refer_df.rename_axis('refer_rank').reset_index()

merged_df = pd.merge(target_df,refer_df,left_on='name',right_on='name',how='inner')
merged_df["Delta"] = (merged_df.apply(lambda x: (x.target_cumulative-x.refer_cumulative)/x.refer_spontaneous, axis='columns')*100).round(2).astype(str)+'%'
merged_df['name'] = merged_df['name'].str.split('>,',n=1,expand=True)[0]+ " ..."


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
    header=dict(values=list(["index","<b>Rank(New)</b>","<b>Rank(Old)</b>","<b>Percent(New)</b>","<b>Percent(Old)</b>","<b>Cumulative(New)</b>","<b>Cumulative(Old)</b>","<b>Delta</b>","<b>name</b>"]),
                fill_color=['black','#4b778d','#28b5b5','#4b778d','#28b5b5','#4b778d','#28b5b5','#194350','#194350'],
		height = 40,
		font=dict(color='white',size=12),
                align='center'),
    cells=dict(values=[merged_df.index,merged_df.target_rank,merged_df.refer_rank,merged_df.target_pct,merged_df.refer_pct,merged_df.target_cumulative,merged_df.refer_cumulative,merged_df.Delta,merged_df.name],
               fill_color='white',
		font=dict(color='black',size=12),
		height = 20,
                align=['center','center','center','right','right','right','right','right','left'])),
		row=1,col=1
)

fig.add_trace(go.Bar(name="old",x=merged_df.index[:50],y=merged_df.target_cumulative[:50]),
		row=2,col=1
)

fig.add_trace(go.Bar(name="new",x=merged_df.index[:50],y=merged_df.refer_cumulative[:50]),
		row=2,col=1
)

fig.update_layout(
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
