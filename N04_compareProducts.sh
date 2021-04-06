#!/bin/bash

## This code analyzing branch size of step3 output root files
## The CMSSW enviroment is needed

#export SCRAM_ARCH=slc7_amd64_gcc900
#export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
#source $VO_CMS_SW_DIR/cmsset_default.sh
#cd $VO_CMS_SW_DIR/$SCRAM_ARCH/cms/cmssw/$2/src
#cmsenv
#cd -

old="/eos/cms/store/user/cmsbuild/profiling/data/$1/slc7_amd64_gcc900/23434.21/step${3}.root.unused"
new="/eos/cms/store/user/cmsbuild/profiling/data/$2/slc7_amd64_gcc900/23434.21/step${3}.root.unused"

fA=`echo $old`
if [ ! -f "${fA}" ]; then
    echo ${fA} does not exist
    exit 17
fi

fB=`echo $new`
if [ ! -f "${fB}" ]; then
    echo ${fB} does not exist
    exit 17
fi

procF=$4
if [ "x${procF}" == "x" ]; then
    procF="_RECO"
fi

absMin=$5
if [ "x${absMin}" == "x" ]; then
    absMin=100
fi
dptMin=$6
if [ "x${dptMin}" == "x" ]; then
    dptMin=20
fi

if [ $3 == 3 ]; then
	echo "Checking process ${procF} ${fA} and ${fB} (if above ${absMin} or ${dptMin}%):"
else
	echo "Checking process _PAT  ${fA} and ${fB}:"
fi

ds=`date -u +%s.%N`
os=os.${ds}
edmEventSize -v ${fA} > ${os}

ns=ns.${ds}
edmEventSize -v ${fB} > ${ns}

grep "_RECO\|_PAT" ${os} ${ns} | sed -e "s/${os}:/os /g;s/${ns}:/ns /g" | absMin=${absMin} dptMin=${dptMin} awk -f compareProducts.awk > temp.csv
python compareProd.py 

rm ${os} ${ns}
rm temp.csv
