 
import Sofa

import os
import sys
import numpy as np
import yaml

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

robotPath =                     cfg['robotParam']['pathTodir']
nameRobotMesh =                 cfg['robotParam']['nameRobotMesh']
nameRobotStl =                  cfg['robotParam']['nameRobotStl']

nbModes =                       cfg['robotParam']['nbModes']   
modesRobot =                    cfg['modes']['pathTodir']  + cfg['modes']['modesFileName']

pathToWeightsAndRIDdir =        cfg['weightsAndRID']['pathTodir']
RIDFileName =                   cfg['weightsAndRID']['RIDFileName']
weightsFileName =               cfg['weightsAndRID']['weightsFileName']

listActiveNodesFileName = "ECSWdata_stored/" + cfg['listActiveNodesFileName']
connectivityFileName =  cfg['connectivityFileName']

prepareECSWBool =               cfg['ECSWBool']['prepare']
performECSWBool =               cfg['ECSWBool']['perform']
performECSWBoolMappedMatrix =   cfg['ECSWBool']['performMappedMatrix']

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

# print "     in pathToWeightsAndRIDdir    :",pathToWeightsAndRIDdir
# print "         -RIDFileName                :",RIDFileName
# print "         -weightsFileName            :",weightsFileName
# print "     -listActiveNodesFileName     :",listActiveNodesFileName

################################################################################################

modesPositionStr = '0'
for i in range(1,nbModes):
    modesPositionStr = modesPositionStr + ' 0'

class saveNodesInfo(Sofa.PythonScriptController):

    def initGraph(self, node):
        
        self.node = node

        tetrahedra = self.node.getObject('loader').findData("tetrahedra").value
        np.savetxt(pathToWeightsAndRIDdir+connectivityFileName, tetrahedra,fmt='%i')
        print "Saved tetrahedra in", pathToWeightsAndRIDdir+connectivityFileName

    
def createScene(rootNode):

    #Required plugin

        rootNode.createObject('RequiredPlugin', pluginName='SoftRobots')
        rootNode.createObject('RequiredPlugin', pluginName='ModelOrderReduction')

    #Root node

        rootNode.findData('dt').value=0.01
        rootNode.findData('gravity').value='0 0 -9810'
        rootNode.createObject('VisualStyle', displayFlags=
            'showCollision showVisualModels showForceFields showInteractionForceFields hideCollisionModels hideBoundingCollisionModels hideWireframe')
        rootNode.createObject('FreeMotionAnimationLoop')
        rootNode.createObject('GenericConstraintSolver', tolerance="1e-5", maxIterations="100")


    #Solver

        solverNode = rootNode.createChild('solverNode')
        solverNode.createObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
        solverNode.createObject('SparseLDLSolver', name="ldlsolveur")
        solverNode.createObject('GenericConstraintCorrection', solverName='ldlsolveur')


    #Feuille

        feuilleMOR = solverNode.createChild('feuilleMOR')

        feuilleMOR.createObject('MechanicalObject', template='Vec1d',name='alpha', position=modesPositionStr)

        feuille = feuilleMOR.createChild('feuille')
        feuille.createObject('MeshVTKLoader', name="loader", filename=robotPath+nameRobotMesh) 
        feuille.createObject('Mesh',name='meshInput', src="@loader")
        feuille.createObject('MechanicalObject', name="tetras", template="Vec3d", showIndices="false", showIndicesScale="4e-5", rx="90", dz="35")
        
        feuille.createObject('ModelOrderReductionMapping',
            input='@../alpha',
            output='@./tetras',
            modesPath=modesRobot,
            listActiveNodesPath="ECSWdata_stored/listActiveNodes_Diamond.txt",
            performECSW="false",
            printLog="0")

        feuille.createObject('UniformMass', name="diamondMass",totalmass="0.5")
        
        feuille.createObject('HyperReducedTetrahedronFEMForceField',
            youngModulus="450",
            poissonRatio="0.45",
            name='DiamondWellConverged_HyperReducedFF_Quite_'+ str(nbModes),
            src="@meshInput",
            prepareECSW=prepareECSWBool,
            performECSW=performECSWBool,
            nbModes=str(nbModes),
            modesPath=modesRobot,
            nbTrainingSet="135",
            periodSaveGIE="10",
            printLog="0") 
        
        feuille.createObject('BoxROI', name="boxROI", box="-15 -15 -40  15 15 10", drawBoxes="true")
        feuille.createObject('PythonScriptController', classname="interface", filename="pythonControllers/shakeDiamondRobotNG.py")

        
        solverNode.createObject('MappedMatrixForceFieldAndMass',
            template='Vec1d,Vec1d',
            object1='@./feuilleMOR/alpha',
            object2='@./feuilleMOR/alpha',
            mappedForceField='@./feuilleMOR/feuille/DiamondWellConverged_HyperReducedFF_Quite_'+ str(nbModes) , 
            mappedMass='@./feuilleMOR/feuille/diamondMass',
            performECSW=performECSWBoolMappedMatrix,
            listActiveNodesPath=pathToWeightsAndRIDdir+listActiveNodesFileName,
            timeInvariantMapping = 'true',
            saveReducedMass="false",
            usePrecomputedMass="false",
            precomputedMassPath='ECSWdata_stored/diamondMass_reduced34modes.txt',
            printLog="0")

    #Save Nodes Info
        feuille.createObject('PythonScriptController', classname="saveNodesInfo")
        
    #Feuille/controlledPoints

        controlledPoints = feuille.createChild('controlledPoints')
        controlledPoints.findData('printLog').value=1
        controlledPoints.createObject('MechanicalObject', name="actuatedPoints", template="Vec3d", position="0 97 45   -97 0 45   0 -97 45  97 0 45")
        controlledPoints.createObject('CableConstraint', name="nord", indices="0", pullPoint="0 10 30")
        controlledPoints.createObject('CableConstraint', name="ouest", indices="1", pullPoint="-10 0 30")
        controlledPoints.createObject('CableConstraint', name="sud", indices="2", pullPoint="0 -10 30")
        #controlledPoints.createObject('CableConstraint', name="nord", indices="0", pullPoint="0 10 30", valueType="displacement", value="40")
        #controlledPoints.createObject('CableConstraint', name="ouest", indices="1", pullPoint="-10 0 30", valueType="displacement", value="40")
        #controlledPoints.createObject('CableConstraint', name="sud", indices="2", pullPoint="0 -10 30", valueType="displacement", value="40")
        controlledPoints.createObject('CableConstraint', name="est", indices="3", pullPoint="10 0 30")

        controlledPoints.createObject('BarycentricMapping', mapForces="false", mapMasses="false")

        if (performECSWBool == 'true'):
            outputGoalName = "positionGoalECSW"
            outputArmsName = "positionArmsECSW"
        else:
            outputGoalName = "positionGoalPOD"
            outputArmsName = "positionArmsPOD"

    #Goal

        goalTop = feuille.createChild('goalTop')
        goalTop.createObject('MechanicalObject', name='goalMO', position='0 0 125')
        #goalTop.createObject('WriteState', filename="output/" + outputGoalName + ".state", period='1',writeX="1", writeV="0")
        goalTop.createObject('Sphere', radius='3', group='1')
        goalTop.createObject('BarycentricMapping')

        goalArm = feuille.createChild('goalArm')
        goalArm.createObject('MechanicalObject', name='goalMO', position='0 60 80   -60 0 80   0 -60 80   60 0 80')
        #goalArm.createObject('WriteState', filename="output/" + outputArmsName + ".state", period='1',writeX="1", writeV="0")
        goalArm.createObject('Sphere', radius='3', group='1')
        goalArm.createObject('BarycentricMapping')

    #Visu

        visuNode = feuille.createChild("visuNode")
        visuNode.createObject("OglModel",filename=robotPath+nameRobotStl, template='ExtVec3f', color='0.7 0.7 0.7 0.6',rotation="90 0 0", translation="0 0 35")
        visuNode.createObject("BarycentricMapping")

        #modelCollis = feuille.createChild('modelCollis')
        #modelCollis.createObject('MeshSTLLoader', name='loader', filename=path+"surface.stl",rotation="90 0 0", translation="0 0 35")
        #modelCollis.createObject('TriangleSetTopologyContainer', src='@loader', name='container')
        #modelCollis.createObject('MechanicalObject', name='collisMO', template='Vec3d')
        #modelCollis.createObject('Triangle',group="0")
        #modelCollis.createObject('Line',group="0")
        #modelCollis.createObject('Point',group="0")
        #modelCollis.createObject('BarycentricMapping')

        return rootNode
                
