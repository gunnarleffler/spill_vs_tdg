#!/bin/bash
#
# wq_tools.sh
# This script is intended to run the various WQ Tools from cron
# POC: Gunnar Leffler
#      Dan Turner

. ~/.env_vars

OFFICE=nwdp
FN=wq_tools
SCRIPT_NAME="wq_tools.sh"

SOURCE=/usr/dx

FN_SOURCE=$SOURCE/$OFFICE/$FN
SCRIPT_DIR=${FN_SOURCE}/script
CNTL_LIB_DIR=$SOURCE/control/lib

export OFFICE FN

#====================================================
# load standard dc functions library
#====================================================

. $CNTL_LIB_DIR/dx_functions.sh

#====================================================
# Check if feed is activated (flag file on)
#====================================================
feed_status $OFFICE $FN "${SCRIPT_NAME}.sh" >/dev/null 2>/dev/null
if [ "$?" -ne "0" ]
then
  echo "$OFFICE $FN $SCRIPT_NAME is not configured to run on this node"
#  exit
fi

#====================================================
# Start into script
#====================================================

###################################################
# Generate Spill and TDG relationship plots
###################################################

cd $SCRIPT_DIR

find . -name "*.pyc" | xargs rm

python3 Timeseries_spill_TDG_plus_py36_v1.py

python3 Spill_v_TDG_daily_py36_v1.py

############################################################
# Calculate Washington, Oregon and Combined 12h TDG Averages
############################################################

cd $SCRIPT_DIR/12hr
python3 ./get_avgs.py -l 5 config.yml -rj > ../../data/12hr.json

############################################################
#Create overview tables
############################################################
cd $SCRIPT_DIR/12hr
jupyter nbconvert --to html --execute ./columbia.ipynb
jupyter nbconvert --to html --execute ./snake_river.ipynb

###########################################################
#create wq plot dashboard
##########################################################
cd $SCRIPT_DIR/wq_plots
python3 ./main.py snake.yml -t Snake_River
