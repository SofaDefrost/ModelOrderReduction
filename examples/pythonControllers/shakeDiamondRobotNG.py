#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Sofa
import math


class interface(Sofa.PythonScriptController):


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



	
	self.cableNord  = node.getChild('controlledPoints').getObject("nord")
        self.cableSud   = node.getChild('controlledPoints').getObject("sud")
        self.cableEst   = node.getChild('controlledPoints').getObject("est")
        self.cableOuest = node.getChild('controlledPoints').getObject("ouest")

        self.mechObject = node.getChild('controlledPoints').getObject("actuatedPoints")

        
	self.time = 0.0
	self.nbTimesSteps = 0
	

        self.phaseNum = [[0] * 4 for i in range(16)]
        for i in range(16):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                self.phaseNum[i][j + 4-len(binVal)] = int(binVal[j])
        self.phaseNumClass = []
        for nb in range(5):
            for i in range(16):
                if sum(self.phaseNum[i]) == nb:
                    self.phaseNumClass.append(self.phaseNum[i])
        print len(self.phaseNumClass)            
        print self.phaseNumClass
        
        self.i = 0
        
        self.done = [0] * 4
        self.breathTime = 0
        self.cptBreath = 0
        self.numStep = -1

										   

    def onBeginAnimationStep(self,dt):
        print 'onBeginAnimationStep %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        self.numStep = self.numStep+1
	self.time = self.time + dt
	self.nbTimesSteps = self.nbTimesSteps + 0.1
	print 'time = ', self.time 
	
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
                        print 'cptBreath Reset to 0 '
                    else:
                        self.cptBreath = self.cptBreath + 1
                        print 'cptBreath -------------------------------->>>>>>>>>>>>>> ', self.cptBreath

            print 'displacementNord ', displacementNord
            print 'displacementSud ', displacementSud	
            print 'displacementEst ', displacementEst	
            print 'displacementOuest ', displacementOuest                                    
        else:
            print 'SAMPLING DONE !!!'
