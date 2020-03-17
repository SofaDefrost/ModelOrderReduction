# -*- coding: utf-8 -*-

## Usage: python readLambdaFilesAndComputeNNMF.py stateFilename tol modesFilename addRigidBodyModesBOOL
import os
import math
import numpy as np
from scipy.linalg import solve
import platform

from sys import argv

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"

def readLambdaFilesAndComputeNNMF(lambdaIndicesPath, lambdaValsPath, dim, withFriction, nbOtherConstraints, NNMFfileName, NonZerosCoeffTable):# , verbose=False ):


    f = open(lambdaIndicesPath,'r')
    nbSnap = 0
    snapshot = []
    snapshotV = []

    #if verbose : print "Reading file %r:" % lambdaIndicesPath
    lambdaIndices = []
    currentMaxIndex = 0
    for line in f:
        nbSnap = nbSnap + 1
        lineSplit = line.split()
        sizeLine = len(lineSplit)
        lineInt = map(int,lineSplit)
        if max(lineInt) > currentMaxIndex:
            currentMaxIndex = max(lineInt)
        lambdaIndices.append(lineInt)
    f.close()
    
    dimension = int(dim)
    
            
    
    
    
    withFriction = int(withFriction)
    nbOtherConstraints = int(nbOtherConstraints)
    if withFriction:
        dimension = 3*dimension
    lambdaSnapshot = np.zeros([dimension,nbSnap])
    lambdaFrictionSnapshot = np.zeros([dimension,nbSnap])
    f = open(lambdaValsPath,'r')
    nbCol = 0
    print('lambdaIndices ------------: ',lambdaIndices)
    print('lambdaIndices.shape', len(lambdaIndices[0]))
    for line in f:
        lineSplit = line.split()
        if withFriction:
            sizeLine = len(lineSplit)/3
        else:
            sizeLine = len(lineSplit)
        lineFloat = map(float,lineSplit)
        print('lineFloat ------------: ',lineFloat)
        print('sizeLine ------------: ',sizeLine)
        for i in range(sizeLine-nbOtherConstraints):
            if withFriction:
                print('i ------------: ',i)
                print('lambdaIndices[nbCol][3*i] ------------: ',lambdaIndices[nbCol][3*i])
                print('lambdaSnapshot size ------------: ',lambdaSnapshot.shape)
                lambdaSnapshot[3*lambdaIndices[nbCol][3*i],nbCol] = lineFloat[3*i]
                
                lambdaSnapshot[3*lambdaIndices[nbCol][3*i]+1,nbCol] = lineFloat[3*i+1]
                lambdaSnapshot[3*lambdaIndices[nbCol][3*i]+2,nbCol] = lineFloat[3*i+2]
                
                #lambdaFrictionSnapshot[3*lambdaIndices[nbCol][3*i]+1,nbCol] = lineFloat[3*i+1]
                #lambdaFrictionSnapshot[3*lambdaIndices[nbCol][3*i]+2,nbCol] = lineFloat[3*i+2]
            else:
                print('lambdaIndices[nbCol] ------------: ',lambdaIndices[nbCol]) 
                print('lambdaIndices[nbCol][i] ------------: ',lambdaIndices[nbCol][i]) 
                print('nbCol: ', nbCol, ' i: ', i)
                print
                lambdaSnapshot[lambdaIndices[nbCol][i],nbCol] = lineFloat[i]
        nbCol = nbCol + 1
    f.close()
    print('nbCol: ', nbCol)
    print('lambdaSnapshot.shape: ', lambdaSnapshot.shape)    
    print('lambdaFrictionSnapshot.shape: ', lambdaFrictionSnapshot.shape)    
    print(lambdaSnapshot)
    lambdaSnapCleaned = lambdaSnapshot[:,sum(lambdaSnapshot) != 0]
    lambdaFrictionSnapCleaned = lambdaFrictionSnapshot[:,sum(lambdaFrictionSnapshot) != 0]
    print('lambdaSnapCleaned.shape: ', lambdaSnapCleaned.shape)    
    print('lambdaFrictionSnapCleaned.shape: ', lambdaFrictionSnapCleaned.shape)    

    print(np.sum(lambdaSnapCleaned,axis=1))
    
    lambdaSnapVeryCleaned = lambdaSnapCleaned[np.sum(lambdaSnapCleaned,axis=1) != 0,:]
    lambdaFrictionSnapVeryCleaned = lambdaFrictionSnapCleaned[np.sum(lambdaFrictionSnapCleaned,axis=1) != 0,:]
    print('lambdaSnapVeryCleaned.shape: ', lambdaSnapVeryCleaned.shape)    
    print('lambdaFrictionSnapVeryCleaned.shape: ', lambdaFrictionSnapVeryCleaned.shape)         
    print(lambdaSnapCleaned)
    print(lambdaSnapVeryCleaned)
    np.savetxt('lambdaSnapshot.txt', lambdaSnapVeryCleaned, fmt='%10.5f')
    np.savetxt('lambdaFrictionSnapshot.txt', lambdaFrictionSnapVeryCleaned, fmt='%10.5f')
    k = 4
    sizeProblem = np.shape(lambdaSnapVeryCleaned)[0]
    

            
    
    
    
    W = np.random.random((sizeProblem, k))
    #W = lambdaSnapVeryCleaned[:,0:k]
    normalForceIndices = range(0,sizeProblem,3)
    for j in range(100):
        #input("Press Enter to continue...")
        WTW = np.dot(np.transpose(W),W)
        #print('titi:', np.dot(np.transpose(W),W))
        #print('toto:', np.dot(np.transpose(W),lambdaSnapVeryCleaned))
        #print('W:', W)
        #H = solve( WTW , np.dot(np.transpose(W),lambdaSnapVeryCleaned) )
        H = np.dot(np.linalg.pinv(WTW) , np.dot(np.transpose(W),lambdaSnapVeryCleaned))
        #print(H)
        negIndicesOnNormal = H<0
        #print('H ----- ',H)
        #print('H shape:', H.shape)
        #print('negIndicesOnNormal ----- ',negIndicesOnNormal)
        #print('range(1,sizeProblem,3) ----- ',range(1,sizeProblem,3))
        #if withFriction:
            #negIndicesOnNormal[range(1,sizeProblem,3)] = False
            #negIndicesOnNormal[range(2,sizeProblem,3)] = False
            #print('negIndicesOnNormal withFriction----- ',negIndicesOnNormal)
        #print('H ----- ',np.transpose(H))
        
        H[negIndicesOnNormal]=0
        np.savetxt('H0.txt', H, fmt='%10.5f')
        #print('H ----- ',np.transpose(H))
        print('current error: ----- ',np.linalg.norm(np.dot(W,H)-lambdaSnapVeryCleaned)/np.linalg.norm(lambdaSnapVeryCleaned))
        HHT = np.dot(H,np.transpose(H))
        HAT = np.dot(H,np.transpose(lambdaSnapVeryCleaned))
        #nonZeroLines = np.sum(HHT,axis=1) != 0
        #HHT = HHT[nonZeroLines,:]
        #HHT = HHT[:,nonZeroLines]
        #HAT = HAT[nonZeroLines,:]
        #W = solve( HHT , HAT )
        W = np.dot(np.linalg.pinv(HHT) , HAT)
        #W = solve( np.dot(H,np.transpose(H)) , np.dot(H,np.transpose(lambdaSnapVeryCleaned)) )
        #WnonZero = solve( HHT , HAT )
        #WT = np.transpose(np.random.random((sizeProblem, k)))
        #WT[nonZeroLines,:] = WnonZero
        #W = np.transpose(WT)
        W = np.transpose(W)
        
        negIndicesOnNormal = W<0
        if withFriction:
            negIndicesOnNormal[range(1,sizeProblem,3)] = False
            negIndicesOnNormal[range(2,sizeProblem,3)] = False        
        W[negIndicesOnNormal]=0
        WisZero = W==0
        #print WisZero
        #print range(0,sizeProblem,3)
        for ii in range(0,sizeProblem,3):
            for jj in range(k):
                #print WisZero[ii,jj]
                if WisZero[ii,jj]:
                    W[ii+1,jj]=0
                    W[ii+2,jj]=0

        print 'iteration', j
        #print ('W at the end:', W)
    #H = solve( np.dot(np.transpose(W),W) , np.dot(np.transpose(W),lambdaSnapVeryCleaned) )
    #H[H<0]=0
    for p in range(k):
            if (np.linalg.norm(W[:,p]) != 0.0):
                W[:,p] = W[:,p]/np.linalg.norm(W[:,p])
    print(W)
    #U, s, V = np.linalg.svd(lambdaFrictionSnapVeryCleaned, full_matrices=False)

    np.savetxt(NNMFfileName, W, header=str(sizeProblem)+' '+str(k), comments='', fmt='%10.5f')
    contactIndices = np.array(range(dimension))
    print(contactIndices)
    print(np.sum(lambdaSnapCleaned,axis=1) != 0)
    nonZerosIndices = contactIndices[np.sum(lambdaSnapCleaned,axis=1) != 0]
    print(contactIndices[np.sum(lambdaSnapCleaned,axis=1) != 0])
    print(dim)
    nonZerosTable = np.array([-1]*int(dimension))
    for i in range(nonZerosIndices.shape[0]):
        print (nonZerosIndices[i])
        nonZerosTable[nonZerosIndices[i]]=i
    print(nonZerosTable)
    np.savetxt(NonZerosCoeffTable, nonZerosTable, header=str(dimension)+' '+str(1), comments='', fmt='%d')
    
### Contacts HyperReduction   
    nbModes=k
    
    f = open('W_File.txt','r')
    modes = W
    contactWorkspaceSize = modes.shape[0]
    PsiWsnapLambda = np.zeros((nbModes*nbSnap, contactWorkspaceSize*contactWorkspaceSize))

    Wnp = np.zeros((contactWorkspaceSize,contactWorkspaceSize))
    print("lambdaIndices: ",lambdaIndices)
    snapNum = 0
    rowNum = 0
    for line in f:
        lineSplit = line.split()
        sizeLine = len(lineSplit)
        if (sizeLine != 0):
            lineFloat = map(float,lineSplit)
            print("lineFloat: ",lineFloat)
            for j in range(len(lineFloat)):
                if ((nonZerosTable[lambdaIndices[snapNum][rowNum]] != -1) or (nonZerosTable[lambdaIndices[snapNum][j]] != -1)):
                    Wnp[nonZerosTable[lambdaIndices[snapNum][rowNum]],nonZerosTable[lambdaIndices[snapNum][j]]] = lineFloat[j]
            rowNum = rowNum + 1
            print("Wnp at ",rowNum," : ", Wnp)
        else:
            print("000000000000000000000000000000000000000000000000")
            WsnapLambda = np.zeros((contactWorkspaceSize,contactWorkspaceSize))
            if (rowNum != 0):
                rowNum = 0
                for i in range(contactWorkspaceSize):
                    for j in range(contactWorkspaceSize):
                        print("contactWorkspaceSize:", contactWorkspaceSize, " i:", i, " j:", j, " snapNum:", snapNum)
                        print("lambdaSnapVeryCleaned.shape", lambdaSnapVeryCleaned.shape)
                        WsnapLambda[i][j] = Wnp[i][j]*lambdaSnapVeryCleaned[j][snapNum]
                        for modNum in range(nbModes):
                            PsiWsnapLambda[snapNum*nbModes+modNum][i*contactWorkspaceSize + j] = modes[i][modNum]*WsnapLambda[i][j]
                snapNum = snapNum + 1
                Wnp = np.zeros((contactWorkspaceSize,contactWorkspaceSize))
            print("WsnapLambda: ", WsnapLambda) 
                
    print('nbSnap:', nbSnap)
    print('nbModes:', nbModes)
    print('contactWorkspaceSize:',contactWorkspaceSize)
    print(PsiWsnapLambda)      
    np.savetxt('PsiWsnapLambda.txt', PsiWsnapLambda, fmt='%10.5f')        
            
            
            
        #if not x0Found and lineSplit[0] == "X0=":
            #lineFloat = map(float,lineSplit[1:])
            #restPos = []
            #restPos.append(lineFloat)
            #restPos = np.transpose(restPos)
            #x0Found = True
        #if (lineSplit[0] == "X="):  
            #lineFloat = map(float,lineSplit[1:])
            #snapshot.append(lineFloat);
        #if (lineSplit[0] == "V="):  
            #lineFloat = map(float,lineSplit[1:])
            #snapshotV.append(lineFloat);

    #if x0Found :
        #snapshot = np.transpose(snapshot)
        #if np.isnan(np.sum(np.sum(snapshot))):
            #print "NAN PRESENT IN THE POSITIONS! THE SIMULATION WENT WRONG DURING THE SHAKING! MAKE SURE YOUR SIMULATION IS STABLE!"
            #return -1

        #nbDOFs, nbSnap = np.shape(snapshot)
        #snapshotDiff = np.zeros((nbDOFs,nbSnap))
        #translationModes = np.zeros((nbDOFs,3))

        #if verbose : 
            #print "    Read",nbLine,"line and found",nbSnap,"snapshot with",nbDOFs,"of DOF"
            #print "Done reading file %r:" % stateFilePath,'\n'

        #for i in range(0,nbSnap):
            #snapshotDiff[:,i] = snapshot[:,i] - restPos[:,0]
                      
        #for i in range(0,nbDOFs/3):
            #translationModes[3*i][0] = 1/math.sqrt(nbDOFs/3)
            #translationModes[3*i+1][1] = 1/math.sqrt(nbDOFs/3)
            #translationModes[3*i+2][2] = 1/math.sqrt(nbDOFs/3)
        
        #tmp = []
        #if (addRigidBodyModes):
            #if (addRigidBodyModes[0] == 1):
                #for j in range(nbSnap-1):    
                    #snapshotDiff[:,[j]] = snapshotDiff[:,[j]] - (np.matmul(np.transpose(snapshotDiff[:,[j]]),translationModes[:,[0]]))*translationModes[:,[0]]
                #tmp.append(0)
            #if (addRigidBodyModes[1] == 1):
                #for j in range(nbSnap-1):    
                    #snapshotDiff[:,[j]] = snapshotDiff[:,[j]] - (np.matmul(np.transpose(snapshotDiff[:,[j]]),translationModes[:,[1]]))*translationModes[:,[1]]
                #tmp.append(1)
            #if (addRigidBodyModes[2] == 1):
                #for j in range(nbSnap-1):    
                    #snapshotDiff[:,[j]] = snapshotDiff[:,[j]] - (np.matmul(np.transpose(snapshotDiff[:,[j]]),translationModes[:,[2]]))*translationModes[:,[2]]
                #tmp.append(2)

        #U, s, V = np.linalg.svd(snapshotDiff, full_matrices=False) # 99% time execution
        #sSquare = [i**2 for i in s]
        #sumSVD = np.sum(sSquare)

        #stateFilePath = os.path.normpath(stateFilePath)
        #outputDir = slash.join(stateFilePath.split(slash)[:-1])+slash
        #np.savetxt(outputDir+"Sdata.txt",s)

        #i = 0
        #if verbose : 
            #print "Determining number of Modes with a Tolerance of",tol

        #while (np.sqrt(np.sum(sSquare[i:])/sumSVD) > tol or i==0):
            #i = i+1

        #nbModes = i
        #if (addRigidBodyModes and addRigidBodyModes != [0]*3):    
            #print "Concatenating translation modes"
            #nbModes += 3
            #modesTot = np.concatenate((translationModes[:,tmp], U[:,0:nbModes]), axis=1)
            #np.savetxt(modesFileName, modesTot, header=str(nbDOFs)+' '+str(nbModes), comments='', fmt='%10.5f')
        #else:
            #np.savetxt(modesFileName, U[:,0:nbModes], header=str(nbDOFs)+' '+str(nbModes), comments='', fmt='%10.5f')
        #if verbose :
            #print "===> Success readStateFilesAndComputeModes.py\n"

        #f.close()

        #print(str(nbModes)+" possible modes with a tolerance of "+str(tol))
        #return nbModes

    #else: 
        #print "XO NOT FOUND"
        #return -1

##########################################################################################





if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 2:
        print("Function need at least 3 arguments")
    else:
        readLambdaFilesAndComputeNNMF(*argv[1:])