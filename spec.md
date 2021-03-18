# Profiling webpage specification 

- data should be separated from the html in a machine readable format (json, yaml, txt which is clearly parseable) and in GitHub
- page contents should be tracked in github
- intermediate results such as SQL, compareProducts and any other derived files should be generated with a single script from the profiling outputs in eos, given the release name (e.g. `analyze.py --release CMSSW_11_3_0_pre4`)
   - it can be useful to regenerate also only a single feature for all releases (e.g. `analyze.py --feature compareProducts`)
- webpage should contain the same basic measurements as on Jiwoong's page:
   - SQL outputs: CPU, mem.1, mem.50, mem.99
   - getTimeMemorySummary
   - TimeDiff
   - CPU, MEM compare (igprof diffs)
   - compareOutProd
