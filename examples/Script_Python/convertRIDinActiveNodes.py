## Usage: python convertRIDinActiveNodes argv[1] argv[2] argv[3]  
##
##               arg1 = RIDfilename             ->  Path to the Reduced Integration Domain file
##               arg2 = connectivityFilename    ->  ????
##               arg3 = nbOfMode                ->  Number of Mode

import yaml
import math
import numpy as np
import code #   ???

# from sys import argv
# script, RIDfilename, connectivityFileName, nbOfMode = argv

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
  
connectivityFileName =          cfg['connectivityFileName']
pathToWeightsAndRIDdir =        cfg['weightsAndRID']['pathTodir']
RIDFileName =                   cfg['weightsAndRID']['RIDFileName']  
listActiveNodesFileName =       cfg['listActiveNodesFileName']

verbose = cfg['other']['verbose']

print "###################################################"
print "Executing readGieFileAndComputeRIDandWeights.py\n"
print "Arguments :\n"
print "     INPUT  :"
print "     in pathToWeightsAndRIDdir    :",pathToWeightsAndRIDdir
print "         -RIDFileName                :",RIDFileName
print "         -connectivityFileName       :",connectivityFileName
print "     OUTPUT :"
print "     in pathToWeightsAndRIDdir    :",pathToWeightsAndRIDdir
print "         -listActiveNodesFileName    :",listActiveNodesFileName,"\n"
print "###################################################"

################################################################################################

def distance3D(vec1,vec2):
   norm = ((vec2[0]-vec1[0])**2 + (vec2[1]-vec1[1])**2 + (vec2[2]-vec1[2])**2)**0.5
   return norm


fRID = open(pathToWeightsAndRIDdir+RIDFileName,'r')
if verbose : print "Reading file :",RIDFileName
RIDlist = []
for line in fRID:
    lineSplit = line.split();
    RIDlist.append(int(lineSplit[0]))
fRID.close()
#print RIDlist
if verbose : print "Done reading file :",RIDFileName,'\n'


fconnec = open(pathToWeightsAndRIDdir+connectivityFileName,'r')
if verbose : print "Reading file :",connectivityFileName
connecList = []
for line in fconnec:
    lineSplit = line.split();
    connecList.append(map(int,lineSplit))
fconnec.close()
#print connecList
if verbose : print "Done reading file :",connectivityFileName,'\n'


if verbose : print "Generating listActiveNodes\n"
dimension = len(lineSplit)
listActiveNodes = []
for i in RIDlist:
    #if verbose :
        # print "#######################"
        # print "elem number: ", i
        # for coordIndex in range(dimension):
        #     print connecList[i][coordIndex]
    lenStart = len(listActiveNodes)
    for coordIndex in range(dimension):
        if connecList[i][coordIndex] not in listActiveNodes:
                listActiveNodes.append(connecList[i][coordIndex])
    lenEnd = len(listActiveNodes)
    #if (lenEnd - lenStart < dimension and verbose):
        #print 'some nodes were already in the list !!! '


listActiveNodes.sort()

print "listActiveNodes :"
print listActiveNodes

if verbose : print "Filling file :",listActiveNodesFileName,"\n"
fActiveNodes = open(pathToWeightsAndRIDdir+listActiveNodesFileName,'w')
for item in listActiveNodes:
    fActiveNodes.write("%d\n" % item)
fActiveNodes.close()

if cfg['ECSWBool']['prepare'] == "true" and cfg['ECSWBool']['perform'] == "false":
    cfg['ECSWBool']['prepare'] = "false"
    cfg['ECSWBool']['perform'] = "true"
    with open("config.yml", "w") as f:
        yaml.dump(cfg, f)

print "===> Success convertRIDinActiveNodes.py\n"
