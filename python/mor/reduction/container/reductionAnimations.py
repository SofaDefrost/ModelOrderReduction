# -*- coding: utf-8 -*-

import math, os

path = os.path.dirname(os.path.abspath(__file__))
pathToAnimation = path+"/../../animation/shakingAnimations.py"

class ReductionAnimations():
    """
    **Contain all the parameters & functions related to the animation of the reduction**

    """
    def __init__(self,listObjToAnimate,listPathToAnimation=[]):

        # A list of what you want to animate in your scene and with which parameters
        self.listObjToAnimate = listObjToAnimate
        self.listPathToAnimation = [pathToAnimation] + listPathToAnimation

        self.listOfLocation = []
        for obj in self.listObjToAnimate:
            self.listOfLocation.append(obj.location)

        self.nbActuator = len(self.listObjToAnimate) 
        self.nbPossibility = 2**self.nbActuator


        self.nbIterations = 0
        self.setNbIteration()

        self.phaseNumClass = None
        self.generateListOfPhase(self.nbPossibility,self.nbActuator)

    def setNbIteration(self,nbIterations=None):
        '''
        '''

        if nbIterations :
            self.nbIterations = int(math.ceil(nbIterations))
        else :
            for obj in self.listObjToAnimate:
                tmp = 0
                if all (k in obj.params for k in ("incr","incrPeriod")):
                    if obj.params['incr'] == 0:
                        print("[WARNING]: 'incr' is 0 for an object. Please check. 'incr' has been set temporary to 1.")
                        obj.params['incr'] = 1
                    tmp = ((obj.params['rangeOfAction']/obj.params['incr'])-1)*obj.params['incrPeriod'] + 2*obj.params['incrPeriod']-1
                if tmp > self.nbIterations:
                    self.nbIterations = int(math.ceil(tmp))

    def generateListOfPhase(self,nbPossibility,nbActuator):
        '''
        '''

        phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
        phaseNumClass = []
        for i in range(nbPossibility):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                phaseNum[i][j + nbActuator-len(binVal)] = int(binVal[j])

        for nb in range(nbActuator+1):
            for i in range(nbPossibility):
                if sum(phaseNum[i]) == nb:
                    phaseNumClass.append(phaseNum[i])

        self.phaseNumClass = phaseNumClass