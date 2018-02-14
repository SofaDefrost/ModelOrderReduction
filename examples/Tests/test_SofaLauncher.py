#!/usr/bin/python
# coding: utf8 
#############################################################################
# This file is part of Sofa Framework
#
# This script is showing how you can use the launcher.py API to start
# multiple runSofa instance and gather the results. 
# 
# You need the cheetha template engine to use this
# http://www.cheetahtemplate.org/learn.html
#
# Contributors:
#       - damien.marchal@univ-lille.1
#####################################################################
import sys 
import math              
from launcher import *                 

####################      USER PARAM       ##########################
nbActuator = 4
dt = 0.01
increment = [5]*nbActuator
breathTime = [20]*nbActuator
maxPull = [40]*nbActuator

####################     VAR SHAKING      ###########################
nbPossibility = 2**nbActuator
phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
phaseNumClass = []

####################  INIT SCENE SEQUENCES  #########################
timeExe = [0]*nbActuator
for i in range(nbActuator):
    timeExe[i] = dt*((maxPull[i]/increment[i])+1)*breathTime[i]

for i in range(nbPossibility):
    binVal = "{0:b}".format(i)
    for j in range(len(binVal)):
        phaseNum[i][j + nbActuator-len(binVal)] = int(binVal[j])

for nb in range(nbActuator+1):
    for i in range(nbPossibility):
        if sum(phaseNum[i]) == nb:
            phaseNumClass.append(phaseNum[i])

listSofaScene = []
for i in range(nbPossibility):
    listSofaScene.append({"PHASE": phaseNumClass[i], "INCREMENT" : increment, "MAXPULL" : maxPull, "BREATHTIME" : breathTime,"DT" : dt,"nbIterations":timeExe[0]/0.01 })

#####################################################################

print "List of phase :",phaseNumClass
print "Number of Iteration :",timeExe[0]/dt
print "##############"


filenames = ["test_Cheetah.pyscn"]
filesandtemplates = []
for filename in filenames:                
        filesandtemplates.append( (open(filename).read(), filename) )
     
results = startSofa([listSofaScene[1]], filesandtemplates, launcher=ParallelLauncher(4))

for res in results:
       print("Results: ")
       print("    directory: "+res["directory"])
       print("        scene: "+res["scene"])
       print("      logfile: "+res["logfile"])
       print("     duration: "+str(res["duration"])+" sec")  