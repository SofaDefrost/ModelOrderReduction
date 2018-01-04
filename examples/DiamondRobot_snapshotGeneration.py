import Sofa

import os
import sys
import yaml

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

initState =         cfg['stateFile']['initState']
stateFileName =     cfg['stateFile']['nameStateFile']
stateFilePath =     cfg['stateFile']['pathTodir']
robotPath =         cfg['robotParam']['pathTodir']
nameRobotMesh =     cfg['robotParam']['nameRobotMesh']
nameRobotStl =      cfg['robotParam']['nameRobotStl']

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
print "         -initState :",initState,"\n"
print "     OUTPUT :"
print "     in stateFilePath  :",stateFilePath
print "         stateFileName  :",stateFileName,"\n"
print "###################################################"


################################################################################################

GREEN = "\033[1;32m"
ENDL  = '\033[0m'
print GREEN + "[INFO]" + ENDL + " [Scene]:" + " If the computation is slow, it might be because you did not add sparse and metis to sofa configuration."
print GREEN + "[INFO]" + ENDL + " [Scene]:" + " (please refer to the README file for more informations)"

def createScene(rootNode):

    #Required plugin
        rootNode.createObject('RequiredPlugin', pluginName='SoftRobots')
        #rootNode.createObject('RequiredPlugin', pluginName='SofaPardisoSolver')

    #Root node
        rootNode.findData('dt').value=1
        #rootNode.findData('dt').value=0.01
        rootNode.findData('gravity').value='0 0 -9810'
        rootNode.createObject('VisualStyle', displayFlags=
                'showCollision hideVisualModels showForceFields showInteractionForceFields hideCollisionModels hideBoundingCollisionModels hideWireframe')
        rootNode.createObject('BackgroundSetting')
        rootNode.createObject('FreeMotionMasterSolver')
        rootNode.createObject('GenericConstraintSolver', tolerance="1e-12", maxIterations="10000")

    #Feuille
        feuille = rootNode.createChild('feuille')
        feuille.createObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
        feuille.createObject('ShewchukPCGLinearSolver', 
            iterations="1",
            name="linearsolver", 
            tolerance="1e-5",
            preconditioners="preconditioner",
            use_precond="true",
            update_step="1")
        feuille.createObject('MeshVTKLoader', name="loader", filename=robotPath+nameRobotMesh) 
        feuille.createObject('TetrahedronSetTopologyContainer', src="@loader")
        feuille.createObject('TetrahedronSetGeometryAlgorithms', drawTetrahedra="false", template="Vec3d")
        feuille.createObject('MechanicalObject', name="tetras", template="Vec3d", showIndices="false", showIndicesScale="4e-5", rx="90", dz="35")
        feuille.createObject('UniformMass', totalmass="0.5")
        feuille.createObject('TetrahedronFEMForceField', youngModulus="450", poissonRatio="0.45")

        poissonRatio = 0.45
        youngModulus = 450
        mu_ = youngModulus/(2*(1+poissonRatio))
        lambda_ = youngModulus*poissonRatio/((1-2*poissonRatio)*(1+poissonRatio))
        k0_ = youngModulus/(3*(1-2*poissonRatio))
        c_1 = 250
        c_2 = 2*mu_ - c_1
        alpha1_ = 2
        #feuille.createObject('TetrahedronHyperelasticityFEMForceField',materialName="StVenantKirchhoff", ParameterSet=str(mu_) + " " + str(lambda_),AnisotropyDirections="")
        #feuille.createObject('TetrahedronHyperelasticityFEMForceField',materialName="NeoHookean", ParameterSet=str(mu_) + " " + str(k0_), AnisotropyDirections="")              
        #feuille.createObject('TetrahedronHyperelasticityFEMForceField',materialName="MooneyRivlin", ParameterSet=str(c_1) + " " + str(c_2) + " " + str(k0_), AnisotropyDirections="", printLog="1")    
        #feuille.createObject('TetrahedronHyperelasticityFEMForceField',materialName="Ogden", ParameterSet=str(k0_) + " " + str(mu_) + " " + str(alpha1_), AnisotropyDirections="")              


        feuille.createObject('BoxROI', name="boxROI", box="-15 -15 -40  15 15 10", drawBoxes="true")
        feuille.createObject('FixedConstraint', indices="@boxROI.indices")
        feuille.createObject('BoxROI', name="boxROIArms", box="-100 -100 60  100 100 70", drawBoxes="true")

        feuille.createObject('SparseLDLSolver', name="preconditioner")
        #feuille.createObject('SparsePARDISOSolver', name="preconditioner", symmetric="1")

        feuille.createObject('PythonScriptController', classname="interface", filename="pythonControllers/shakeDiamondRobotNG.py")
        #feuille.createObject('PythonScriptController', classname="measureHeight", filename="pythonControllers/measureHeight.py")
        feuille.createObject('LinearSolverConstraintCorrection', solverName="preconditioner")

        if initState :
            # writeX0 = True to take the first pose
            feuille.createObject('WriteState', filename=stateFilePath+stateFileName, period='0.1',writeX="0", writeX0="1", writeV="0")
        else : 
            feuille.createObject('WriteState', filename=stateFilePath+stateFileName, period='10',writeX="1", writeX0="", writeV="0") 

    #Feuille/controlledPoints
        controlledPoints = feuille.createChild('controlledPoints')
        controlledPoints.createObject('MechanicalObject', name="actuatedPoints", template="Vec3d", position="0 0 125   0 97 45   -97 0 45   0 -97 45  97 0 45")

        for i in range(len(cfg['robotActuator'])) :
            controlledPoints.createObject(cfg['robotActuator'][i]['type'],
                name=cfg['robotActuator'][i]['name'],
                indices=str(i+1),
                pullPoint=cfg['robotActuator'][i]['pullPoint'],
                valueType="displacement",
                value="0")

        # for actuator "est" why no value for valueTypev and value ???

        controlledPoints.createObject('BarycentricMapping', mapForces="false", mapMasses="false")

    #Visu
        visuNode = feuille.createChild("visuNode")
        visuNode.createObject("OglModel",filename=robotPath+nameRobotStl, template='ExtVec3f', color='0.7 0.7 0.7 0.6',rotation="90 0 0", translation="0 0 35")
        visuNode.createObject("BarycentricMapping")


    #Goal Top/Arm
        goalTop = feuille.createChild('goalTop')
        goalTop.createObject('MechanicalObject', name='goalMO', position='0 0 125')
        goalTop.createObject('Sphere', radius='3', group='1')
        goalTop.createObject('BarycentricMapping')

        goalArm = feuille.createChild('goalArm')
        goalArm.createObject('MechanicalObject', name='goalMO', position='0 60 80   -60 0 80   0 -60 80   60 0 80')
        goalArm.createObject('Sphere', radius='3', group='1')
        goalArm.createObject('BarycentricMapping')

        return rootNode