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

### DIAMOND ROBOT PARAM
originalScene = "originalScene.py"
# A list of what you want to animate in your scene and with which parameters
toAnimate = ["nord","ouest","sud","est"]

nbActuator = len(toAnimate)
increment = [5]*nbActuator
breathTime = [10]*nbActuator
maxPull = [40]*nbActuator
addRigidBodyModes = False
nodesToReduce =['/modelNode']
outputDir = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/diamond/"
###

### STARFISH ROBOT PARAM
# originalScene = "quadruped_snapshotGeneration.py"
# # A list of what you want to animate in your scene and with which parameters
# toAnimate = ["centerCavity","rearLeftCavity","rearRightCavity","frontLeftCavity","frontRightCavity"]

# nbActuator = len(toAnimate)
# increment = [350,200,200,200,200]
# breathTime = [2]*nbActuator
# maxPull = [x*10 for x in increment]
# addRigidBodyModes = True
# nodesToReduce =[('/model','/model/modelSubTopo')]
# outputDir = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/strafish/"
###

# Where will be all the different results and with which name

stateFileName = "fullStates.state"
modesFileName = "test_modes.txt"

# The different Tolerance & Nbr of Nodes wanted
tolModes = 0.001
tolGIE =  0.05

# Optionnal parameters
verbose = True


####################   SHAKING VARIABLES  ###########################
nbPossibility = 2**nbActuator
phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
phaseNumClass = []


periodSaveGIE = [x+1 for x in breathTime]
nbTrainingSet = (maxPull[0]/increment[0]) * nbPossibility

####################    PYTHON SCRIPT INIT  #########################

morScript = ModelOrderReductionScript(  outputDir = outputDir, verbose = verbose )

####################  INIT SCENE SEQUENCES  #########################

defaultParamForcefield = {
    'prepareECSW' : True,
    'modesPath': outputDir+modesFileName,
    'periodSaveGIE' : periodSaveGIE[0],
    'nbTrainingSet' : nbTrainingSet}

defaultParamMappedMatrixMapping = {
    'template': 'Vec1d,Vec1d',
    'object1': '@./MechanicalObject',
    'object2': '@./MechanicalObject'}

defaultParamMORMapping = {
    'input': '@../MechanicalObject',
    'modesPath': outputDir+modesFileName}

paramWrapper = []
subTopoList = []
for item in nodesToReduce :
    if isinstance(item,tuple):
        subTopoList.append(nodesToReduce.index(item))
        paramWrapper.append(   (item[0] , 
                               {'subTopo' : 'modelSubTopo',
                                'paramForcefield': defaultParamForcefield.copy(),
                                'paramMORMapping': defaultParamMORMapping.copy(),
                                'paramMappedMatrixMapping': defaultParamMappedMatrixMapping.copy()} ) )

        paramWrapper.append(  (item[1] ,{'paramForcefield': defaultParamForcefield.copy()} ) )
    else:
        paramWrapper.append(   (item , 
                               {'paramForcefield': defaultParamForcefield.copy(),
                                'paramMORMapping': defaultParamMORMapping.copy(),
                                'paramMappedMatrixMapping': defaultParamMappedMatrixMapping.copy()} ) )

gieFilesNames = []
RIDFilesNames = []
weightsFilesNames = [] 
savedElementsFilesNames = []
connectivityFilesNames = []

for path , param in paramWrapper :
    nodeName = path.split('/')[-1]
    gieFilesNames.append('HyperReducedFEMForceField_'+nodeName+'_Gie.txt')
    RIDFilesNames.append('RID_'+nodeName+'.txt')
    weightsFilesNames.append('weight_'+nodeName+'.txt')
    savedElementsFilesNames.append('elmts_'+nodeName+'.txt')
    connectivityFilesNames.append('conectivity_'+nodeName+'.txt')

nbIterations = [0]*nbActuator
for i in range(nbActuator):
    nbIterations[i] = (maxPull[i]/increment[i])*breathTime[i] + (maxPull[i]/increment[i]) 

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
                            'PERIODSAVEGIE' : periodSaveGIE,
                            "nbIterations":nbIterations[0]
        })

print ('periodSaveGIE : '+str(periodSaveGIE[0]))
print ('nbTrainingSet : '+str(nbTrainingSet))
print ('nbIterations : '+str(nbIterations[0]))


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


filenames = ["phase1_snapshots.py",originalScene]
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

    with open(outputDir+stateFileName, "a") as stateFile:
        currentStateFile = open(res["directory"]+"/stateFile.state", "r") 
        stateFile.write(currentStateFile.read())
        currentStateFile.close()
    stateFile.close()

potentialNbrOfModes = morScript.readStateFilesAndComputeModes(  stateFileName = stateFileName,
                                                                modesFileName = modesFileName,
                                                                tol = tolModes,
                                                                addRigidBodyModes = addRigidBodyModes)

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
    listSofaScene[i]['NBROFMODES'] = potentialNbrOfModes
    listSofaScene[i]['NBTRAININGSET'] = nbTrainingSet
    listSofaScene[i]["PARAMWRAPPER"] = paramWrapper

filenames = ["phase2_prepareECSW.py","phase1_snapshots.py",originalScene]
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

try:
    for fileName in savedElementsFilesNames :
        with open(outputDir+fileName, "a") as savedElementsFile:
            currentStateFile = open(results[-1]["directory"]+'/'+fileName, "r") 
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
    for fileName in gieFilesNames :
        with open(outputDir+fileName, "a") as gieFile:
            currentGieFile = open(res["directory"]+'/'+fileName, "r") 
            gieFile.write(currentGieFile.read())
            currentGieFile.close()
        gieFile.close()

activesNodesLists = []
for fileName in gieFilesNames :
    index = gieFilesNames.index(fileName)
    morScript.readGieFileAndComputeRIDandWeights(outputDir+fileName,RIDFilesNames[index],weightsFilesNames[index],tolGIE)
    activesNodesLists.append(morScript.convertRIDinActiveNodes(RIDFilesNames[index],savedElementsFilesNames[index],connectivityFilesNames[index]))

print("PHASE 4 --- %s seconds ---\n" % (time.time() - start_time))
start_time = time.time()

if subTopoList :
    print('there is at least one subTopo : '+str(subTopoList))
    for i in range(len(subTopoList)) :
        nodeName1 , nodeName2 = nodesToReduce[i]
        nodeName1 = nodeName1.split('/')[-1]
        nodeName2 = nodeName2.split('/')[-1]
        # print ('nodeName1 ', nodeName1)
        # print ('nodeName2 ', nodeName2)
        print activesNodesLists[i]
        print '###################\n\n'
        print activesNodesLists[i+1]
        print '===================\n\n'
        activesNodesLists[i] = list(set().union(activesNodesLists[i],activesNodesLists[i+1]))
        print activesNodesLists[i]

        with open(outputDir+'conectivity_'+nodeName1+'.txt', "w") as file:
            for item in activesNodesLists[i]:
              file.write("%i\n" % item)
        file.close()


filenames = ["phase3_test.py",originalScene]

filesandtemplates = []
for filename in filenames:                
    filesandtemplates.append( (open(filename).read(), filename) )


paramWrapper = []
for item in nodesToReduce :

    if isinstance(item,tuple):

        nodeName = item[0].split('/')[-1]
        nodeNameSubTopo = item[1].split('/')[-1]
        tmptParamForcefield = {
            'performECSW': True,
            'modesPath': outputDir+modesFileName,
            'RIDPath': outputDir+'RID_'+nodeName+'.txt',
            'weightsPath': outputDir+'weight_'+nodeName+'.txt'}

        tmptParamForcefieldSubTopo = {
            'performECSW': True,
            'modesPath': outputDir+modesFileName,
            'RIDPath': outputDir+'RID_'+nodeNameSubTopo+'.txt',
            'weightsPath': outputDir+'weight_'+nodeNameSubTopo+'.txt'}

        tmpParamMappedMatrixMapping = {
            'template': 'Vec1d,Vec1d',
            'object1': '@./MechanicalObject',
            'object2': '@./MechanicalObject',
            'listActiveNodesPath': outputDir+'conectivity_'+nodeName+'.txt',
            'performECSW': True}

        paramWrapper.append(   (item[0] , 
                               {'subTopo' : 'modelSubTopo',
                                'paramForcefield': tmptParamForcefield.copy(),
                                'paramMORMapping': defaultParamMORMapping.copy(),
                                'paramMappedMatrixMapping': tmpParamMappedMatrixMapping.copy()} ) )

        paramWrapper.append(  (item[1] ,{'paramForcefield': tmptParamForcefieldSubTopo.copy()} ) )
    else:

        nodeName = item.split('/')[-1]

        tmptParamForcefield = {
            'performECSW': True,
            'modesPath': outputDir+modesFileName,
            'RIDPath': outputDir+'RID_'+nodeName+'.txt',
            'weightsPath': outputDir+'weight_'+nodeName+'.txt'}

        tmpParamMappedMatrixMapping = {
            'template': 'Vec1d,Vec1d',
            'object1': '@./MechanicalObject',
            'object2': '@./MechanicalObject',
            'listActiveNodesPath': outputDir+'conectivity_'+nodeName+'.txt',
            'performECSW': True}

        paramWrapper.append(   (item , 
                               {'paramForcefield': tmptParamForcefield.copy(),
                                'paramMORMapping': defaultParamMORMapping.copy(),
                                'paramMappedMatrixMapping': tmpParamMappedMatrixMapping.copy()} ) )

finalScene = {}
finalScene["ORIGINALSCENE"] = originalScene
finalScene["PARAMWRAPPER"] = paramWrapper
finalScene['NBROFMODES'] = potentialNbrOfModes
finalScene["nbIterations"] = 1

results = startSofa([finalScene], filesandtemplates, launcher=ParallelLauncher(4))

if verbose:
    for res in results:
        print("Results: ")
        print("    directory: "+res["directory"])
        print("        scene: "+res["scene"])
        print("     duration: "+str(res["duration"])+" sec")

print("TOTAL TIME --- %s seconds ---" % (time.time() - total_time))