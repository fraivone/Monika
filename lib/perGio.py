from THR_Utils import * 
from PFA_Analyzer_Utils import *

print "P5_Position\tOverallTHR"
for re in [-1,1]:
    for ch in range(1,37):
        for la in [1,2]:
            ChamberID = ReChLa2chamberName(re,ch,la)
            OverallTHR = GetOverallChamberThreshold("/afs/cern.ch/user/f/fivone/Test/PFA_Analyzer/THR_Data/THR_ARM_DAC/SBit100_Trimming",ChamberID,verbose=True)
            print ChamberID,'\t',OverallTHR
