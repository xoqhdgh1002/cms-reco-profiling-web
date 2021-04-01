#!/bin/bash
set -e

DEPLOY_DIR=/eos/project/c/cmsweb/www/reco-prof
DATA_DIR=/eos/cms/store/user/cmsbuild/profiling
IGPROF_COMMIT=03d16c15bd970256affcfde9e510a8404856b233
CIRCLES_COMMIT=f5321bf6352caeecc681c877dea473e5a61d647f

#Deploy igprof navigator
[ ! -d ${DEPLOY_DIR}/cgi-bin ] && mkdir ${DEPLOY_DIR}/cgi-bin
[ ! -d ${DEPLOY_DIR}/cgi-bin/data ] && mkdir ${DEPLOY_DIR}/cgi-bin/data
wget https://raw.githubusercontent.com/igprof/igprof/${IGPROF_COMMIT}/src/igprof-navigator -O ${DEPLOY_DIR}/cgi-bin/igprof-navigator
chmod +x ${DEPLOY_DIR}/cgi-bin/igprof-navigator

#Deploy circles
wget https://github.com/fwyzard/circles/archive/${CIRCLES_COMMIT}.zip -O circles.zip
rm -Rf ${DEPLOY_DIR}/circles
unzip circles.zip
mv circles-${CIRCLES_COMMIT}/web ${DEPLOY_DIR}/circles
rm -Rf circles-${CIRCLES_COMMIT}
rm circles.zip

rm -Rf ${DEPLOY_DIR}/circles/data
ln -s ${DATA_DIR}/data ${DEPLOY_DIR}/circles/data
