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

# #   STLIB IMPORT
# from stlib.wrapper import Wrapper

# # MOR IMPORT
# from mor.wrapper import MORWrapper
from modelOrderReductionScript import ModelOrderReductionScript

# ### We import our original scene 
# import originalScene 

####################      USER PARAM       ##########################

# A list of what you want to animate in your scene and with which parameters
toAnimate = ["nord","ouest","sud","est"]

nbActuator = len(toAnimate)
increment = [5]*nbActuator
breathTime = [10]*nbActuator
maxPull = [40]*nbActuator

# Where will be all the different results and with which name
stateFilePath = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/1_State_Files/"
stateFileName = "fullStates.state"
modesFilePath = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/2_Modes_Options/"
modesFileName = "test_modes.txt"
pathToWeightsAndRIDdir = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/3_Reduced_Model/"

# Optionnal parameters
verbose = True
dt = 1


actuatorsParam = [
        {'withName' : 'nord',
         'withCableGeometry' : [[0, 97, 45]],
         'withAPullPointLocation' : [0, 10, 30]
        },
        {'withName' : 'ouest',
         'withCableGeometry' : [[-97, 0, 45]],
         'withAPullPointLocation' : [-10, 0, 30]
        },
        {'withName' : 'sud',
         'withCableGeometry' : [[0, -97, 45]],
         'withAPullPointLocation' : [0, -10, 30]
        },
        {'withName' : 'est',
         'withCableGeometry' : [[97, 0, 45]],
         'withAPullPointLocation' : [10, 0, 30]
        }
    ]


####################   SHAKING VARIABLES  ###########################
nbPossibility = 2**nbActuator
phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
phaseNumClass = []

###############################################################################
#                                                                             #
#      We modify the original scene to do the first step of MOR :             #
#   we add animation to each actuators we want for our model                  #
#   add a writeState componant to save the shaking resulting states           #
#                                                                             #
###############################################################################


####################  INIT SCENE SEQUENCES  #########################
nbIterations = [0]*nbActuator
for i in range(nbActuator):
    nbIterations[i] = ((maxPull[i]/increment[i])-1)*breathTime[i]+ (maxPull[i]/increment[i])

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
    listSofaScene.append({"PHASE": phaseNumClass[i], 
                          "INCREMENT" : increment, 
                          "MAXPULL" : maxPull, 
                          "BREATHTIME" : breathTime,
                          "DT" : dt,
                          "ACTUATORPARAM" : actuatorsParam,
                          "nbIterations":nbIterations[0] })

####################    PYTHON SCRIPT       #########################

morScript = ModelOrderReductionScript(  stateFilePath = stateFilePath,
                                        modesFilePath = modesFilePath,
                                        pathToWeightsAndRIDdir = pathToWeightsAndRIDdir,
                                        verbose = verbose )

print "List of phase :",phaseNumClass
print "Number of Iteration :",nbIterations[0]
print "##############"


filenames = ["test_Cheetah.pyscn"]
filesandtemplates = []
for filename in filenames:                
    filesandtemplates.append( (open(filename).read(), filename) )
     
results = startSofa([listSofaScene[15]], filesandtemplates, launcher=ParallelLauncher(4))

for res in results:
    print("Results: ")
    print("    directory: "+res["directory"])
    print("        scene: "+res["scene"])
    print("     duration: "+str(res["duration"])+" sec")  

    with open(stateFilePath+stateFileName, "a") as stateFile:
        currentStateFile = open(res["directory"]+"/stateFile.state", "r") 
        stateFile.write(currentStateFile.read())
        currentStateFile.close()
    stateFile.close()


morScript.readStateFilesAndComputeModes(stateFileName = stateFileName,
                                        modesFileName = modesFileName,
                                        tol = 0.001)