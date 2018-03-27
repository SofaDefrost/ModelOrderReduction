## Usage: python convertRIDinActiveNodes RIDfilename connectivityFilename keyword

import math
from sys import argv

#listActiveNodesFilename = "listActiveNodes_Diamond.txt"
#listActiveNodesFilename = "listActiveNodes_beam.txt"

def distance3D(vec1,vec2):
   norm = ((vec2[0]-vec1[0])**2 + (vec2[1]-vec1[1])**2 + (vec2[2]-vec1[2])**2)**0.5
   return norm

script, RIDfilename, connectivityFilename, keyword = argv

listActiveNodesFilename = "listActiveNodes_"+keyword+".txt"
fRID = open(RIDfilename,'r')
RIDlist = []
for line in fRID:
  lineSplit = line.split();
  RIDlist.append(int(lineSplit[0]))
fRID.close()
print RIDlist
fconnec = open(connectivityFilename,'r')
connecList = []
for line in fconnec:
  lineSplit = line.split();
  connecList.append(map(int,lineSplit))
fconnec.close()

print connecList
dimension = len(lineSplit)
listActiveNodes = []
for i in RIDlist:
   print "#######################"
   print "elem number: ", i
   for coordIndex in range(dimension):
        print connecList[i][coordIndex]
   lenStart = len(listActiveNodes)
   for coordIndex in range(dimension):
        if connecList[i][coordIndex] not in listActiveNodes:
                listActiveNodes.append(connecList[i][coordIndex])
   lenEnd = len(listActiveNodes)
   if (lenEnd - lenStart < dimension):
      print 'some nodes were already in the list !!! '



listActiveNodes.sort()
print listActiveNodes
#listActiveNodes = range(8646)
fActiveNodes = open(listActiveNodesFilename,'w')
for item in listActiveNodes:
  fActiveNodes.write("%d\n" % item)
fActiveNodes.close()
