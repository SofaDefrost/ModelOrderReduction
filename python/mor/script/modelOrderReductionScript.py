# -*- coding: utf-8 -*-

import time, sys
import math
import numpy as np
import code #   ???


####	UTILITY FUNCTION	#############################

def distance3D(vec1,vec2):
   norm = ((vec2[0]-vec1[0])**2 + (vec2[1]-vec1[1])**2 + (vec2[2]-vec1[2])**2)**0.5
   return norm

def update_progress(progress):
    barLength = 50 # Modify this to change the length of the progress bar
    status = "Compute Weight&RID"
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress > 1:
        progress = 1
    block = int(round(barLength*progress))
    text = "\r[{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    if progress == 1 :
        text =  text+"\n"
    sys.stdout.write(text)
    sys.stdout.flush()

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
            print 'Current Error: ', currentValue,' Target Error: ', valTarget
        else :
            update_progress( round( ( 100 - ((currentValue - valTarget)*100) / marge) / 100 , 4) )

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
        print "Final Error: ", errDif(G,xi,b) ," Target Error: ", valTarget
    else :    
        update_progress( 1 )

    return (ECSWindex,xi)

#########################################################

class ModelOrderReductionScript():

    def __init__(self, modesFilePath, stateFilePath, pathToWeightsAndRIDdir, verbose):

        self.modesFilePath = modesFilePath
        self.stateFilePath = stateFilePath
        self.pathToWeightsAndRIDdir = pathToWeightsAndRIDdir

        self.verbose = verbose

    def readStateFilesAndComputeModes(self, stateFileName, tol, modesFileName):

        initPositionFilename = self.stateFilePath+"test_init.state" # 'init_myDiamondFairlyFine.state' #  'init_myDiamondQuiteFine.state' # 
        print "###################################################"
        print "Executing readStateFilesAndComputeModes.py\n" 
        print "Arguments :\n"
        print "     INPUT  :"
        print "     in stateFilePath         :",self.stateFilePath
        print "			-stateFileName 			 :",stateFileName
        print "     in initPositionFilename  :",initPositionFilename
        print "     with arguments           :"
        print "         -tolerance               :",tol,"\n"
        print "     OUTPUT :"
        print "     in modesFilePath         :",self.modesFilePath
        print "         -modesFileName           :",modesFileName,"\n"
        print "###################################################"
        start_time = time.time()
        x0Found = False

        #Find Init Pos
        finit = open(initPositionFilename,'r')
        if self.verbose : print "Reading file %r:" % initPositionFilename
        for line in finit:
            lineSplit = line.split();
            if (lineSplit[0] == "X0="): 
                lineFloat = map(float,lineSplit[1:])
                restPos = []
                restPos.append(lineFloat)
                restPos = np.transpose(restPos)
                x, y = np.shape(restPos)
                if self.verbose : print "    X0 FOUND : size restPos = ", x, ' ', y
                x0Found = True
                break
        finit.close()
        if self.verbose : print "Done reading file %r:" % initPositionFilename,'\n'

        #Compute Modes
        if x0Found :
            f = open(self.stateFilePath+stateFileName,'r')
            nbSnap = 0
            nbLine = 0
            snapshot = []
            snapshotV = []

            if self.verbose : print "Reading file %r:" % self.stateFilePath+stateFileName
            for line in f:
                nbLine = nbLine + 1
                lineSplit = line.split();
                if (lineSplit[0] == "X="):  
                    lineFloat = map(float,lineSplit[1:])
                    snapshot.append(lineFloat);
                if (lineSplit[0] == "V="):  
                    lineFloat = map(float,lineSplit[1:])
                    snapshotV.append(lineFloat);

            snapshot = np.transpose(snapshot)
            nbDOFs, nbSnap = np.shape(snapshot)
            snapshotDiff = np.zeros((nbDOFs,nbSnap))
            translationModes = np.zeros((nbDOFs,3))

            if self.verbose : 
                print "    Read",nbLine,"line and found",nbSnap,"snapshot with",nbDOFs,"of DOF"
                print "Done reading file %r:" % self.stateFilePath+stateFileName,'\n'

            start_time = time.time()

            for i in range(0,nbSnap):
                snapshotDiff[:,i] = snapshot[:,i] - restPos[:,0]
                          
            for i in range(0,nbDOFs/3):
                translationModes[3*i][0] = 1/math.sqrt(nbDOFs/3)
                translationModes[3*i+1][1] = 1/math.sqrt(nbDOFs/3)
                translationModes[3*i+2][2] = 1/math.sqrt(nbDOFs/3)

            U, s, V = np.linalg.svd(snapshotDiff, full_matrices=False) # 99% time execution
            sSquare = [i**2 for i in s]
            sumSVD = np.sum(sSquare)

            i = 0
            if self.verbose : 
                print "Determining number of Modes with a Tolerance of",tol

            while (np.sqrt(np.sum(sSquare[i:])/sumSVD) > tol or i==0):
                i = i+1

            nbModes = i

            np.savetxt(self.modesFilePath+modesFileName, U[:,0:nbModes], header=str(nbDOFs)+' '+str(nbModes), comments='', fmt='%10.5f')

            if self.verbose :
                print "Number of modes to reach tolerance: ", nbModes
                print "===> Success readStateFilesAndComputeModes.py\n"

            f.close()

            return nbModes

        else: 
            print "XO NOT FOUND"
            return -1

    def readGieFileAndComputeRIDandWeights(self, gieFilename, RIDFileName, weightsFileName, tol):

        print "###################################################"
        print "Executing readGieFileAndComputeRIDandWeights.py\n"
        print "Arguments :\n"
        print "     INPUT  :"
        print "     in gieFilename    :",gieFilename
        print "     with arguments    :"
        print "         -tolerance        :",tol,"\n"
        print "     OUTPUT :"
        print "     in pathToWeightsAndRIDdir :",self.pathToWeightsAndRIDdir
        print "         -RIDFileName                :",RIDFileName
        print "         -weightsFileName            :",weightsFileName,"\n"
        print "###################################################"

        ################################################################################################

        fgie = open(gieFilename,'r')
        lineCount = 0
        gie = []
        keepIndex = []

        #Read all the file & store it in GIE
        if self.verbose : print "Reading file : %r" %gieFilename
        for line in fgie:
            lineSplit = line.split();
            lineFloat = map(float,lineSplit)
            gie.append(lineFloat);
            lineCount = lineCount +1
        fgie.close()

        if self.verbose : 
            print "     File read until line", lineCount
            print "Done reading file %r:" % gieFilename,'\n'

        gie = np.array(gie)
        nbLines , nbElements = np.shape(gie)

        #Clean GIE
        for i in range(nbLines):
            if any(gie[i,:] != 0):
                keepIndex.append(i)

        #Creat bECSW from GIE
        gie = gie[keepIndex,:]
        bECSW = np.sum(gie,axis=1)
        bECSW = bECSW[np.newaxis]
        bECSW = np.transpose(bECSW)

        ####################################
        if self.verbose : 
            print "INFO pre-process"
            print "     size GIE (nbLine,nbElements) :   ", '('+str(nbLines)+', '+str(nbElements)+')'
            print "     size cleaned GIE :               ", np.shape(gie)
            print "     size bECSW :                     ", np.shape(bECSW),'\n'
        ####################################

        #Compute RID & Weight
        ECSWindex,xi = selectECSW(gie,bECSW,tol,self.verbose)
        ECSWindex = np.array(sorted(list(ECSWindex)))
        sizeRID = ECSWindex.size
        nbElements = xi.size

        #Store results in files 
        np.savetxt(self.pathToWeightsAndRIDdir+RIDFileName,ECSWindex, header=str(sizeRID)+' 1', comments='', fmt='%d')
        np.savetxt(self.pathToWeightsAndRIDdir+weightsFileName,xi, header=str(nbElements)+' 1', comments='',fmt='%10.5f')

        if self.verbose: print "===> Success readGieFileAndComputeRIDandWeights.py\n"

    def convertRIDinActiveNodes(self, RIDFileName,connectivityFileName,listActiveNodesFileName):

        print "###################################################"
        print "Executing convertRIDinActiveNodes.py\n"
        print "Arguments :\n"
        print "     INPUT  :"
        print "     in pathToWeightsAndRIDdir    :",self.pathToWeightsAndRIDdir
        print "         -RIDFileName                :",RIDFileName
        print "         -connectivityFileName       :",connectivityFileName
        print "     OUTPUT :"
        print "     in pathToWeightsAndRIDdir    :",self.pathToWeightsAndRIDdir
        print "         -listActiveNodesFileName    :",listActiveNodesFileName,"\n"
        print "###################################################"

        ##############################################################################

        fRID = open(self.pathToWeightsAndRIDdir+RIDFileName,'r')
        if self.verbose : print "Reading file :",RIDFileName
        RIDlist = []
        for line in fRID:
            lineSplit = line.split();
            RIDlist.append(int(lineSplit[0]))
        fRID.close()
        #print RIDlist
        if self.verbose : print "Done reading file :",RIDFileName,'\n'


        fconnec = open(self.pathToWeightsAndRIDdir+connectivityFileName,'r')
        if self.verbose : print "Reading file :",connectivityFileName
        connecList = []
        for line in fconnec:
            lineSplit = line.split();
            connecList.append(map(int,lineSplit))
        fconnec.close()
        #print connecList
        if self.verbose : print "Done reading file :",connectivityFileName,'\n'


        if self.verbose : print "Generating listActiveNodes\n"
        dimension = len(lineSplit)
        listActiveNodes = []
        for i in RIDlist:
            #if self.verbose :
                # print "#######################"
                # print "elem number: ", i
                # for coordIndex in range(dimension):
                #     print connecList[i][coordIndex]
            lenStart = len(listActiveNodes)
            for coordIndex in range(dimension):
                if connecList[i][coordIndex] not in listActiveNodes:
                        listActiveNodes.append(connecList[i][coordIndex])
            lenEnd = len(listActiveNodes)
            #if (lenEnd - lenStart < dimension and self.verbose):
                #print 'some nodes were already in the list !!! '


        listActiveNodes.sort()

        if self.verbose : print "Filling file :",listActiveNodesFileName,"\n"
        fActiveNodes = open(self.pathToWeightsAndRIDdir+listActiveNodesFileName,'w')
        for item in listActiveNodes:
            fActiveNodes.write("%d\n" % item)
        fActiveNodes.close()

        if self.verbose :
            print "listActiveNodes :"
            print listActiveNodes
            print "===> Success convertRIDinActiveNodes.py\n"