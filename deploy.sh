#!/bin/bash
set -e

DEPLOY_DIR=/eos/project/c/cmsweb/www/reco-prof

#deploy the HTML
cp -R web $DEPLOY_DIR/

#Deploy igprof navigator
[ ! -d $DEPLOY_DIR/cgi-bin ] && mkdir $DEPLOY_DIR/cgi-bin
[ ! -d $DEPLOY_DIR/cgi-bin/data ] && mkdir $DEPLOY_DIR/cgi-bin/data
wget https://raw.githubusercontent.com/cms-externals/igprof/51fbb32/src/igprof-navigator -O $DEPLOY_DIR/cgi-bin/igprof-navigator
chmod +x $DEPLOY_DIR/cgi-bin/igprof-navigator

#Deploy circles
