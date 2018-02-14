#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Sofa
import time, sys
import math
import yaml

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
ymlfile.close()

#Load Actuator config file
with open(cfg['sceneConfigFile'], 'r') as ymlfile:
    sceneConfigFile = yaml.load(ymlfile)
ymlfile.close()

#Load Actuator config file
with open(sceneConfigFile['modelNode']['actuatorConfigFile'], 'r') as ymlfile:
    cfg_Actuator = yaml.load(ymlfile)
ymlfile.close()

#Load MOR config file
with open(cfg['morConfigFile'], 'r') as ymlfile:
    morConfigFile = yaml.load(ymlfile)
ymlfile.close()

verbose =       cfg['other']['verbose']
nbActuator =    len(cfg_Actuator['modelActuator'])

increment =     morConfigFile['actuatorParam']['increment']
modulo =        morConfigFile['actuatorParam']['modulo']
breathTime =    morConfigFile['actuatorParam']['breathTime']

initState =     morConfigFile['stateFile']['initState']

################################################################################################

def update_progress(progress):
    barLength = 40 # Modify this to change the length of the progress bar
    status = "Shake Model"
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress > 1:
        progress = 1
    block = int(round(barLength*progress))
    text = "\r[{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    if progress == 1 :
        text =  text+"\n"
    sys.stdout.write(text)
    sys.stdout.flush()


class interface(Sofa.PythonScriptController):


    def initGraph(self, node):

        print "########################################\n"
        print "shakeDiamondRobotNG arguments :\n"
        print "     nbActuator       :",nbActuator
        print "     increment        :",increment
        print "     modulo           :",modulo
        print "     breathTime       :",breathTime,"\n"
        print "########################################"

        self.node = node
        self.nbActuator = nbActuator
        self.nbPossibility = 2**self.nbActuator
        self.listActuator = []
        
        self.time = 0.0
        self.nbTimesSteps = 0
        self.i = 0              
        self.done = [0] * self.nbActuator
        self.breathTime = breathTime
        self.modulo = modulo      
        self.cptBreath = 0
        self.numStep = -1
        
        self.phaseNum = [[0] * self.nbActuator for i in range(self.nbPossibility)]
        self.phaseNumClass = []

        for i in range(nbActuator):
            self.listActuator.append(node.getChild('Actuator_'+str(i)+'_'+cfg_Actuator['modelActuator'][i]['name']).getObject('actuatorType'))

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

        if initState :
            morConfigFile['stateFile']['initState'] = False
            with open(cfg['morConfigFile'], "w") as f:
                yaml.dump(morConfigFile, f)
            f.close()

    
        if (self.i < self.nbPossibility):
            if verbose : 
                print 'time = ', self.time 
                print 'onBeginAnimationStep %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                print 'We are in phase: ', self.phaseNumClass[self.i], '++++++++++++++++++++++++++++++++'
                print "step:", self.numStep

            listActualValues = []

            for i in range(nbActuator): 
                listActualValues.append(self.listActuator[i].findData('value').value[0][0])

            if (self.numStep - 2) % self.modulo == 0:

                for i in range(nbActuator):

                    if (self.phaseNumClass[self.i][i] == 1):
                        if (listActualValues[i] < cfg_Actuator['modelActuator'][i]['range']['maxPull']):
                            if 'increment' in cfg_Actuator['modelActuator'][i]['range']:
                                listActualValues[i] = listActualValues[i] + cfg_Actuator['modelActuator'][i]['range']['increment']
                            else : 
                                listActualValues[i] = listActualValues[i] + increment
                        else:
                            self.done[i] = 1
                    else:
                        if (listActualValues[i] >= increment):
                            if 'increment' in cfg_Actuator['modelActuator'][i]['range']:
                                listActualValues[i] = listActualValues[i] - cfg_Actuator['modelActuator'][i]['range']['increment']
                            else: listActualValues[i] = listActualValues[i] - increment
                        else:
                            self.done[i] = 1

                    self.listActuator[i].findData('value').value = str(listActualValues[i])
                
                if self.done == [1] * self.nbActuator:
                    if self.cptBreath == self.breathTime:
                        self.i = self.i + 1
                        self.done = [0] * self.nbActuator
                        self.cptBreath = 0
                        if not verbose : update_progress(round(float(self.i ) / self.nbPossibility , 2) )
                    else:
                        self.cptBreath = self.cptBreath + 1
            
            if verbose :
                for i in range(nbActuator):
                    print listActualValues[i]
        # else:
        #     print 'SAMPLING DONE !!!'
