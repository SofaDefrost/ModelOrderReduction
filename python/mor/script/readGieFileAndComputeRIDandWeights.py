## Usage: python readGieFileAndComputeRIDandWeights.py gieFilename outputfilesName tol  
## tol is typically between 0.1 and 0.01

import math
import numpy as np
import code
from sys import argv

ECSWdataPath = ''


def selectECSW(G,b,tau):

  plop, numElem = np.shape(G)
#  ECSWindex = np.empty([0,1])
  ECSWindex = set([])
  #frontierIndexToSave = [19,35,36,38]; % ************************   To force the elements on the frontier
  #freeIndex = 1:numElem;   % ************************
  #freeIndex(frontierIndexToSave) = [];  % ************************
  #G = G(:,freeIndex);   % ************************
  xi = np.zeros((numElem,1))
  #xi = zeros(size(G,2),1); % ************************


  valTarget = tau*np.linalg.norm(b);
  while (np.linalg.norm(G.dot(xi) - b) > tau*np.linalg.norm(b)):
    valErr = np.linalg.norm(G.dot(xi) - b)
    print 'Current Error: ', valErr,' Target Error: ', valTarget
    vecDiff = b - G.dot(xi)
    #print 'b - G.dot(xi)', np.shape(b), np.shape(G.dot(xi)) 
    #print 'vecDiff computed', np.shape(vecDiff)
    GT = np.transpose(G)
    #print 'GT computed', np.shape(GT)
    mu = GT.dot(vecDiff)
    #print 'mu', mu
    index = int(np.argmax(mu))
    #print 'ECSWindex', ECSWindex, 'index', index
  #  print type(index)
  #  ECSWindex = np.unique(np.append(ECSWindex, [[index]], axis=0))
    ECSWindex = ECSWindex.union([index])


  #  print type(ECSWindex)
    #print 'ECSWindex', ECSWindex
    
    while (True):
      
      Gtilde = G[:,list(ECSWindex)]
      etaTilde = np.linalg.solve( np.transpose(Gtilde).dot(Gtilde) , np.transpose(Gtilde).dot(b) )
      if all(etaTilde>0):
        xi[list(ECSWindex)] = etaTilde
        break
        
        
      print 'Hohohohohohohohoho !!!'
      negIndex = (etaTilde-xi[list(ECSWindex)])<0
      negIndex = list(negIndex.flatten())
      #print negIndex



      ECSWindexNegative = []
      etaTildeNegative = []
      ind = 0
      for i in negIndex:
        if (i):
          ECSWindexNegative.append(list(ECSWindex)[ind])
          etaTildeNegative.append(etaTilde[ind])
        ind = ind + 1

      vec1 = -xi[ECSWindexNegative] 
      #code.interact(local=locals())
      vec2 = (etaTildeNegative-xi[ECSWindexNegative])
      maxFeasibleStep = np.amin(vec1/vec2);
      xi[list(ECSWindex)] = xi[list(ECSWindex)] + maxFeasibleStep*(etaTilde - xi[list(ECSWindex)]);
      zeroIndex = np.absolute(xi)<1.0e-12;
      
      #print 'ECSWindex hohoho', ECSWindex
      ECSWindex = set(range(numElem))
      #code.interact(local=locals())
      NonZero = []
      ind = 0
      for i in zeroIndex:
        if (not i):
          NonZero.append(list(ECSWindex)[ind])
        ind = ind + 1

      ECSWindex = set(NonZero)
      #code.interact(local=locals())

  valErr = np.linalg.norm(G.dot(xi) - b)
  print '#############################'
  print 'Final Error: ', valErr ,' Target Error: ', valTarget

  return (ECSWindex,xi)

script, gieFilename, outputfilesName, tol = argv



#ECSWindex,xi = selectECSW(np.array([[1,2],[3,4]]),np.array([[3],[7]]),0.01)



fgie = open(gieFilename,'r')

print "Reading file %r:" % gieFilename
print tol
tol = float(tol)
print "Will store in:", 'reducedIntegrationDomain_'+outputfilesName+'.txt'

lineCount = 0
gie = []
for line in fgie:
  lineSplit = line.split();
  lineFloat = map(float,lineSplit)
  gie.append(lineFloat);
  lineCount = lineCount +1
  print 'line nb ', lineCount, ' read'

gie = np.array(gie)
nbTests , nbElements = np.shape(gie)
print 'size GIE = ', nbTests, ' ', nbElements

keepIndex = []
for i in range(nbTests):
  if any(gie[i,:] != 0):
    keepIndex.append(i)

gie = gie[keepIndex,:]

print 'size cleaned GIE = ', np.shape(gie)
bECSW = np.sum(gie,axis=1)
bECSW = bECSW[np.newaxis]
print 'size bECSW = ', np.shape(bECSW)
bECSW = np.transpose(bECSW)
print 'size bECSW = ', np.shape(bECSW)

ECSWindex,xi = selectECSW(gie,bECSW,tol)
#code.interact(local=locals())

print tol
ECSWindex = np.array(sorted(list(ECSWindex)))
sizeRID = ECSWindex.size
nbElements = xi.size
np.savetxt(ECSWdataPath+'reducedIntegrationDomain_'+outputfilesName+'.txt',ECSWindex, header=str(sizeRID)+' 1', comments='', fmt='%d')
np.savetxt(ECSWdataPath+'weights_'+outputfilesName+'.txt',xi, header=str(nbElements)+' 1', comments='',fmt='%10.5f')


fgie.close()

