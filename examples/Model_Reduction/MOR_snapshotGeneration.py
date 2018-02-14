import Sofa

import os
import sys
import yaml

import sceneGeneration

path = os.path.dirname(os.path.abspath(__file__))+'/'
################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
ymlfile.close()

#Load Scene config file
with open(cfg['sceneConfigFile'], 'r') as ymlfile:
    sceneConfigFile = yaml.load(ymlfile)
ymlfile.close()

#Load MOR config file
with open(cfg['morConfigFile'], 'r') as ymlfile:
    morConfigFile = yaml.load(ymlfile)
ymlfile.close()

initState =          morConfigFile['stateFile']['initState']
stateFileName =      morConfigFile['stateFile']['nameStateFile']
stateFilePath =      path + morConfigFile['stateFile']['pathTodir']

robotPath =          sceneConfigFile['modelNode']['pathTodir']
nameRobotMesh =      sceneConfigFile['modelNode']['nameModelMesh']
nameRobotStl =       sceneConfigFile['modelNode']['nameModelVisu']
actuatorConfigFile = sceneConfigFile['modelNode']['actuatorConfigFile']

if initState :
    stateFileName = stateFileName+"_init.state"
else :
    stateFileName = stateFileName+".state"

print "###################################################\n"
print "DiamondRobot_snapshotGeneration arguments :\n"
print "     INPUT  :"
print "     in robotPath      :",robotPath
print "         -nameRobotStl   :",nameRobotStl
print "         -nameRobotMesh  :",nameRobotMesh
print "     with arguments    :"
print "         -actuatorConfigFile :",actuatorConfigFile
print "         -sceneConfigFile    :",cfg['sceneConfigFile']
print "         -initState :",initState,"\n"
print "     OUTPUT :"
print "     in stateFilePath  :",stateFilePath
print "         stateFileName   :",stateFileName,"\n"
print "###################################################"
################################################################################################


collision = False
GREEN = "\033[1;32m"
ENDL  = '\033[0m'
print GREEN + "[INFO]" + ENDL + " [Scene]:" + " If the computation is slow, it might be because you did not add sparse and metis to sofa configuration."
print GREEN + "[INFO]" + ENDL + " [Scene]:" + " (please refer to the README file for more informations)"

def createScene(rootNode):

    #InstantiateRootNode
        rootNode = sceneGeneration.instantiateRootNode(rootNode,sceneConfigFile)
        if 'collision' in sceneConfigFile['rootNode'] :
             rootNode = sceneGeneration.planeNode(rootNode)
    #InstantiateModel
        solverNode = sceneGeneration.instanciateSolver(rootNode,sceneConfigFile)

    #model

        model = sceneGeneration.instantiateModelLight(solverNode,sceneConfigFile)

    #Forcefield
        if 'ForceField' in sceneConfigFile['modelNode']:
            model = sceneGeneration.instanciateForceField(model,sceneConfigFile)

    #BoxROI
        if 'BoxROI' in sceneConfigFile['modelNode']:
            if 'SubTopo' in sceneConfigFile['modelNode']:
                sceneGeneration.instanciateBoxROI(model,sceneConfigFile,'modelSubTopo')
            else :                 
                sceneGeneration.instanciateBoxROI(model,sceneConfigFile)

    #Solver
        if 'linearSolver' in sceneConfigFile['modelNode']:
            model.createObject('LinearSolverConstraintCorrection', solverName=sceneConfigFile['modelNode']['linearSolver']) #have to be after forcefield

    #PythonScriptController
        if 'pythonControllers' in sceneConfigFile['modelNode'] :
            model = sceneGeneration.instanciatePythonScriptController(model,sceneConfigFile)

    #CollisionModel
        if 'collision' in sceneConfigFile['rootNode']:
            model = sceneGeneration.instanciateCollisionModel(model,sceneConfigFile)

    #Visualization 
        if 'nameModelVisu' in sceneConfigFile['modelNode']: 
            model = sceneGeneration.instantiateVisu(model,sceneConfigFile)

    #Actuator
        if 'actuatorConfigFile' in sceneConfigFile['modelNode']: 
            model = sceneGeneration.instantiateActuators(model,sceneConfigFile['modelNode']['actuatorConfigFile'])
    

        if initState :
            # writeX0 = True to take the first pose
            model.createObject('WriteState', filename=stateFilePath+stateFileName, period='0.01',writeX="0", writeX0="1", writeV="0")
        else : 
            model.createObject('WriteState', filename=stateFilePath+stateFileName, period='0.1',writeX="1", writeX0="", writeV="0") 

        return rootNode