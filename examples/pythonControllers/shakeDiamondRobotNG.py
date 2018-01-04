#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Sofa
import math


class interface(Sofa.PythonScriptController):

<<<<<<< HEAD
=======
nbActuator = len(cfg['robotActuator'])
increment = cfg['robotParam']['increment']

verbose =cfg['other']['verbose']
>>>>>>> e07ffe2... ADD bash script to generate reduced model

    def initGraph(self, node):
        self.node = node

	#self.mesh  = node.getChild('feuille').getObject("loader")
	#print 'connnnnnnnnnnnnnnnnnnnnecccccctivity'
	#connec = self.mesh.findData('tetrahedra').value
	#print connec[0]
	#print len(connec)
	#fconnec = open('output/connectivity_Diamond.txt','w')
	#for elem in connec:
		#for point in elem:
			#fconnec.write('%s ' % point)
		#fconnec.write('\n')
        #fconnec.close()



<<<<<<< HEAD
	
	self.cableNord  = node.getChild('controlledPoints').getObject("nord")
        self.cableSud   = node.getChild('controlledPoints').getObject("sud")
        self.cableEst   = node.getChild('controlledPoints').getObject("est")
        self.cableOuest = node.getChild('controlledPoints').getObject("ouest")

        self.mechObject = node.getChild('controlledPoints').getObject("actuatedPoints")

=======
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
>>>>>>> e07ffe2... ADD bash script to generate reduced model
        
	self.time = 0.0
	self.nbTimesSteps = 0
	

<<<<<<< HEAD
        self.phaseNum = [[0] * 4 for i in range(16)]
        for i in range(16):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                self.phaseNum[i][j + 4-len(binVal)] = int(binVal[j])
        self.phaseNumClass = []
        for nb in range(5):
            for i in range(16):
=======
        for i in range(nbActuator):
            self.listActuator.append(node.getChild('controlledPoints').getObject(cfg['robotActuator'][i]['name']))

        for i in range(self.nbPossibility):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                self.phaseNum[i][j + self.nbActuator-len(binVal)] = int(binVal[j])

        for nb in range(self.nbActuator+1):
            for i in range(self.nbPossibility):
>>>>>>> e07ffe2... ADD bash script to generate reduced model
                if sum(self.phaseNum[i]) == nb:
                    self.phaseNumClass.append(self.phaseNum[i])
        print len(self.phaseNumClass)            
        print self.phaseNumClass
        
        self.i = 0
        
        self.done = [0] * 4
        self.breathTime = 0
        self.cptBreath = 0
        self.numStep = -1

<<<<<<< HEAD
										   
=======
        if verbose :
            print "phaseNum             :\n",self.phaseNum
            print "Lenght phaseNumClass :",len(self.phaseNumClass)            
            print "phaseNumClass        :\n",self.phaseNumClass
>>>>>>> e07ffe2... ADD bash script to generate reduced model

    def onBeginAnimationStep(self,dt):
        print 'onBeginAnimationStep %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        self.numStep = self.numStep+1
<<<<<<< HEAD
	self.time = self.time + dt
	self.nbTimesSteps = self.nbTimesSteps + 0.1
	print 'time = ', self.time 
=======
        self.nbTimesSteps = self.nbTimesSteps + 0.1
        self.time = self.time + dt

        if cfg['stateFile']['initState'] == True :
            cfg['stateFile']['initState'] = False
            with open("config.yml", "w") as f:
                yaml.dump(cfg, f)

>>>>>>> e07ffe2... ADD bash script to generate reduced model
	
	if (self.i < 16):
            print 'We are in phase: ', self.phaseNumClass[self.i], '++++++++++++++++++++++++++++++++'
            increment = 5
            maxPull = 40

            inputvalueNord = self.cableNord.findData('value')
            inputvalueSud = self.cableSud.findData('value')
            inputvalueEst = self.cableEst.findData('value')
            inputvalueOuest = self.cableOuest.findData('value')
            
            displacementNord = inputvalueNord.value[0][0]
            displacementSud = inputvalueSud.value[0][0]
            displacementEst = inputvalueEst.value[0][0]
            displacementOuest = inputvalueOuest.value[0][0]
            print "step:", self.numStep
            if (self.numStep - 2) % 10 == 0:
                if (self.phaseNumClass[self.i][0] == 1):
                    if (displacementNord < maxPull):
                        displacementNord = displacementNord + increment
                    else:
                        self.done[0] = 1
                else:
                    if (displacementNord >= increment):
                        displacementNord = displacementNord - increment
                    else:
                        self.done[0] = 1
                        
                if (self.phaseNumClass[self.i][1] == 1):
                    if (displacementSud < maxPull):
                        displacementSud = displacementSud + increment
                    else:
                        self.done[1] = 1
                else:
                    if (displacementSud >= increment):
                        displacementSud = displacementSud - increment
                    else:
                        self.done[1] = 1
                
                if (self.phaseNumClass[self.i][2] == 1):
                    if (displacementEst < maxPull):
                        displacementEst = displacementEst + increment
                    else:
                        self.done[2] = 1
                else:
                    if (displacementEst >= increment):
                        displacementEst = displacementEst - increment
                    else:
                        self.done[2] = 1
                        
                if (self.phaseNumClass[self.i][3] == 1):
                    if (displacementOuest < maxPull):
                        displacementOuest = displacementOuest + increment
                    else:
                        self.done[3] = 1
                else:
                    if (displacementOuest >= increment):
                        displacementOuest = displacementOuest - increment
                    else:
                        self.done[3] = 1	


                inputvalueNord.value = str(displacementNord)
                inputvalueSud.value = str(displacementSud)
                inputvalueEst.value = str(displacementEst)
                inputvalueOuest.value = str(displacementOuest)
                
                if ((self.done[0] == 1) and (self.done[1] == 1) and (self.done[2] == 1) and (self.done[3] == 1)):
                    if self.cptBreath == self.breathTime:
                        self.i = self.i + 1
                        self.done = [0] * 4
                        self.cptBreath = 0
                        print "Possibility n°",self.i #'cptBreath Reset to 0 '
                    else:
                        self.cptBreath = self.cptBreath + 1
                        print 'cptBreath -------------------------------->>>>>>>>>>>>>> ', self.cptBreath

            print 'displacementNord ', displacementNord
            print 'displacementSud ', displacementSud	
            print 'displacementEst ', displacementEst	
            print 'displacementOuest ', displacementOuest                                    
        else:
            print 'SAMPLING DONE !!!'
