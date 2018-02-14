 
import Sofa

import os
import sys
import numpy as np
import yaml

import sceneGeneration
path = os.path.dirname(os.path.abspath(__file__))+'/Mesh/'
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

#Load MOR config file
with open(cfg['morConfigFile'], 'r') as ymlfile:
    morConfigFile = yaml.load(ymlfile)
ymlfile.close()

robotPath =          sceneConfigFile['modelNode']['pathTodir']
nameRobotMesh =      sceneConfigFile['modelNode']['nameModelMesh']
nameRobotStl =       sceneConfigFile['modelNode']['nameModelVisu']

nbModes =                       morConfigFile['nbModes']   
modesRobot =                    morConfigFile['modes']['pathTodir']  + morConfigFile['modes']['modesFileName']

pathToWeightsAndRIDdir =        morConfigFile['weightsAndRID']['pathTodir']
RIDFileName =                   morConfigFile['weightsAndRID']['RIDFileName']
weightsFileName =               morConfigFile['weightsAndRID']['weightsFileName']

RID_subTopoFileName = 'RID_subTopo.txt'
weights_subTopoFileName = 'weights_subTopo.txt'
listActiveNodes_subTopoFileName = 'listActiveNodes_subTopo.txt'

listActiveNodesFileName = morConfigFile['listActiveNodesFileName']
connectivityFileName =  morConfigFile['connectivityFileName']

prepareECSWBool =               morConfigFile['ECSWBool']['prepare']
performECSWBool =               morConfigFile['ECSWBool']['perform']
performECSWBoolMappedMatrix =   morConfigFile['ECSWBool']['performMappedMatrix']

print "###################################################\n"
print "DiamondRobot_snapshotGeneration_PrepareECSW arguments :\n"
print "     INPUT  :"
print "     in robotPath                 :",robotPath
print "         -nameRobotStl                :",nameRobotStl
print "         -nameRobotMesh               :",nameRobotMesh
print "     in modesRobot                :",modesRobot
print "     with arguments    :"
print "         -nbModes                     :",nbModes
print "         -prepareECSWBool             :",prepareECSWBool
print "         -performECSWBool             :",performECSWBool
print "         -performECSWBoolMappedMatrix :",performECSWBoolMappedMatrix,"\n"
print "     OUTPUT :"
print "     in DiamondWellConverged_HyperReducedFF_Quite_"+ str(nbModes)
print "     in "+pathToWeightsAndRIDdir+connectivityFileName,"\n"
print "###################################################"

modesPositionStr = '0'
for i in range(1,nbModes):
    modesPositionStr = modesPositionStr + ' 0'
    
def createScene(rootNode):

    #InstantiateRootNode
        rootNode = sceneGeneration.instantiateRootNode(rootNode,sceneConfigFile)
        if 'collision' in sceneConfigFile['rootNode'] :
             rootNode = sceneGeneration.planeNode(rootNode)

    #Solver
        solverNode = sceneGeneration.instanciateSolver(rootNode,sceneConfigFile)
    
        # arg : if subTopo mappedForceField2
        solverNode.createObject('MappedMatrixForceFieldAndMass',
            template='Vec1d,Vec1d',
            object1='@./modelMOR/MechanicalObject',
            object2='@./modelMOR/MechanicalObject',
            mappedForceField='@./modelMOR/model/DiamondWellConverged_HyperReducedFF_Quite_'+ str(nbModes) ,
            mappedMass='@./modelMOR/model/UniformMass',
            performECSW=performECSWBool,
            listActiveNodesPath=pathToWeightsAndRIDdir+listActiveNodesFileName)

        if 'MappedMatrixForceFieldAndMass' in morConfigFile:
            if 'mappedForceField2' in morConfigFile['MappedMatrixForceFieldAndMass']:
                solverNode.getObject('MappedMatrixForceFieldAndMass').findLink('mappedForceField2').value = '@./modelMOR/model/modelSubTopo/HyperReducedTriangleFEMForceField'
            # solverNode = sceneGeneration.instanciateArg(solverNode,
            #     'MappedMatrixForceFieldAndMass',
            #     morConfigFile['MappedMatrixForceFieldAndMass'])

    #MechanicalObject nbr position mode
        modelMOR = solverNode.createChild('modelMOR')
        modelMOR.createObject('MechanicalObject', template='Vec1d', position=modesPositionStr)

    #model

        model = sceneGeneration.instantiateModelLight(modelMOR,sceneConfigFile)

    #MOR Mapping
        model.createObject('ModelOrderReductionMapping',
            input='@../MechanicalObject',
            output='@./MechanicalObject',
            modesPath=modesRobot,
            performECSW=False)

    #Forcefield
        model.createObject('HyperReducedTetrahedronFEMForceField',
            name='DiamondWellConverged_HyperReducedFF_Quite_'+ str(nbModes),
            prepareECSW=prepareECSWBool,
            performECSW=performECSWBool,
            modesPath=modesRobot,
            RIDPath=pathToWeightsAndRIDdir+RIDFileName,
            weightsPath=pathToWeightsAndRIDdir+weightsFileName) 

        if 'HyperReducedFEMForceField' in morConfigFile:
            model = sceneGeneration.instanciateArg(model,
                'DiamondWellConverged_HyperReducedFF_Quite_'+ str(nbModes),
                morConfigFile['HyperReducedFEMForceField'])

    #BoxROI
        if 'BoxROI' in sceneConfigFile['modelNode']:
            if sceneConfigFile['modelNode']:
                model = sceneGeneration.instanciateBoxROI(model,sceneConfigFile,'modelSubTopo')
            else: 
                model = sceneGeneration.instanciateBoxROI(model,sceneConfigFile)

    #PythonScriptController
        if ('pythonControllers' in sceneConfigFile['modelNode']):
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
    
        tetrahedra = model.getObject('loader').findData("tetrahedra").value
        np.savetxt(pathToWeightsAndRIDdir+connectivityFileName, tetrahedra,fmt='%i')
        print "Saved tetrahedra in", pathToWeightsAndRIDdir+connectivityFileName


        return rootNode
                
