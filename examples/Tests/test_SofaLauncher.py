# -*- coding: utf-8 -*-

import sys 
import math              
from launcher import *                 

# MOR IMPORT
from modelOrderReductionScript import ModelOrderReductionScript

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

####################   SHAKING VARIABLES  ###########################
nbPossibility = 2**nbActuator
phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
phaseNumClass = []

####################    PYTHON SCRIPT INIT  #########################

morScript = ModelOrderReductionScript(  stateFilePath = stateFilePath,
                                        modesFilePath = modesFilePath,
                                        pathToWeightsAndRIDdir = pathToWeightsAndRIDdir,
                                        verbose = verbose )

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
    listSofaScene.append({
                            "TOANIMATE": toAnimate,
                            "PHASE": phaseNumClass[i],
                            "INCREMENT" : increment,
                            "MAXPULL" : maxPull,
                            "BREATHTIME" : breathTime,
                            "DT" : dt,
                            "nbIterations":nbIterations[0]
        })

####################    SOFA LAUNCHER       ##########################
#                                                                    #
#                           PHASE 1                                  #
#                                                                    #
#      We modify the original scene to do the first step of MOR :    #
#   we add animation to each actuators we want for our model         #
#   add a writeState componant to save the shaking resulting states  #
#                                                                    #
######################################################################
print ("List of phase :",phaseNumClass)
print ("Number of Iteration per phase :",nbIterations[0])
print ("##############")


filenames = ["phase1_snapshots.py"]
filesandtemplates = []
for filename in filenames:                
    filesandtemplates.append( (open(filename).read(), filename) )
     
results = startSofa(listSofaScene, filesandtemplates, launcher=ParallelLauncher(4))


####################    PYTHON SCRIPT       ##########################
#                                                                    #
#                           PHASE 2                                  #
#                                                                    #
#      With the previous result we combine all the generated         #
#       state files into one to be able to extract from it           #
#                       the different mode                           #
#                                                                    #
######################################################################

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

####################    SOFA LAUNCHER       ##########################
#                                                                    #
#                           PHASE 3                                  #
#                                                                    #
#      We launch again a set of sofa scene with the sofa launcher    #
#      with the same previous arguments but with a different scene   #
#      This scene take the previous one and add the model order      #
#      reduction component:                                          #
#            - HyperReducedFEMForceField                             #
#            - MappedMatrixForceFieldAndMass                         #
#            - ModelOrderReductionMapping                            #
#       and produce an Hyper Reduced description of the model        #
#                                                                    #
######################################################################

# filenames = ["phase2_prepareECSW.py"]
# filesandtemplates = []
# for filename in filenames:                
#     filesandtemplates.append( (open(filename).read(), filename) )
     
# results = startSofa(listSofaScene, filesandtemplates, launcher=ParallelLauncher(4))


####################    PYTHON SCRIPT       ##########################
#                                                                    #
#                           PHASE 4                                  #
#                                                                    #
#      Final step : we gather again all the results of the           #
#      previous scenes into one and then compute the RID and Weigts  #
#      with it. Additionnally we also compute the Active Nodes       #
#                                                                    #
######################################################################


# morScript.readGieFileAndComputeRIDandWeights()
# morScript.convertRIDinActiveNodes()