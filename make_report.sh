igprof-analyse --sqlite -v -d -g /eos/cms/store/user/cmsbuild/profiling/data/${1}/slc7_amd64_gcc900/23434.21/step${2}_igprof${3}.gz | sed -e 's/INSERT INTO files VALUES (\([^,]*\), \"[^$]*/INSERT INTO files VALUES (\1, \"ABCD\");/g' | sqlite3 igprof_${1}_step${2}_${3}.sql3 >& ${1}_step${2}_${3}_sql.log

igprof-analyse  -v -d -g /eos/cms/store/user/cmsbuild/profiling/data/${1}/slc7_amd64_gcc900/23434.21/step${2}_igprof${3}.gz >& RES_${1}_step${2}_${3}.res
