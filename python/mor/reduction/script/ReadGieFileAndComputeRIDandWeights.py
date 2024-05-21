# -*- coding: utf-8 -*-
"""
:code:`python readGieFileAndComputeRIDandWeights.py gieFilename RIDFileName weightsFileName tol`

tol is typically between 0.1 and 0.01
"""

import numpy as np
import os , sys
from sys import argv

from mor.utility import utility as util


def errDif(G, xi, b):
    return np.linalg.norm(G.dot(xi) - b)

def etaTild(Gtilde, b):
    return np.linalg.solve( np.transpose(Gtilde).dot(Gtilde) , np.transpose(Gtilde).dot(b) )

def selectECSW(G,b,tau,verbose):
    nbLines, numElem = np.shape(G)
    ECSWindex = set([])
    xi = np.zeros((numElem,1))
    valTarget = tau*np.linalg.norm(b);
    currentValue = errDif(G,xi,b)
    marge = currentValue - valTarget

    while (currentValue > valTarget):

        if verbose :
            print ("Current Error: ", currentValue,"Target Error:", valTarget)
        else :
            util.update_progress( round( ( 100 - ((currentValue - valTarget)*100) / marge) / 100 , 4) )

        vecDiff = b - G.dot(xi)
        GT = np.transpose(G)
        mu = GT.dot(vecDiff)
        index = int(np.argmax(mu))
        ECSWindex = ECSWindex.union([index])

        Gtilde = G[:,list(ECSWindex)]
        etaTilde = etaTild(Gtilde,b)

        while ( not(all(etaTilde>0) ) ):

            ECSWindexNegative = []
            etaTildeNegative = []
            NonZero = []
            ind = 0

            #if verbose : print 'Hohohohohohohohoho !!!'

            negIndex = (etaTilde-xi[list(ECSWindex)])<0
            negIndex = list(negIndex.flatten())

            for i in negIndex:

                if (i):
                    ECSWindexNegative.append(list(ECSWindex)[ind])
                    etaTildeNegative.append(etaTilde[ind])

                ind = ind + 1

            vec1 = -xi[ECSWindexNegative]
            vec2 = (etaTildeNegative-xi[ECSWindexNegative])
            maxFeasibleStep = np.amin(vec1/vec2);
            xi[list(ECSWindex)] = xi[list(ECSWindex)] + maxFeasibleStep*(etaTilde - xi[list(ECSWindex)]);
            zeroIndex = np.absolute(xi)<1.0e-12;
            ECSWindex = set(range(numElem))

            ind = 0
            for i in zeroIndex:

                if (not i): NonZero.append(list(ECSWindex)[ind])
                ind = ind + 1

            ECSWindex = set(NonZero)

            Gtilde = G[:,list(ECSWindex)]
            etaTilde = etaTild(Gtilde,b)

        xi[list(ECSWindex)] = etaTilde

        currentValue = errDif(G,xi,b)

    if verbose :
        print ("Final Error: ", errDif(G,xi,b) ," Target Error: ", valTarget)
    else :
        u.update_progress( 1 )

    return (ECSWindex,xi)


def readGieFileAndComputeRIDandWeights(gieFilename, RIDFileName, weightsFileName, tol, verbose=False ):

    print("###################################################")
    print("Executing readGieFileAndComputeRIDandWeights.py\n")
    print("Arguments :\n")
    print("     INPUT  :")
    print("         -gieFilename    :",gieFilename)
    print("     with arguments    :")
    print("         -tolerance        :",tol,"\n")
    print("     OUTPUT :")
    print("         -RIDFileName                :",RIDFileName)
    print("         -weightsFileName            :",weightsFileName,"\n")
    print("###################################################")

    ################################################################################################

    gie = None

    #Read all the file & store it in GIE
    if verbose : print("Reading file : %r" %gieFilename)

    with open(gieFilename,'r') as fgie :
        nbLines = 0
        lenght = len(fgie.readline().split())
        fgie.seek(0)
        for i,line in enumerate(fgie):
            lineSplit = line.split()
            if lineSplit != ['0']*len(lineSplit):
                nbLines += 1

        gie=np.zeros((nbLines,lenght),dtype=np.float32)
        fgie.seek(0)

        tmp = 0
        for i,line in enumerate(fgie):
            lineSplit = line.split()
            # print(i,len(lineSplit)
            if lineSplit != ['0']*len(lineSplit):
                # print(lineSplit)
                gie[tmp,:] = lineSplit
                tmp += 1

        # np.set_printoptions(precision=5)
        # print("DONE -------------> "+str(gie[0][0]))

        if verbose :
            print("nbLines "+str(nbLines)+"  lenght "+str(lenght))
            print("Done reading file %r:" % gieFilename,'\n')


    #Create bECSW from GIE
    bECSW = np.sum(gie,axis=1)
    bECSW = bECSW[np.newaxis]
    bECSW = np.transpose(bECSW)

    ####################################
    if verbose :
        print("INFO pre-process")
        # print "     size GIE (nbLine,lenght) :   ", '('+str(nbLines)+', '+str(lenght)+')'
        print("     size cleaned GIE :               ", np.shape(gie))
        print("     size bECSW :                     ", np.shape(bECSW),'\n')
    ####################################

    #Compute RID & Weight
    ECSWindex,xi = selectECSW(gie,bECSW,tol,verbose)
    ECSWindex = np.array(sorted(list(ECSWindex)))
    sizeRID = ECSWindex.size

    #Store results in files
    np.savetxt(RIDFileName,ECSWindex, header=str(sizeRID)+' 1', comments='', fmt='%d')
    np.savetxt(weightsFileName,xi, header=str(xi.size)+' 1', comments='',fmt='%10.5f')

    if verbose: print ("===> Success readGieFileAndComputeRIDandWeights.py\n")


##########################################################################################

if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 5:
        print("Function need at least 4 arguments")
    else:
        readGieFileAndComputeRIDandWeights(*argv[1:])
