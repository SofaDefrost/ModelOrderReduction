# -*- coding: utf-8 -*-
"""
:code:`python readStateFilesAndComputeModes.py stateFilename tol modesFilename addRigidBodyModesBOOL`
"""

import os
import math
import numpy as np
import platform

from sys import argv

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"


def readStateFilesAndComputeModes(stateFilePath, tol, modesFileName, addRigidBodyModes=None, verbose=False):
    print("###################################################")
    print("Executing readStateFilesAndComputeModes.py\n")
    print("Arguments :\n")
    print("     INPUT  :")
    print("     in stateFilePath         :", stateFilePath)
    print("     with arguments           :")
    print("         -tolerance               :", tol, "\n")
    print("     OUTPUT :")
    print("         -modesFileName           :", modesFileName, "\n")
    print("###################################################")
    x0Found = False

    f = open(stateFilePath, 'r')
    nbSnap = 0
    nbLine = 0
    snapshot = []
    snapshotV = []

    if verbose: print("Reading file %r:" % stateFilePath)
    for line in f:
        nbLine = nbLine + 1
        lineSplit = line.split();
        if not x0Found and lineSplit[0] == "X0=":
            lineFloat = list(map(float, lineSplit[1:]))
            restPos = []
            restPos.append(lineFloat)
            restPos = np.transpose(restPos)
            x0Found = True
        if (lineSplit[0] == "X="):
            lineFloat = list(map(float, lineSplit[1:]))
            snapshot.append(lineFloat);
        if (lineSplit[0] == "V="):
            lineFloat = list(map(float, lineSplit[1:]))
            snapshotV.append(lineFloat);

    if x0Found:
        snapshot = np.transpose(snapshot)
        if np.isnan(np.sum(np.sum(snapshot))):
            print("NAN PRESENT IN THE POSITIONS! THE SIMULATION WENT WRONG DURING THE SHAKING! MAKE SURE YOUR "
                  "SIMULATION IS STABLE!")
            return -1

        nbDOFs, nbSnap = np.shape(snapshot)
        snapshotDiff = np.zeros((nbDOFs, nbSnap))
        translationModes = np.zeros((nbDOFs, 3))

        if verbose:
            print("    Read", nbLine, "line and found", nbSnap, "snapshot with", nbDOFs, "of DOF")
            print("Done reading file %r:" % stateFilePath, '\n')

        for i in range(0, nbSnap):
            snapshotDiff[:, i] = snapshot[:, i] - restPos[:, 0]

        for i in range(0, int(nbDOFs / 3)):
            translationModes[3 * i][0] = 1 / math.sqrt(nbDOFs / 3)
            translationModes[3 * i + 1][1] = 1 / math.sqrt(nbDOFs / 3)
            translationModes[3 * i + 2][2] = 1 / math.sqrt(nbDOFs / 3)

        tmp = []
        if (addRigidBodyModes):
            if (addRigidBodyModes[0] == 1):
                for j in range(nbSnap - 1):
                    snapshotDiff[:, [j]] = snapshotDiff[:, [j]] - (
                        np.matmul(np.transpose(snapshotDiff[:, [j]]), translationModes[:, [0]])) * translationModes[:,
                                                                                                   [0]]
                tmp.append(0)
            if (addRigidBodyModes[1] == 1):
                for j in range(nbSnap - 1):
                    snapshotDiff[:, [j]] = snapshotDiff[:, [j]] - (
                        np.matmul(np.transpose(snapshotDiff[:, [j]]), translationModes[:, [1]])) * translationModes[:,
                                                                                                   [1]]
                tmp.append(1)
            if (addRigidBodyModes[2] == 1):
                for j in range(nbSnap - 1):
                    snapshotDiff[:, [j]] = snapshotDiff[:, [j]] - (
                        np.matmul(np.transpose(snapshotDiff[:, [j]]), translationModes[:, [2]])) * translationModes[:,
                                                                                                   [2]]
                tmp.append(2)

        U, s, V = np.linalg.svd(snapshotDiff, full_matrices=False)  # 99% time execution
        sSquare = [i ** 2 for i in s]
        sumSVD = np.sum(sSquare)

        stateFilePath = os.path.normpath(stateFilePath)
        outputDir = slash.join(stateFilePath.split(slash)[:-1]) + slash
        np.savetxt(outputDir + "Sdata.txt", s)

        i = 0
        if verbose:
            print("Determining number of Modes with a Tolerance of", tol)

        while (np.sqrt(np.sum(sSquare[i:]) / sumSVD) > tol or i == 0):
            i = i + 1

        nbModes = i
        if (addRigidBodyModes and addRigidBodyModes != [0] * 3):
            print("Concatenating translation modes")
            nbModes += 3
            modesTot = np.concatenate((translationModes[:, tmp], U[:, 0:nbModes]), axis=1)
            np.savetxt(modesFileName, modesTot, header=str(nbDOFs) + ' ' + str(nbModes), comments='', fmt='%10.5f')
        else:
            np.savetxt(modesFileName, U[:, 0:nbModes], header=str(nbDOFs) + ' ' + str(nbModes), comments='',
                       fmt='%10.5f')
        if verbose:
            print("===> Success readStateFilesAndComputeModes.py\n")

        f.close()

        print(str(nbModes) + " possible modes with a tolerance of " + str(tol))
        return nbModes

    else:
        print("XO NOT FOUND")
        return -1


##########################################################################################


if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 4:
        print("Function need at least 3 arguments")
    else:
        readStateFilesAndComputeModes(*argv[1:])
