#!/bin/sh
echo
echo %s_Run346979_Prompt_CosmicsPrompt
echo
echo 'START---------------'
cd /afs/cern.ch/user/f/fivone/Monika
source /cvmfs/sft.cern.ch/lcg/contrib/gcc/9.1.0/x86_64-centos7/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.18.04/x86_64-centos7-gcc48-opt/bin/thisroot.sh
ClusterId=$1
ProcId=$2
python stripHits.py --dataset 346979_Prompt_CosmicsPrompt --outputname 346979_Prompt_CosmicsPrompt 
