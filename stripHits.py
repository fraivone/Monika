import ROOT
import time
import re as regularExpression
import argparse
from argparse import RawTextHelpFormatter
import sys
from lib.ROOT_Utils import *
from lib.PFA_Analyzer_Utils import *


parser = argparse.ArgumentParser(
        description='''Scripts that: \n\t-Reads the GEMMuonNtuple\n\t-Plot Sanity Checks\n\t-Plot Residuals (takes the cut as parameter)\n\t-Plot efficiency\nCurrently allows the hits matching on glb_phi and glb_rdphi''',
        epilog="""Typical exectuion\n\t python stripHits.py  --dataset 344679_Prompt""",
        formatter_class=RawTextHelpFormatter
)

parser.add_argument('--verbose', default=False, action='store_true',help="Verbose printing",required=False)
parser.add_argument('--dataset','-ds', type=str,help="TAG to the folder containing the NTuples to be analyzed",required=True,nargs='*')
parser.add_argument('--outputname', type=str, help="output file name",required=False)
parser.set_defaults(outputname=None)
args = parser.parse_args()
outputname = args.outputname
if outputname == None: outputname = args.dataset

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetLineScalePS(1)
if not args.verbose: ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=2001;") #suppressed everything less-than-or-equal-to kWarning



start_time = time.time()

files = []

for folder in args.dataset:
    files = files + files_in_folder(folder)

print files
THSanityChecks = {'RecHitperStrip':{}}   
                

for key in ['ML1','ML2','PL1','PL2']:
    THSanityChecks['RecHitperStrip'][key] = {}
    for ch in range(1,37):
        size = "S" if ch%2 == 1 else "L"
        chID = 'GE11-'+key[0]+'-%02d' % ch + key[1:]+"-"+size 
        THSanityChecks['RecHitperStrip'][key][ch] = ROOT.TH2F(chID,chID,384,-0.5,383.5,10,-0.5,9.5)
        THSanityChecks['RecHitperStrip'][key][ch].SetStats(0)
        THSanityChecks['RecHitperStrip'][key][ch].SetMaximum(600)
        THSanityChecks['RecHitperStrip'][key][ch].GetXaxis().SetTitle("StripNumber")
        THSanityChecks['RecHitperStrip'][key][ch].GetYaxis().SetTitle("EtaPartition")


## Chain files
chain = ROOT.TChain("muNtupleProducer/MuDPGTree")

print args.dataset, "TChaining ",len(files)," files..."
print'\n'.join(files)
print
for fl in files:
    chain.Add(fl)
## Enabling only the branches which are actually in use
# 1. Disabling them all
chain.SetBranchStatus("*",0);     

branchList=["event_eventNumber","event_lumiBlock","event_runNumber","gemRecHit_region", "gemRecHit_chamber", "gemRecHit_layer", "gemRecHit_etaPartition", "gemRecHit_firstClusterStrip", "gemRecHit_cluster_size"]
# 2. Enabling the useful ones
for b in branchList:
    chain.SetBranchStatus(b,1)


chainEntries = chain.GetEntries()
maxLS = 0
print "\n#############\nStarting\n#############"

try:
    print "Analysing run(s): \t", [int(regularExpression.sub("[^0-9]", "", i)) for i in args.dataset]
except:
    pass

print "Number of evts \t\t%.2fM\n" %(round(float(chainEntries)/10**6,2))

for chain_index,evt in enumerate(chain):
    
    if chain_index % 40000 ==0:
        print "[",time.strftime("%B %d - %H:%M:%S"),"]\t",round(float(chain_index)/float(chainEntries),3)*100,"%"
        
    n_gemrec = len(evt.gemRecHit_chamber)
    
    RecHit_Dict = {}
    for RecHit_index in range(0,n_gemrec):
        region = evt.gemRecHit_region[RecHit_index]
        chamber = evt.gemRecHit_chamber[RecHit_index]
        layer = evt.gemRecHit_layer[RecHit_index]
        etaP = evt.gemRecHit_etaPartition[RecHit_index]
        RecHitEtaPartitionID =  region*(100*chamber+10*layer+etaP)
        endcapKey = EndcapLayer2label(region,layer)
        chamberID = ReChLa2chamberName(region,chamber,layer)

        RecHit_Dict.setdefault(RecHitEtaPartitionID, {'firstStrip':[],'cluster_size':[]})
        RecHit_Dict[RecHitEtaPartitionID]['firstStrip'].append(evt.gemRecHit_firstClusterStrip[RecHit_index])
        RecHit_Dict[RecHitEtaPartitionID]['cluster_size'].append(evt.gemRecHit_cluster_size[RecHit_index])

        for j in range(0,RecHit_Dict[RecHitEtaPartitionID]['cluster_size'][-1]):
            strip = RecHit_Dict[RecHitEtaPartitionID]['firstStrip'][-1] + j
            THSanityChecks['RecHitperStrip'][endcapKey][chamber].Fill(strip,etaP)


print("--- %s seconds ---" % (time.time() - start_time))


## Storing the results
# matchingFile.Write()
OutF = ROOT.TFile("./Output/"+outputname+".root","RECREATE")

for key in ['ML1','ML2','PL1','PL2']:
    for ch in range(1,37):
        writeToTFile(OutF,THSanityChecks['RecHitperStrip'][key][ch],"RecHitByStrip/"+key)

print "\n#############\nOUTPUT\n#############"
print "\tROOT_File \t"+"./Output/"+outputname+".root"