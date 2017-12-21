 
import Sofa

import os
path = os.path.dirname(os.path.abspath(__file__))+'/Mesh/'
#meshRobot=path+'siliconeV0.vtu'
#meshRobot=path+'myDiamondFairlyFine.vtu'
meshRobot=path+'myDiamondQuiteFine.vtu'
#meshRobot=path+'myDiamondFine.vtu'
GREEN = "\033[1;32m "
ENDL  = '\033[0m'
print GREEN + "[INFO]" + ENDL + " [Scene]:" + " If the computation is slow, it might be because you did not add sparse and metis to sofa configuration."
print GREEN + "[INFO]" + ENDL + " [Scene]:" + " (please refer to the README file for more informations)"


def createScene(rootNode):

 	  # Root node
            #                rootNode.findData('dt').value=1
            rootNode.findData('dt').value=0.01
            rootNode.findData('gravity').value='0 0 -9810'
            rootNode.createObject('VisualStyle', displayFlags='showCollision hideVisualModels showForceFields showInteractionForceFields hideCollisionModels hideBoundingCollisionModels hideWireframe')
            rootNode.createObject('BackgroundSetting')
            #Required plugin
            rootNode.createObject('RequiredPlugin', pluginName='SoftRobots')
            rootNode.createObject('RequiredPlugin', pluginName='SofaPardisoSolver')


            rootNode.createObject('FreeMotionMasterSolver')
            rootNode.createObject('GenericConstraintSolver', tolerance="1e-12", maxIterations="10000")

            #goal = rootNode.createChild('goal')
            #goal.createObject('EulerImplicit', firstOrder='1')
            #goal.createObject('CGLinearSolver', iterations='100',threshold="1e-5", tolerance="1e-5")
            #goal.createObject('MechanicalObject', name='goalMO', position='0 0 125')
            #goal.createObject('Sphere', radius='5', group='1')
            #goal.createObject('UncoupledConstraintCorrection')


            #feuille
            feuille = rootNode.createChild('feuille')
            feuille.createObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
            feuille.createObject('ShewchukPCGLinearSolver', iterations="1", name="linearsolver", tolerance="1e-5", preconditioners="preconditioner", use_precond="true", update_step="1")
            feuille.createObject('MeshVTKLoader', name="loader", filename=meshRobot) 
            feuille.createObject('TetrahedronSetTopologyContainer', src="@loader")
            feuille.createObject('TetrahedronSetGeometryAlgorithms', drawTetrahedra="false", template="Vec3d")
            feuille.createObject('MechanicalObject', name="tetras", template="Vec3d", showIndices="false", showIndicesScale="4e-5", rx="90", dz="35")
            feuille.createObject('UniformMass', totalmass="0.5")
            feuille.createObject('TetrahedronFEMForceField', youngModulus="450", poissonRatio="0.45")
            feuille.createObject('BoxROI', name="boxROI", box="-15 -15 -40  15 15 10", drawBoxes="true")
            feuille.createObject('FixedConstraint', indices="@boxROI.indices")
            feuille.createObject('BoxROI', name="boxROIArms", box="-100 -100 60  100 100 70", drawBoxes="true")

            feuille.createObject('SparseLDLSolver', name="preconditioner")
            #feuille.createObject('SparsePARDISOSolver', name="preconditioner", symmetric="1")

            feuille.createObject('PythonScriptController', classname="interface", filename="pythonControllers/shakeDiamondRobotNG.py")
            #feuille.createObject('PythonScriptController', classname="measureHeight", filename="pythonControllers/measureHeight.py")
            feuille.createObject('LinearSolverConstraintCorrection', solverName="preconditioner")
            feuille.createObject('WriteState', filename="output/feuilleQuiteMooneyRivlin.state", period='0.02',writeX="1", writeX0="0", writeV="0")


            #feuille/controlledPoints
            controlledPoints = feuille.createChild('controlledPoints')
            controlledPoints.createObject('MechanicalObject', name="actuatedPoints", template="Vec3d", position="0 0 125   0 97 45   -97 0 45   0 -97 45  97 0 45")
            #controlledPoints.createObject('CableConstraint', name="nord", indices="1", pullPoint="0 10 30", valueType="force", value="4000")
            #controlledPoints.createObject('CableConstraint', name="ouest", indices="2", pullPoint="-10 0 30", valueType="force", value="4000")
            #controlledPoints.createObject('CableConstraint', name="sud", indices="3", pullPoint="0 -10 30", valueType="force", value="4000")
            controlledPoints.createObject('CableConstraint', name="nord", indices="1", pullPoint="0 10 30", valueType="displacement", value="0")
            controlledPoints.createObject('CableConstraint', name="ouest", indices="2", pullPoint="-10 0 30", valueType="displacement", value="0")
            controlledPoints.createObject('CableConstraint', name="sud", indices="3", pullPoint="0 -10 30", valueType="displacement", value="0")
            controlledPoints.createObject('CableConstraint', name="est", indices="4", pullPoint="10 0 30")

            controlledPoints.createObject('BarycentricMapping', mapForces="false", mapMasses="false")

            visuNode = feuille.createChild("visuNode")
            visuNode.createObject("OglModel",filename=path+"surface.stl", template='ExtVec3f', color='0.7 0.7 0.7 0.6',rotation="90 0 0", translation="0 0 35")
            visuNode.createObject("BarycentricMapping")


            goalTop = feuille.createChild('goalTop')
            goalTop.createObject('MechanicalObject', name='goalMO', position='0 0 125')
            #goalTop.createObject('WriteState', filename="output/positionGoalCOARSEfull.state", period='1',writeX="1", writeV="0")
            #goalTop.createObject('WriteState', filename="output/positionGoalFULL.state", period='1',writeX="1", writeV="0")
            #goalTop.createObject('WriteState', filename="output/positionGoalFairlyFULL.state", period='1',writeX="1", writeV="0")
            goalTop.createObject('Sphere', radius='3', group='1')
            goalTop.createObject('BarycentricMapping')

            goalArm = feuille.createChild('goalArm')
            goalArm.createObject('MechanicalObject', name='goalMO', position='0 60 80   -60 0 80   0 -60 80   60 0 80')
            #goalArm.createObject('WriteState', filename="output/positionArmsCOARSEfull.state", period='1',writeX="1", writeV="0")
            #goalArm.createObject('WriteState', filename="output/positionArmsFairlyFULL.state", period='1',writeX="1", writeV="0")
            goalArm.createObject('Sphere', radius='3', group='1')
            goalArm.createObject('BarycentricMapping')

            return rootNode
                
