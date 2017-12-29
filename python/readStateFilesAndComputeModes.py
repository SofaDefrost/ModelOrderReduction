## Usage: python readStateFilesAndComputeModes.py stateFilename initPositionFilename modesFilename tol addRigidBodyModesBOOL

import math
import numpy as np

from sys import argv


script, stateFilename, initPositionFilename, modesFilename, tol, addRigidBodyModes = argv

finit = open(initPositionFilename,'r')
print "Reading file %r:" % initPositionFilename
for line in finit:
  lineSplit = line.split();
  print(lineSplit[0])
  if (lineSplit[0] == "X0="):  
      print "Reading rest position: "
      lineFloat = map(float,lineSplit[1:])
      restPos = []
      restPos.append(lineFloat)
      break
finit.close()
restPos = np.transpose(restPos)
x, y = np.shape(restPos)
print 'size restPos = ', x, ' ', y

f = open(stateFilename,'r')
#fout = open("snapshot.txt",'w')
print "Reading file %r:" % stateFilename
print tol
tol = float(tol)
addRigidBodyModes = int(addRigidBodyModes)
nbSnap = 0
snapshot = []
snapshotV = []
for line in f:
  lineSplit = line.split();
  if (lineSplit[0] == "X="):  
    nbSnap = nbSnap + 1
    print "Reading snapshot number: ", nbSnap
    lineFloat = map(float,lineSplit[1:])
    snapshot.append(lineFloat);
    #fout.write(lineSplit[1:-1])
  if (lineSplit[0] == "V="):  
    print "Reading speed snapshot number: ", nbSnap
    lineFloat = map(float,lineSplit[1:])
    snapshotV.append(lineFloat);


snapshot = np.transpose(snapshot)
nbDOFs, nbSnap = np.shape(snapshot)
print 'sizes = ',nbDOFs, nbSnap

#snapshotDiff = np.zeros((nbDOFs,nbSnap-1))
#for i in range(1,nbSnap):
#    snapshotDiff[:,i-1] = snapshot[:,i] - snapshot[:,0]
print restPos[:,0]
snapshotDiff = np.zeros((nbDOFs,nbSnap))
for i in range(0,nbSnap):
    snapshotDiff[:,i] = snapshot[:,i] - restPos[:,0]
    
translationModes = np.zeros((nbDOFs,3))
#translationModes = np.zeros((nbDOFs,2))
for i in range(0,nbDOFs/3):
    translationModes[3*i][0] = 1/math.sqrt(nbDOFs/3)
    translationModes[3*i+1][1] = 1/math.sqrt(nbDOFs/3)
    translationModes[3*i+2][2] = 1/math.sqrt(nbDOFs/3)
if (addRigidBodyModes == 1):
    for i in range(3):
#    for i in range(2):
        for j in range(nbSnap-1):    
            snapshotDiff[:,[j]] = snapshotDiff[:,[j]] - (np.matmul(np.transpose(snapshotDiff[:,[j]]),translationModes[:,[i]]))*translationModes[:,[i]]

U, s, V = np.linalg.svd(snapshotDiff, full_matrices=False)

sSquare = [i**2 for i in s]
sumSVD = np.sum(sSquare)
print 'sumSVD', sumSVD

i = 1
print 'np.sqrt(np.sum(sSquare[i:])/sumSVD)',np.sqrt(np.sum(sSquare[i:])/sumSVD)
while (np.sqrt(np.sum(sSquare[i:])/sumSVD) > tol):
#while (np.sum(sSquare[i:])/sumSVD > tol):    
	print 'np.sqrt(np.sum(sSquare[i:])/sumSVD)',np.sqrt(np.sum(sSquare[i:])/sumSVD)
#	print 'np.sqrt(np.sum(sSquare[i:])/sumSVD)',np.sum(sSquare[i:])/sumSVD
	i = i+1
nbModes = i
print 'Number of modes to reach tolerance: ', nbModes

if (addRigidBodyModes == 1):    
    print "Concatenating translation modes !!!!!!!!!!!!"
    modesTot = np.concatenate((translationModes, U[:,0:nbModes]), axis=1)
    np.savetxt(modesFilename, modesTot, header=str(nbDOFs)+' '+str(nbModes+3), comments='', fmt='%10.5f')
else:
    np.savetxt(modesFilename, U[:,0:nbModes], header=str(nbDOFs)+' '+str(nbModes), comments='', fmt='%10.5f')
print np.shape(snapshot)
print(s)

#fout.write(translateCoordString)

f.close()
#fout.close()
