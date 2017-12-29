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
# script, RIDfilename, connectivityFilename, nbOfMode = argv

print "Executing readGieFileAndComputeRIDandWeights.py\n"

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("../config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
  
connectivityFilename =          cfg['connectivityFilename']
pathToWeightsAndRIDdir =        cfg['weightsAndRID']['pathTodir']
RIDFileName =                   cfg['weightsAndRID']['RIDFileName']
nbModes =                       cfg['robotParam']['nbModes']   
listActiveNodesFileName =       cfg['listActiveNodesFileName']

verbose = cfg['other']['verbose']

print "readGieFileAndComputeRIDandWeights arguments :"
print "     input pathToWeightsAndRIDdir    :",pathToWeightsAndRIDdir
print "         -RIDFileName                :",RIDFileName
print "         -connectivityFilename       :",connectivityFilename
print "         with nbModes of :",nbModes
print "     output pathToWeightsAndRIDdir   :",pathToWeightsAndRIDdir
print "         -listActiveNodesFileName    :",listActiveNodesFileName,"\n"

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


fconnec = open(pathToWeightsAndRIDdir+connectivityFilename,'r')
if verbose : print "Reading file :",connectivityFilename
connecList = []
for line in fconnec:
    lineSplit = line.split();
    connecList.append(map(int,lineSplit))
fconnec.close()
#print connecList
if verbose : print "Done reading file :",connectivityFilename,'\n'


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

print "===> Success convertRIDinActiveNodes.py\n"
