#!/bin/bash

if [ ${1} == "0" ]; then
	igprof-analyse -v -d -g ${2} >& ${3}
elif [ ${1} == "1" ]; then
	igprof-analyse  -v --demangle --gdb -r MEM_LIVE ${2} >& ${3}
fi
