#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Sofa
import math
import yaml

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

nbActuator = len(cfg['robotActuator'])
increment = cfg['robotParam']['increment']

verbose =cfg['other']['verbose']

################################################################################################


class interface(Sofa.PythonScriptController):


    def initGraph(self, node):

        print "########################################\n"
        print "shakeDiamondRobotNG arguments :\n"
        print "     nbActuator      :",nbActuator
        print "     increment       :",increment,"\n"
        print "########################################"

        self.node = node
        self.nbActuator = nbActuator
        self.nbPossibility = 2**self.nbActuator
        self.listActuator = []
        
    	self.time = 0.0
    	self.nbTimesSteps = 0
        self.i = 0
        self.done = [0] * self.nbActuator
        self.breathTime = 0
        self.cptBreath = 0
        self.numStep = -1
        
        self.phaseNum = [[0] * self.nbActuator for i in range(self.nbPossibility)]
        self.phaseNumClass = []

        for i in range(nbActuator):
            self.listActuator.append(node.getChild('controlledPoints').getObject(cfg['robotActuator'][i]['name']))

        for i in range(self.nbPossibility):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                self.phaseNum[i][j + self.nbActuator-len(binVal)] = int(binVal[j])

        for nb in range(self.nbActuator+1):
            for i in range(self.nbPossibility):
                if sum(self.phaseNum[i]) == nb:
                    self.phaseNumClass.append(self.phaseNum[i])

        if verbose :
            print "phaseNum             :\n",self.phaseNum
            print "Lenght phaseNumClass :",len(self.phaseNumClass)            
            print "phaseNumClass        :\n",self.phaseNumClass

    def onBeginAnimationStep(self,dt):
        self.numStep = self.numStep+1
        self.nbTimesSteps = self.nbTimesSteps + 0.1
        self.time = self.time + dt

        if cfg['stateFile']['initState'] == True :
            cfg['stateFile']['initState'] = False
            with open("config.yml", "w") as f:
                yaml.dump(cfg, f)

	
    	if (self.i < self.nbPossibility):
            if verbose : 
                print 'time = ', self.time 
                print 'onBeginAnimationStep %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                print 'We are in phase: ', self.phaseNumClass[self.i], '++++++++++++++++++++++++++++++++'
                print "step:", self.numStep

            listActualValues = []

            for i in range(nbActuator): 
                listActualValues.append(self.listActuator[i].findData('value').value[0][0])

            if (self.numStep - 2) % 10 == 0:

                for i in range(nbActuator):

                    if (self.phaseNumClass[self.i][i] == 1):
                        if (listActualValues[i] < cfg['robotActuator'][i]['range']['maxPull']):
                            listActualValues[i] = listActualValues[i] + increment
                        else:
                            self.done[i] = 1
                    else:
                        if (listActualValues[i] >= increment):
                            listActualValues[i] = listActualValues[i] - increment
                        else:
                            self.done[i] = 1

                    self.listActuator[i].findData('value').value = str(listActualValues[i])
                
                if ((self.done[0] == 1) and (self.done[1] == 1) and (self.done[2] == 1) and (self.done[3] == 1)):
                    if self.cptBreath == self.breathTime:
                        self.i = self.i + 1
                        self.done = [0] * 4
                        self.cptBreath = 0
                        print "Possibility n°",self.i #'cptBreath Reset to 0 '
                    else:
                        self.cptBreath = self.cptBreath + 1
                        print 'cptBreath -------------------------------->>>>>>>>>>>>>> ', self.cptBreath

            
            if verbose :
                for i in range(nbActuator):
                    print listActualValues[i]

        else:
            print 'SAMPLING DONE !!!'
