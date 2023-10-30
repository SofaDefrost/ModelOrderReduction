# -*- coding: utf-8 -*-
"""
:code:`python readLambdaFilesAndComputeNNMF.py stateFilename tol modesFilename addRigidBodyModesBOOL`
"""

import numpy as np
from scipy.linalg import solve
import platform

from sys import argv

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"

def readLambdaFilesAndComputeNNMF(lambdaIndicesPath, lambdaValsPath, dim, withFriction, nbOtherConstraints, NNMFfileName, NonZerosCoeffTable, nbModes):# , verbose=False ):

    f = open(lambdaIndicesPath,'r')
    nbSnap = 0
    snapshot = []
    snapshotV = []

    #if verbose : print "Reading file %r:" % lambdaIndicesPath
    lambdaIndices = []
    currentMaxIndex = 0
    #To skip Nskip snapshot entries: Nskip = 1 to keep everything
    Nskip = 1
    for line in f:
        nbSnap = nbSnap + 1
        lineSplit = line.split()
        sizeLine = len(lineSplit)
        lineInt = map(int,lineSplit)
        if max(lineInt) > currentMaxIndex:
            currentMaxIndex = max(lineInt)
        if nbSnap%Nskip == 0:    
            lambdaIndices.append(lineInt)
    f.close()
    nbSnap = nbSnap/Nskip
    dimension = int(dim)
    nbModes = int(nbModes)
            
    
    
    
    withFriction = int(withFriction)
    nbOtherConstraints = int(nbOtherConstraints)
    if withFriction:
        dimension = 3*dimension
    lambdaSnapshot = np.zeros([dimension,nbSnap])
    lambdaFrictionSnapshot = np.zeros([dimension,nbSnap])
    f = open(lambdaValsPath,'r')
    nbCol = 0
    nbSnap = 0
    #print('lambdaIndices ------------: ',lambdaIndices)
    #print('lambdaIndices.shape', len(lambdaIndices[0]))
    for line in f:
        nbSnap = nbSnap + 1
        lineSplit = line.split()
        if withFriction:
            sizeLine = len(lineSplit)/3
        else:
            sizeLine = len(lineSplit)
        lineFloat = map(float,lineSplit)
        #print('lineFloat ------------: ',lineFloat)
        #print('sizeLine ------------: ',sizeLine)
        print(nbCol)
        if nbSnap%Nskip == 0:
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
                    #print('lambdaIndices[nbCol] ------------: ',lambdaIndices[nbCol]) 
                    #print('lambdaIndices[nbCol][i] ------------: ',lambdaIndices[nbCol][i]) 
                    #print('nbCol: ', nbCol, ' i: ', i)
                    lambdaSnapshot[lambdaIndices[nbCol][i],nbCol] = lineFloat[i]
            nbCol = nbCol + 1
        #nbCol = nbCol + 1
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
    print("Saving snaphot... Size is ", lambdaSnapVeryCleaned.shape)
    np.savetxt('lambdaSnapshot.txt', lambdaSnapVeryCleaned, fmt='%10.5f')
    np.savetxt('lambdaFrictionSnapshot.txt', lambdaFrictionSnapVeryCleaned, fmt='%10.5f')
    k = nbModes
    sizeProblem = np.shape(lambdaSnapVeryCleaned)[0]
    

            
    
    
    
    W = np.random.random((sizeProblem, k))
    Wmin = np.zeros([sizeProblem, k])
    #W = lambdaSnapVeryCleaned[:,0:k]
    normalForceIndices = range(0,sizeProblem,3)
    minErr = 200
    #for j in range(100):
    for j in range(50):

        #input("Press Enter to continue...")
        WTW = np.dot(np.transpose(W),W)
        #print('titi:', np.dot(np.transpose(W),W))
        #print('toto:', np.dot(np.transpose(W),lambdaSnapVeryCleaned))
        #print('W:', W)
        H = solve( WTW , np.dot(np.transpose(W),lambdaSnapVeryCleaned) )
        #H = np.dot(np.linalg.pinv(WTW) , np.dot(np.transpose(W),lambdaSnapVeryCleaned))
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
        print('Error in H before zeroing: ----- ',np.linalg.norm(np.dot(W,H)-lambdaSnapVeryCleaned)/np.linalg.norm(lambdaSnapVeryCleaned))
        H[negIndicesOnNormal]=0
        #np.savetxt('H0.txt', H, fmt='%10.5f')
        #print('H ----- ',np.transpose(H))
        print('Error in H after zeroing: ----- ',np.linalg.norm(np.dot(W,H)-lambdaSnapVeryCleaned)/np.linalg.norm(lambdaSnapVeryCleaned))
        HHT = np.dot(H,np.transpose(H))
        HAT = np.dot(H,np.transpose(lambdaSnapVeryCleaned))
        #nonZeroLines = np.sum(HHT,axis=1) != 0
        #HHT = HHT[nonZeroLines,:]
        #HHT = HHT[:,nonZeroLines]
        #HAT = HAT[nonZeroLines,:]
        W = solve( HHT , HAT )
        #W = np.dot(np.linalg.pinv(HHT) , HAT)
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
            
        print('Error in W before zeroing: ----- ',np.linalg.norm(np.dot(W,H)-lambdaSnapVeryCleaned)/np.linalg.norm(lambdaSnapVeryCleaned))    
        W[negIndicesOnNormal]=0
        err = np.linalg.norm(np.dot(W,H)-lambdaSnapVeryCleaned)/np.linalg.norm(lambdaSnapVeryCleaned)
        print('Error in W after zeroing: ----- ',err)
        
        if err < minErr:
            minErr = err
            Wmin[:] = W[:]
            
        #print('numerateur: ----- ',np.linalg.norm(np.dot(W,H)-lambdaSnapVeryCleaned))
        #print('denominateur: ----- ',np.linalg.norm(lambdaSnapVeryCleaned))
        #if withFriction:
            #print W.shape
            #WisZero = W==0
            #print WisZero.shape
            #print 'sizeProblem:', sizeProblem
            #print range(0,sizeProblem,3)
            #for ii in range(0,sizeProblem,3):
                #print ii
                #for jj in range(k):
                    ##print WisZero[ii,jj]
                    #if WisZero[ii,jj]:
                        #W[ii+1,jj]=0
                        #W[ii+2,jj]=0

        print('iteration', j)
        #print ('W at the end:', W)
    print('Min Error in W after zeroing: ----- ',minErr)
    #H = solve( np.dot(np.transpose(W),W) , np.dot(np.transpose(W),lambdaSnapVeryCleaned) )
    #H[H<0]=0
    for p in range(k):
            if (np.linalg.norm(W[:,p]) != 0.0):
                W[:,p] = W[:,p]/np.linalg.norm(W[:,p])
                Wmin[:,p] = Wmin[:,p]/np.linalg.norm(Wmin[:,p])
    #print(W)
    #U, s, V = np.linalg.svd(lambdaFrictionSnapVeryCleaned, full_matrices=False)

    np.savetxt(NNMFfileName, W, header=str(sizeProblem)+' '+str(k), comments='', fmt='%10.5f')
    #np.savetxt(NNMFfileName, Wmin, header=str(sizeProblem)+' '+str(k), comments='', fmt='%10.5f')
    contactIndices = np.array(range(dimension))
    #print(contactIndices)
    #print(np.sum(lambdaSnapCleaned,axis=1) != 0)
    nonZerosIndices = contactIndices[np.sum(lambdaSnapCleaned,axis=1) != 0]
    #print(contactIndices[np.sum(lambdaSnapCleaned,axis=1) != 0])
    #print(dim)
    nonZerosTable = np.array([-1]*int(dimension))
    for i in range(nonZerosIndices.shape[0]):
        nonZerosTable[nonZerosIndices[i]]=i
    #print(nonZerosTable)
    np.savetxt(NonZerosCoeffTable, nonZerosTable, header=str(dimension)+' '+str(1), comments='', fmt='%d')
    
### Contacts HyperReduction   
    #nbModes=k
    
    #f = open('W_File.txt','r')
    #modes = W
    #contactWorkspaceSize = modes.shape[0]
    #PsiWsnapLambda = np.zeros((nbModes*nbSnap, contactWorkspaceSize*contactWorkspaceSize))

    #Wnp = np.zeros((contactWorkspaceSize,contactWorkspaceSize))
    #print("lambdaIndices: ",lambdaIndices)
    #snapNum = 0
    #rowNum = 0
    #for line in f:
        #lineSplit = line.split()
        #sizeLine = len(lineSplit)
        #if (sizeLine != 0):
            #lineFloat = map(float,lineSplit)
            #print("lineFloat: ",lineFloat)
            #for j in range(len(lineFloat)):
                #if ((nonZerosTable[lambdaIndices[snapNum][rowNum]] != -1) or (nonZerosTable[lambdaIndices[snapNum][j]] != -1)):
                    #Wnp[nonZerosTable[lambdaIndices[snapNum][rowNum]],nonZerosTable[lambdaIndices[snapNum][j]]] = lineFloat[j]
            #rowNum = rowNum + 1
            #print("Wnp at ",rowNum," : ", Wnp)
        #else:
            #print("000000000000000000000000000000000000000000000000")
            #WsnapLambda = np.zeros((contactWorkspaceSize,contactWorkspaceSize))
            #if (rowNum != 0):
                #rowNum = 0
                #for i in range(contactWorkspaceSize):
                    #for j in range(contactWorkspaceSize):
                        #print("contactWorkspaceSize:", contactWorkspaceSize, " i:", i, " j:", j, " snapNum:", snapNum)
                        #print("lambdaSnapVeryCleaned.shape", lambdaSnapVeryCleaned.shape)
                        #WsnapLambda[i][j] = Wnp[i][j]*lambdaSnapVeryCleaned[j][snapNum]
                        #for modNum in range(nbModes):
                            #PsiWsnapLambda[snapNum*nbModes+modNum][i*contactWorkspaceSize + j] = modes[i][modNum]*WsnapLambda[i][j]
                #snapNum = snapNum + 1
                #Wnp = np.zeros((contactWorkspaceSize,contactWorkspaceSize))
            #print("WsnapLambda: ", WsnapLambda) 
                
    #print('nbSnap:', nbSnap)
    #print('nbModes:', nbModes)
    #print('contactWorkspaceSize:',contactWorkspaceSize)
    #print(PsiWsnapLambda)      
    #np.savetxt('PsiWsnapLambda.txt', PsiWsnapLambda, fmt='%10.5f')        
            
##########################################################################################





if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 2:
        print("Function need at least 3 arguments")
    else:
        readLambdaFilesAndComputeNNMF(*argv[1:])
