# -*- coding: utf-8 -*-
"""
:code:`python readMechanicalMatricesAndComputeVibrationModes.py massFile stiffnessFile modesFilename tol addRigidBodyModesBOOL`
"""

import numpy as np
from scipy import sparse
import scipy.sparse.linalg as sLA

from sys import argv


def readMechanicalMatricesAndComputeVibrationModes(massFile, stiffnessFile, modesFilename, nbModes, addRigidBodyModes):

    fmass = open(massFile,'r')
    print("Reading file %r:" % massFile)
    mass = []
    nbDOFs=0
    for line in fmass:
      lineSplit = line.split();
      if (len(lineSplit) > 1):
          nbDOFs = nbDOFs+1
          print("Reading Mass: line num: %i" % nbDOFs)
          if (lineSplit[-2] == ']'):
                lineFloat = map(float,lineSplit[1:-2])
          else:
                lineFloat = map(float,lineSplit[1:-1])
          mass.append(lineFloat)
    fmass.close()
    mass = np.transpose(mass)
    print('The mass:---------------------------\n', mass, '\n---------------------------End of the mass.')
    fstiff = open(stiffnessFile,'r')
    print("Reading file %r:" % stiffnessFile)
    stiffness = []
    dim = 0
    for line in fstiff:
      lineSplit = line.split();
      if (len(lineSplit) > 1):
          dim = dim+1
          print("Reading Stiffness: line num: %i" % dim)
          if (lineSplit[-2] == ']'):
                lineFloat = map(float,lineSplit[1:-2])
          else:
                lineFloat = map(float,lineSplit[1:-1])
          stiffness.append(lineFloat)
    fstiff.close()
    if (dim == nbDOFs):

        stiffness = np.transpose(stiffness)
        print('The stiffness:---------------------------\n', stiffness, '\n---------------------------End of the stiffness.')

        nbModes = int(nbModes)
        sparseMass = sparse.csr_matrix(mass)
        sparseStiffness = sparse.csr_matrix(stiffness)
        vals, vecs = sLA.eigsh(sparseStiffness,M=sparseMass,k=nbModes,which='SM')
        print('vals :', vals)
        print('vecs :', vecs)

        #w,v = LA.eig(np.matmul(LA.inv(mass),stiffness))
        #order = np.argsort(w)
        #print 'eigenvalues:', w
        #print 'order of the eigenvalues:', order
        #w[::-1].sort() # sort in descending order
        #print 'Sorted eigenvalues:', w

        #sumEig = np.sum(w)
        #print 'sumEig', sumEig
        #print(w)
        #i = 1
        #print 'np.sum(w[i:]/sumEig', np.sum(w[i:])/sumEig
        #tol = float(tol)
        #print 'np.sum(w[i:])/sumEig > tol', (np.sum(w[i:])/sumEig)>tol
        #while (np.sum(w[i:])/sumEig > tol):
            #print 'np.sum(w[i:]/sumEig',np.sum(w[i:])/sumEig
            #i = i+1
        #print 'np.sum(w[i:])/sumEig', (np.sum(w[i:])/sumEig)
        #nbModes = i
        #print 'Number of modes to reach tolerance: ', nbModes

        print('nbModes', nbModes)
        #listOrder = order.tolist()
        #print 'listOrder', listOrder[0:4], listOrder[1]
        #print 'listOrder[0:nbModes]',listOrder[0:nbModes]
        #listOfModesIndices = v[:,listOrder[0:nbModes]]

        #np.savetxt(modesFilename+'.txt', listOfModesIndices, header=str(nbDOFs)+' '+str(nbModes), comments='', fmt='%10.5f')
        np.savetxt(modesFilename+'_sparse.txt', vecs, header=str(nbDOFs)+' '+str(nbModes), comments='', fmt='%10.5f')
    else:
        print('ERROR: Size of Mass and Stiffness are different! Mass dim is : ', nbDOFs, ' .Stiffness dim is : ', dim)


##########################################################################################

if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 6:
        print("Function need at least 5 arguments")
    else:
        readMechanicalMatricesAndComputeVibrationModes(*argv[1:])