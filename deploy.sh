#!/bin/bash
set -e

DEPLOY_DIR=/eos/project/c/cmsweb/www/reco-prof

#deploy the HTML
cp -R web $DEPLOY_DIR/
