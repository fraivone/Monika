import sys
import os
import argparse
from argparse import RawTextHelpFormatter
import re as regularExpression


def generateSubFile(outputName):
    job_flavour = "tomorrow"
    SubfileName = "/afs/cern.ch/user/f/fivone/Monika/CondorSub/JobFiles/SubmitFile_"+str(outputName)+".sub"
    with open(SubfileName, 'w') as sout:
        sout.write("executable              = job_Run_"+str(outputName)+".sh"+"\n")
        sout.write("getenv                  = true"+"\n")
        sout.write("arguments               = $(ClusterId) $(ProcId)"+"\n")
        sout.write("output                  = ./Logs/out.$(ClusterId)_Run"+str(outputName)+".dat"+"\n")
        sout.write("error                   = ./Logs/error.$(ClusterId)_Run"+str(outputName)+".err"+"\n")
        sout.write("log                     = ./Logs/log.$(ClusterId)_Run"+str(outputName)+".log"+"\n")
        sout.write("+JobFlavour             = \""+job_flavour+"\" "+"\n")
        sout.write("queue"+"\n")
    return SubfileName

def generateJobShell(run_number,outputName):
    run_number_int = int(regularExpression.sub("[^0-9]", "", run_number))
    main_command = "python stripHits.py --dataset "+str(run_number)+" --outputname "+outputName       
    main_command = main_command + " \n"


    with open("./JobFiles/job_Run_"+str(outputName)+".sh", 'w') as fout:
        ####### Write the instruction for each job
        fout.write("#!/bin/sh\n")
        fout.write("echo\n")
        fout.write("echo %s_Run"+str(run_number)+"\n")
        fout.write("echo\n")
        fout.write("echo 'START---------------'\n")
        fout.write("cd /afs/cern.ch/user/f/fivone/Monika"+"\n")
        ## sourceing the right gcc version to compile the source code
        fout.write("source /cvmfs/sft.cern.ch/lcg/contrib/gcc/9.1.0/x86_64-centos7/setup.sh"+"\n")
        fout.write("source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.18.04/x86_64-centos7-gcc48-opt/bin/thisroot.sh"+"\n")
        ## Run the same job interval number of time
        fout.write("ClusterId=$1\n")
        fout.write("ProcId=$2\n")
        fout.write(main_command)
if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='''Scripts runs stripHits.py with condor''',
        epilog="""Typical exectuion (TO BE RUN IN THIS FOLDER)\n\t  python runJobs.py --dataset_list 346979_Prompt_CosmicsPrompt --outputNames 346979_Prompt_CosmicsPrompt""",
        formatter_class=RawTextHelpFormatter
        )


    parser.add_argument('--dataset_list', type=str , help="List of the runs to be analyzed (make sure they're  ntuplized)",required=True,nargs='*')
    parser.add_argument('--outputNames', type=str , help="List of output names",required=True,nargs='*')

    args = parser.parse_args()
    inputs = args.dataset_list
    outputs = args.outputNames
    
    if len(inputs) != len(outputs):
        print "Parsed runList and outputNames are different in number...\nExiting .."
        sys.exit(0)    

    for index in range(len(inputs)):
        run = inputs[index]
        name = outputs[index]
        
        SubfileName = generateSubFile(name)
        generateJobShell(run,name)
        os.chdir("./JobFiles/")
        os.system("condor_submit "+SubfileName)
        os.chdir("../")
