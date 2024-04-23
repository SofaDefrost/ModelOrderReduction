# -*- coding: utf-8 -*-
"""
:code:`python convertRIDinActiveNodes RIDfilename connectivityFilename listActiveNodesFileName`
"""

from sys import argv


def convertRIDinActiveNodes(RIDFileName,connectivityFileName,listActiveNodesFileName, verbose=False ):

    print("###################################################")
    print("Executing convertRIDinActiveNodes.py\n")
    print("Arguments :\n")
    print("     INPUT  :")
    print("         -RIDFileName                :",RIDFileName)
    print("         -connectivityFileName       :",connectivityFileName)
    print("     OUTPUT :")
    print("         -listActiveNodesFileName    :",listActiveNodesFileName,'\n')
    print("###################################################")

    ##############################################################################

    fRID = open(RIDFileName,'r')
    if verbose : print("Reading file :",RIDFileName)
    fRID.readline()
    RIDlist = []
    for line in fRID:
        lineSplit = line.split();
        RIDlist.append(int(lineSplit[0]))
    fRID.close()
    #print RIDlist
    if verbose : print("Done reading file :",RIDFileName,'\n')


    fconnec = open(connectivityFileName,'r')
    if verbose : print("Reading file :",connectivityFileName)
    connecList = []
    for line in fconnec:
        lineSplit = line.split();
        connecList.append(list(map(int,lineSplit)))
    fconnec.close()
    #print connecList
    if verbose : print("Done reading file :",connectivityFileName,'\n')


    if verbose : print("Generating listActiveNodes\n")
    dimension = len(lineSplit)
    listActiveNodes = []
    for i in RIDlist:
        lenStart = len(listActiveNodes)
        for coordIndex in range(dimension):
            if connecList[i][coordIndex] not in listActiveNodes:
                    listActiveNodes.append(connecList[i][coordIndex])
        lenEnd = len(listActiveNodes)
        #if (lenEnd - lenStart < dimension and verbose):
            #print 'some nodes were already in the list !!! '


    listActiveNodes.sort()

    if verbose : print("Filling file :",listActiveNodesFileName,"\n")
    fActiveNodes = open(listActiveNodesFileName,'w')
    for item in listActiveNodes:
        fActiveNodes.write("%d\n" % item)
    fActiveNodes.close()

    if verbose :
        print("listActiveNodes :")
        print(listActiveNodes)
        print("===> Success convertRIDinActiveNodes.py\n")

    return listActiveNodes

##########################################################################################

if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 4:
        print("Function need at least 3 arguments")
    else:
        convertRIDinActiveNodes(*argv[1:])