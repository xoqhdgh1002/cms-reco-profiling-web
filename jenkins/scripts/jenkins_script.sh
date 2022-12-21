env
pwd
ls -al

#from https://github.com/cms-sw/cms-bot/blob/master/run-ib-testbase.sh
klist || true
kinit -R || true
hostname
cvmfs_config probe || true
voms-proxy-init -voms cms || true
export PYTHONUNBUFFERED=1
export ARCHITECTURE=${ARCHITECTURE}
export SCRAM_ARCH=${ARCHITECTURE}
export RELEASE_FORMAT=${RELEASE_FORMAT}
export LC_ALL=C

#Do NOT use the local jenkins worker python environment
export PYTHONPATH=
export PYTHON3PATH=

source /cvmfs/cms-ib.cern.ch/latest/cmsset_default.sh

ARCHITECTURE=$(curl -s -L https://raw.githubusercontent.com/cms-sw/cms-bot/master/releases.map | grep "$RELEASE_FORMAT;" | grep 'prodarch=1;' | sed 's|.*architecture=||;s|;.*||')
if [ "$ARCHITECTURE" = "" ] ; then
  echo "ERROR: unable to find production architecture for release $RELEASE_FORMAT"
  exit 1
fi

export ARCHITECTURE
export SCRAM_ARCH=$ARCHITECTURE


#create run.sh script that will be called via singularity
echo "#!/bin/bash
set -e
set -x

#Install extra dependencies in the local environment only (not for everyone), and add to python path
python3 -m pip install --target local plotly
export PYTHONPATH=`pwd`/local:${PYTHONPATH}
export PYTHON3PATH=`pwd`/local:${PYTHON3PATH}

source /cvmfs/cms-ib.cern.ch/latest/cmsset_default.sh
cmsrel $RELEASE_FORMAT
cd $RELEASE_FORMAT
pwd
cmsenv
cd ..

#xrdfs root mkdir /eos/cms/store/user/cmsbuild/profiling/data/hi

env | grep PYTHON

git clone -b bongho https://github.com/xoqhdgh1002/cms-reco-profiling-web
cd cms-reco-profiling-web/jenkins/scripts

cd pre-environment/
python3 make_jenkins_env.py

cd ../
python3 make_RES.py --release ${RELEASE_FORMAT} --architecture ${ARCHITECTURE} --workflow $WORKFLOW

cd summary

python3 make_get_time_memory_summary.py --release ${RELEASE_FORMAT} --architecture ${ARCHITECTURE} --workflow $WORKFLOW
xrdcopy --force --posc -v -p -r step*.txt root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/Time_Mem_Summary/${RELEASE_FORMAT}/${ARCHITECTURE}/${WORKFLOW}
python3 make_summary_plot.py --release ${RELEASE_FORMAT} --workflow $WORKFLOW
xrdcopy --force --posc -v -p -r *.html root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/summary_plot_html/

if [ "$WORKFLOW" != "140.56" ] && [ "$WORKFLOW" != "159.03" ]; then
if [ "$WORKFLOW" != "136.889" ]; then

# TW BUILD: updated Sep. 14
  cd ..
  python3 eventsize_batch.py --release ${RELEASE_FORMAT} --architecture ${ARCHITECTURE} --workflow $WORKFLOW
  xrdcopy --force --posc -v -p -r *.json root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/circles/web/data/

  python3 make_eventsize_hist.py
  python3 draw_eventsize.py ${RELEASE_FORMAT} $WORKFLOW
  xrdcopy --force --posc -v -p -r *.png root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/circles/web/hist/

#run igprof-analyse
  git clone https://github.com/xoqhdgh1002/cms-reco-profiling
  cd cms-reco-profiling
  python3 main.py --profile-data /eos/cms/store/user/cmsbuild/profiling/data/ --releases ${RELEASE_FORMAT} --workflows $WORKFLOW --igprof
  ls
  cd ..

#copy the output to the EOS webdir
  xrdcopy --force --posc -v -p -r cms-reco-profiling/out.md root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/jenkins/${BUILD_ID}/
  xrdcopy --force --posc -v -p -r cms-reco-profiling/out.yaml root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/jenkins/${BUILD_ID}/
  xrdcopy --force --posc -v -p -r cms-reco-profiling/results/igprof/${RELEASE_FORMAT} root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/


  cd igprof
  python3 make_igprof_data.py --release ${RELEASE_FORMAT} --workflow $WORKFLOW
  python3 doEvent.py --release ${RELEASE_FORMAT} --workflow $WORKFLOW
  xrdcopy --force --posc -v -p -r ${RELEASE_FORMAT} root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/comp_igprof/html/

fi

cd ../comparison
python3 make_compare_data.py --operator N03_timeDiffFromReport.sh --release ${RELEASE_FORMAT} --workflow $WORKFLOW
xrdcopy --force --posc -v -p -r ${RELEASE_FORMAT} root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/TimeDiff/
python3 make_compare_data.py --operator N04_compareProducts.sh --release ${RELEASE_FORMAT} --workflow $WORKFLOW
xrdcopy --force --posc -v -p -r ${RELEASE_FORMAT} root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/results/CompProd/

fi

#DY BUILD
cd ../
python3 make_webpage.py > index.html
xrdcopy --force --posc -v -p -r index.html root://eosuser.cern.ch//eos/project/c/cmsweb/www/reco-prof/web/

" > run.sh

cat run.sh

#Now actually run the script in the singularity image with the correct architecture
chmod +x run.sh
$CMSSW_ENVIRONMENT --command-to-run ./run.sh
