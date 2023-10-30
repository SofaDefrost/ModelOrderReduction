# -*- coding: utf-8 -*-
"""
:code:`python prepareStateFiletoDisplayModes.py originalStateFilename modesFilename displayModesFilename scalar`
"""

import numpy as np
import os

from sys import argv


def prepareStateFiletoDisplayModes(originalStateFilename, modesFilename, displayModesFilename, scalar):

    f = open(originalStateFilename,'r')
    print("Reading file %r:" % originalStateFilename)

    for line in f:
      lineSplit = line.split();
      print(lineSplit[0])
      if (lineSplit[0] == "X0="):  
        initialPos = map(float,lineSplit[1:])
        break
    f.close()

    initialPos = np.transpose(initialPos)

    cnt = 0
    nbSnap = 0
    modes = []
    f = open(modesFilename,'r') 
    for line in f:
      cnt = cnt + 1
      lineSplit = line.split();
      print(lineSplit[0])
      if (cnt > 1):  
        nbSnap = nbSnap + 1
        print("Reading modes line number: ", nbSnap)
        lineFloat = map(float,lineSplit)
        modes.append(lineFloat);
    f.close()

    nbDOfs, nbModes = np.shape(modes)
    print('nbDOfs, nbModes: ', nbDOfs, nbModes)
    modes = np.array(modes)
    for i in range(nbDOfs):
        print(modes[i,0], ' ', modes[i,1], ' ', modes[i,2])

    lambdaTimesMode = np.zeros(np.shape(modes))
    displayMode = np.zeros(np.shape(modes))

    for k in range(nbModes):
        lambdaTimesMode[:,k] = np.multiply(modes[:,k],float(scalar))
        displayMode[:,k] = np.add(initialPos,lambdaTimesMode[:,k])
        
    print('display size', np.shape(np.transpose(displayMode)))


    np.savetxt(displayModesFilename+'Tmp', np.transpose(displayMode),header= '', comments='', fmt='%10.5f')

    f = open(displayModesFilename+'Tmp','r')
    fout = open(displayModesFilename,'w')
    time = 0
    for line in f:
        print('time is ', time)
        fout.write('T= ' + str(time) + '\n X= ' + line)
        time = time + 0.01
    f.close()
    fout.close()
    os.remove(displayModesFilename+'Tmp')

##########################################################################################

if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 5:
        print("Function need at least 4 arguments")
    else:
        prepareStateFiletoDisplayModes(*argv[1:])