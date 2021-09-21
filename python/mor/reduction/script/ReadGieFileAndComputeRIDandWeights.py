# -*- coding: utf-8 -*-

## Usage: python readGieFileAndComputeRIDandWeights.py gieFilename RIDFileName weightsFileName tol
## tol is typically between 0.1 and 0.01
from __future__ import print_function
import numpy as np
import os
import sys
from sys import argv
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../../gui')
import utility as u


class ActiveSet():
    def __init__(self):
        self.inds_set = set([])
        self.inds_list = []

    def add(self, ind):
        if ind not in self.inds_set:
            self.inds_set.add(ind)
            self.inds_list.append(ind)

    def get_list(self):
        return self.inds_list

    def override(self, inds):
        self.inds_set = set(inds)
        self.inds_list = list(self.inds_set)

    def is_active(self, ind):
        return ind in self.inds_set


class GtGCache():
    def __init__(self, G):
        self.G = G
        self.Gt = G.T
        self.size = 100
        self.GtG = np.empty((self.size, self.size), dtype=self.G.dtype)
        self.active = {}
        self.active_list = []
        self.n = 0

    def expand_cache(self):
        new_cache = np.empty((2 * self.size, 2 * self.size), dtype=self.G.dtype)
        new_cache[:self.size, :self.size] = self.GtG
        self.size *= 2
        self.GtG = new_cache

    def add_index(self, index):
        if index not in self.active:
            self.active[index] = self.n
            self.active_list.append(index)
            self.n += 1
            if self.n > self.size:
                self.expand_cache()
            gtg = self.Gt[self.active_list].dot(self.G[:, index])
            self.GtG[self.n-1, :self.n] = gtg
            self.GtG[:self.n, self.n-1] = gtg

    def computeGtG(self, inds):
        ordered_inds = []
        for ind in inds:
            if ind not in self.active:
                self.add_index(ind)
            ordered_inds.append(self.active[ind])
        return self.GtG[ordered_inds][:, ordered_inds]


class ECSWOptimizer():

    def __init__(self, G, b, tau, verbose):
        self.nLines, self.nElem = G.shape
        self.G = G
        self.b = b
        self.G /= self.nElem
        self.b /= self.nElem
        self.Gt = self.G.T
        self.Gtb = np.dot(self.Gt, self.b)
        self.GtG_cache = GtGCache(self.G)
        self.dtype = self.G.dtype
        self.tau = tau
        self.verbose = verbose

    def init_vars(self):
        self.active_inds = ActiveSet()
        self.x = np.zeros((self.nElem, 1), self.dtype)
        self.Gx = np.zeros((self.nLines, 1), self.dtype)
        self.err = np.zeros((self.nLines, 1), self.dtype)
        self.mu = np.zeros((self.nElem, 1), self.dtype)
        self._need_to_compute_err = True
        self._last_added_index = None

    def computeGx(self):
        inds = self.active_inds.get_list()
        GTilde = self.G[:, inds]
        xTilde = self.x[inds]
        np.dot(GTilde, xTilde, out=self.Gx)
        return self.Gx

    def computeErr(self):
        if self._need_to_compute_err:
            np.subtract(self.b, self.computeGx(), out=self.err)
            self._need_to_compute_err = False
        return self.err

    def computeErrNorm(self):
        return np.linalg.norm(self.computeErr())

    def computeEtaTilde(self):
        GtG = self.GtG_cache.computeGtG(self.active_inds.get_list())
        Gtb = self.Gtb[self.active_inds.get_list()]
        return np.linalg.solve(GtG, Gtb)

    def expandActiveSet(self):
        np.dot(self.Gt, self.computeErr(), out=self.mu)
        sorted_inds = np.argsort(self.mu[:, 0])
        for ind in reversed(sorted_inds):
            if not self.active_inds.is_active(ind):
                index = int(ind)
                break
        self.active_inds.add(index)
        self._last_added_index = index

    def updateX(self, etaTilde):
        self.x[self.active_inds.get_list()] = etaTilde
        self._need_to_compute_err = True

    def fixNegativeEtaTilde(self, etaTilde):
        while not np.all(etaTilde > 0.0):
            inds = self.active_inds.get_list()
            xTilde = self.x[inds]
            tmpInds = (etaTilde < 0.0).flatten()
            etaTildeNegative = etaTilde[tmpInds]
            indsNegative = list(np.array(inds)[tmpInds])

            vec1 = self.x[indsNegative]
            vec2 = vec1 - etaTildeNegative
            maxFeasibleStep = np.amin(vec1/vec2)

            self.updateX(xTilde + maxFeasibleStep * (etaTilde - xTilde))
            nonzero = (np.absolute(self.x) >= 1e-12).nonzero()[0]
            new_active_inds = [int(i) for i in nonzero]
            self.active_inds.override(new_active_inds)
            etaTilde = self.computeEtaTilde()
        return etaTilde

    def selectECSW(self):
        self.init_vars()
        currentValue = self.computeErrNorm()
        valTarget = self.tau * currentValue
        marge = currentValue - valTarget

        while (currentValue > valTarget):
            if self.verbose:
                print('Current Error: ', currentValue, ' Target Error: ', valTarget)
            else:
                u.update_progress(round(
                    (100 - ((currentValue - valTarget)*100) / marge) / 100, 4
                ))

            self.expandActiveSet()
            etaTilde = self.computeEtaTilde()
            if not np.all(etaTilde > 0):
                etaTilde = self.fixNegativeEtaTilde(etaTilde)

            self.updateX(etaTilde)
            currentValue = self.computeErrNorm()

        if self.verbose:
            print("Final Error: ", currentValue, " Target Error: ", valTarget)
        else:
            u.update_progress(1)

        return self.active_inds.get_list(), self.x


def readGieFileAndComputeRIDandWeights(gieFilename, RIDFileName, weightsFileName, tol, verbose=False):

    print("###################################################")
    print("Executing readGieFileAndComputeRIDandWeights.py\n")
    print("Arguments :\n")
    print("     INPUT  :")
    print("         -gieFilename    :", gieFilename)
    print("     with arguments    :")
    print("         -tolerance        :", tol, "\n")
    print("     OUTPUT :")
    print("         -RIDFileName                :", RIDFileName)
    print("         -weightsFileName            :", weightsFileName, "\n")
    print("###################################################")

    ###########################################################################

    gie = None

    # Read all the file & store it in GIE
    if verbose:
        print("Reading file : %r" % gieFilename)

    with open(gieFilename, 'r') as fgie:
        nbLines = 0
        lenght = len(fgie.readline().split())
        fgie.seek(0)
        for i, line in enumerate(fgie):
            lineSplit = line.split()
            if lineSplit != ['0']*len(lineSplit):
                nbLines += 1

        gie = np.zeros((nbLines, lenght), dtype=np.float64)
        fgie.seek(0)

        tmp = 0
        for i, line in enumerate(fgie):
            lineSplit = line.split()
            # print(i,len(lineSplit)
            if lineSplit != ['0']*len(lineSplit):
                # print(lineSplit)
                gie[tmp, :] = lineSplit
                tmp += 1

        # np.set_printoptions(precision=5)
        # print("DONE -------------> "+str(gie[0][0]))

        if verbose:
            print("nbLines "+str(nbLines)+"  lenght "+str(lenght))
            print("Done reading file %r:" % gieFilename, '\n')

    # Create bECSW from GIE
    bECSW = np.sum(gie, axis=1)
    bECSW = bECSW[np.newaxis]
    bECSW = np.transpose(bECSW)

    ####################################
    if verbose:
        print("INFO pre-process")
        print("     size cleaned GIE :               ", np.shape(gie))
        print("     size bECSW :                     ", np.shape(bECSW), '\n')
    ####################################

    # Compute RID & Weight
    optimizer = ECSWOptimizer(gie, bECSW, tol, verbose)
    ECSWindex, xi = optimizer.selectECSW()
    ECSWindex = np.array(sorted(list(ECSWindex)))
    sizeRID = ECSWindex.size

    # Store results in files
    np.savetxt(RIDFileName, ECSWindex, header=str(sizeRID)+' 1', comments='', fmt='%d')
    np.savetxt(weightsFileName, xi, header=str(xi.size)+' 1', comments='', fmt='%10.5f')

    if verbose:
        print("===> Success readGieFileAndComputeRIDandWeights.py\n")


###############################################################################

if __name__ == '__main__':  # if we're running file directly and not importing it
    if len(argv) < 5:
        print("Function need at least 4 arguments")
    else:
        readGieFileAndComputeRIDandWeights(*argv[1:])
