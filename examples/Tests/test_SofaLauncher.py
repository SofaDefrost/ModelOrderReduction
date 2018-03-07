# -*- coding: utf-8 -*-
import time
import sys 
import math              
from launcher import *                 

sys.path.append('/home/felix/SOFA/plugin/ModelOrderReduction/python') # to change

# MOR IMPORT
from mor.script import ModelOrderReductionScript

total_time = time.time()

####################      USER PARAM       ##########################
originalScene = "originalScene"
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
gieFileName = 'fullGIE.txt'

RIDFileName = 'test_RID.txt'
weightsFileName = 'test_weight.txt' 

savedElementsFileName = 'saved_elements.txt'
connectivityFileName = 'conectivity.txt'

# The different Tolerance & Nbr of Nodes wanted
tolModes = 0.001
tolGIE =  0.05

# Optionnal parameters
verbose = True

####################   SHAKING VARIABLES  ###########################
nbPossibility = 2**nbActuator
phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
phaseNumClass = []


periodSavedGIE = [x+1 for x in breathTime]
nbTrainingSet = (breathTime[0]/increment[0]) * nbPossibility

####################    PYTHON SCRIPT INIT  #########################

morScript = ModelOrderReductionScript(  stateFilePath = stateFilePath,
                                        modesFilePath = modesFilePath,
                                        pathToWeightsAndRIDdir = pathToWeightsAndRIDdir,
                                        verbose = verbose )

####################  INIT SCENE SEQUENCES  #########################
nbIterations = [0]*nbActuator
for i in range(nbActuator):
    nbIterations[i] = (maxPull[i]/increment[i])*breathTime[i] + (maxPull[i]/increment[i]) + 1

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
    listSofaScene.append({  "ORIGINALSCENE": originalScene,
                            "TOANIMATE": toAnimate,
                            "PHASE": phaseNumClass[i],
                            "INCREMENT" : increment,
                            "MAXPULL" : maxPull,
                            "BREATHTIME" : breathTime,
                            'PERIODSAVEDGIE' : periodSavedGIE,
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
start_time = time.time()

if verbose :
    print ("List of phase :",phaseNumClass)
    print ("Number of Iteration per phase :",nbIterations[0])
    print ("##############")


filenames = ["phase1_snapshots.py",originalScene+'.py']
filesandtemplates = []
for filename in filenames:                
    filesandtemplates.append( (open(filename).read(), filename) )


results = startSofa(listSofaScene, filesandtemplates, launcher=ParallelLauncher(4))

if verbose:
    for res in results:
        print("Results: ")
        print("    directory: "+res["directory"])
        print("        scene: "+res["scene"])
        print("     duration: "+str(res["duration"])+" sec")  



print("PHASE 1 --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
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

    with open(stateFilePath+stateFileName, "a") as stateFile:
        currentStateFile = open(res["directory"]+"/stateFile.state", "r") 
        stateFile.write(currentStateFile.read())
        currentStateFile.close()
    stateFile.close()

potentialNbrOfModes = morScript.readStateFilesAndComputeModes(  stateFileName = stateFileName,
                                                                modesFileName = modesFileName,
                                                                tol = tolModes)

if potentialNbrOfModes == -1:
    raise ValueError("problem of execution of readStateFilesAndComputeModes")



print("PHASE 2 --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
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

for i in range(nbPossibility):
    listSofaScene[i]['MODESFILEPATH'] = modesFilePath
    listSofaScene[i]['MODESFILENAME'] = modesFileName
    listSofaScene[i]['NBROFMODES'] = potentialNbrOfModes
    listSofaScene[i]['NBTRAININGSET'] = nbTrainingSet

filenames = ["phase2_prepareECSW.py","phase1_snapshots.py",originalScene+'.py']
filesandtemplates = []
for filename in filenames:                
    filesandtemplates.append( (open(filename).read(), filename) )
     
results = startSofa(listSofaScene[1:], filesandtemplates, launcher=ParallelLauncher(4))

if verbose:
    for res in results:
        print("Results: ")
        print("    directory: "+res["directory"])
        print("        scene: "+res["scene"])
        print("     duration: "+str(res["duration"])+" sec")

try: 
    with open(pathToWeightsAndRIDdir+savedElementsFileName, "a") as savedElementsFile:
        currentStateFile = open(results[-1]["directory"]+'/saved_elements.txt', "r") 
        savedElementsFile.write(currentStateFile.read())
        currentStateFile.close()
    savedElementsFile.close()  
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise



print("PHASE 3 --- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
####################    PYTHON SCRIPT       ##########################
#                                                                    #
#                           PHASE 4                                  #
#                                                                    #
#      Final step : we gather again all the results of the           #
#      previous scenes into one and then compute the RID and Weigts  #
#      with it. Additionnally we also compute the Active Nodes       #
#                                                                    #
######################################################################

for res in results:

    with open(pathToWeightsAndRIDdir+gieFileName, "a") as stateFile:
        currentStateFile = open(res["directory"]+"/HyperReducedFEMForceField_Gie.txt", "r") 
        stateFile.write(currentStateFile.read())
        currentStateFile.close()
    stateFile.close()

morScript.readGieFileAndComputeRIDandWeights(pathToWeightsAndRIDdir+gieFileName,RIDFileName,weightsFileName,tolGIE)
morScript.convertRIDinActiveNodes(RIDFileName,savedElementsFileName,connectivityFileName)

print("PHASE 4 --- %s seconds ---\n" % (time.time() - start_time))

print("TOTAL TIME --- %s seconds ---" % (time.time() - total_time))