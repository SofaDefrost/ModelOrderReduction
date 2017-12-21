 
import Sofa

import os
pathSceneFile = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(os.path.abspath(__file__))+'/Mesh/'
#meshRobot=path+'siliconeV0.vtu'
#meshRobot=path+'myDiamondFairlyFine.vtu'
meshRobot=path+'myDiamondQuiteFine.vtu'
#modesRobot=pathSceneFile + '/modes_Options/modes_DiamondCoarse.txt'
#modesRobot=pathSceneFile + '/modes_Options/modes_DiamondFairlyFine.txt'
#modesRobot=pathSceneFile + '/modes_Options/modes_DiamondFairlyFineNGaccurate.txt'
#modesRobot=pathSceneFile + '/modes_Options/modes_DiamondQuiteFine.txt'
#modesRobot=pathSceneFile + '/modes_Options/modesDiamondQuiteFineWellConverged.txt'
modesRobot=pathSceneFile + '/modes_Options/modesDiamondQuiteFineWellConvergedIniRest.txt'

#RIDfile = pathSceneFile + '/ECSWdata_stored/reducedIntegrationDomain_diamondWellConvergedIniRest21Modes01Tol.txt'
#RIDfile = pathSceneFile + '/ECSWdata_stored/reducedIntegrationDomain_diamondWellConvergedIniRest21Modes003Tol.txt'
#RIDfile = pathSceneFile + '/ECSWdata_stored/reducedIntegrationDomain_diamondWellConvergedIniRest01Tol.txt'
#RIDfile = pathSceneFile + '/ECSWdata_stored/reducedIntegrationDomain_diamondWellConvergedIniRest005Tol.txt'
RIDfile = pathSceneFile + '/ECSWdata_stored/reducedIntegrationDomain_diamondWellConvergedIniRest003Tol.txt'

#weightsFile = pathSceneFile + '/ECSWdata_stored/weights_diamondWellConvergedIniRest21Modes01Tol.txt'
#weightsFile = pathSceneFile + '/ECSWdata_stored/weights_diamondWellConvergedIniRest21Modes003Tol.txt'
#weightsFile = pathSceneFile + '/ECSWdata_stored/weights_diamondWellConvergedIniRest01Tol.txt'
#weightsFile = pathSceneFile + '/ECSWdata_stored/weights_diamondWellConvergedIniRest005Tol.txt'
weightsFile = pathSceneFile + '/ECSWdata_stored/weights_diamondWellConvergedIniRest003Tol.txt'

#listActiveNodesFile = pathSceneFile + '/ECSWdata_stored/listActiveNodes_diamondWellConvergedIniRest21Modes01Tol.txt'
#listActiveNodesFile = pathSceneFile + '/ECSWdata_stored/listActiveNodes_diamondWellConvergedIniRest21Modes003Tol.txt'
#listActiveNodesFile = pathSceneFile + '/ECSWdata_stored/listActiveNodes_diamondWellConvergedIniRest01Tol.txt'
#listActiveNodesFile = pathSceneFile + '/ECSWdata_stored/listActiveNodes_diamondWellConvergedIniRest005Tol.txt'
listActiveNodesFile = pathSceneFile + '/ECSWdata_stored/listActiveNodes_diamondWellConvergedIniRest003Tol.txt'


#nbModes = 21
nbModes = 34
modesPositionStr = '0'
for i in range(1,nbModes):
    modesPositionStr = modesPositionStr + ' 0'
    
prepareECSWBool = "false"

performECSWBool = "false"
performECSWBoolMappedMatrix = "false"


def createScene(rootNode):

 	  # Root node
            #                rootNode.findData('dt').value=1
            rootNode.findData('dt').value=0.01

            rootNode.findData('gravity').value='0 0 -9810'
            rootNode.createObject('VisualStyle', displayFlags='showCollision showVisualModels showForceFields showInteractionForceFields hideCollisionModels hideBoundingCollisionModels hideWireframe')

            #Required plugin
            rootNode.createObject('RequiredPlugin', pluginName='SoftRobots')
            rootNode.createObject('RequiredPlugin', pluginName='ModelOrderReduction')

            rootNode.createObject('FreeMotionAnimationLoop')
            rootNode.createObject('GenericConstraintSolver', tolerance="1e-5", maxIterations="100")
            #rootNode.createObject('QPInverseProblemSolver', name="QP", printLog='0')


            #goal.createObject('UncoupledConstraintCorrection')


            solverNode = rootNode.createChild('solverNode')
            solverNode.createObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
            solverNode.createObject('SparseLDLSolver', name="ldlsolveur")
            solverNode.createObject('GenericConstraintCorrection', solverName='ldlsolveur')


            #feuille
            feuilleMOR = solverNode.createChild('feuilleMOR')

            feuilleMOR.createObject('MechanicalObject', template='Vec1d',name='alpha', position=modesPositionStr)

            feuille = feuilleMOR.createChild('feuille')
            feuille.createObject('MeshVTKLoader', name="loader", filename=meshRobot) 
            feuille.createObject('Mesh',name='meshInput', src="@loader")
            feuille.createObject('MechanicalObject', name="tetras", template="Vec3d", showIndices="false", showIndicesScale="4e-5", rx="90", dz="35")
            feuille.createObject('ModelOrderReductionMapping', input='@../alpha', output='@./tetras',modesPath=modesRobot,listActiveNodesPath="ECSWdata_stored/listActiveNodes_Diamond.txt",performECSW="false",printLog="0")
            feuille.createObject('UniformMass', name="diamondMass",totalmass="0.5")
            feuille.createObject('TetrahedronFEMForceField', youngModulus="450", poissonRatio="0.45")
            feuille.createObject('BoxROI', name="boxROI", box="-15 -15 -40  15 15 10", drawBoxes="true")
            feuille.createObject('PythonScriptController', classname="interface", filename="pythonControllers/shakeDiamondRobotNG.py")
            #                feuille.createObject('FixedConstraint', indices="@boxROI.indices")
            #feuille.createObject('WriteState', filename="output/DiamondQuiteECSWcheckMate.state", period='1',writeX="1", writeV="0")
            solverNode.createObject('MappedMatrixForceFieldAndMass', template='Vec1d,Vec1d', object1='@./feuilleMOR/alpha', object2='@./feuilleMOR/alpha', mappedForceField='@./feuilleMOR/feuille/DiamondWellConverged_HyperElasticHyperReducedFF_Quite_'+ str(nbModes) ,  mappedMass='@./feuilleMOR/feuille/diamondMass', performECSW=performECSWBoolMappedMatrix, listActiveNodesPath=listActiveNodesFile, timeInvariantMapping = 'true', saveReducedMass="false", usePrecomputedMass="true", precomputedMassPath='ECSWdata_stored/diamondMass_reduced34modes.txt', printLog="0")
            #feuille/controlledPoints
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


            visuNode = feuille.createChild("visuNode")
            visuNode.createObject("OglModel",filename=path+"surface.stl", template='ExtVec3f', color='0.7 0.7 0.7 0.6',rotation="90 0 0", translation="0 0 35")
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
                
