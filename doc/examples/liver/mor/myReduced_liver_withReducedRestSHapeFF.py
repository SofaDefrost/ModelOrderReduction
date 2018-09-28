# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract,multiply
from splib.numerics import *

path = os.path.dirname(os.path.abspath(__file__))

def TRSinOrigin(positions,modelPosition,translation,rotation,scale=[1.0,1.0,1.0]):
    posOrigin = subtract(positions , modelPosition)
    if any(isinstance(el, list) for el in positions):
        posOriginTRS = transformPositions(posOrigin,translation,rotation,scale=scale)
    else:
        posOriginTRS = transformPosition(posOrigin,TRS_to_matrix(translation,eulerRotation=rotation,scale=scale))
    return add(posOriginTRS,modelPosition).tolist()
    
def newBox(positions,modelPosition,translation,rotation,offset,scale=[1.0,1.0,1.0]):
    pos = TRSinOrigin(positions,modelPosition,translation,rotation,scale)
    offset =transformPositions([offset],eulerRotation=rotation,scale=scale)[0]
    return add(pos,offset).tolist()

def Reduced_liver(
                  attachedTo=None,
                  name="Reduced_liver",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
                  scale=[1.0, 1.0, 1.0],
                  surfaceMeshFileName=False,
                  surfaceColor=[1.0, 1.0, 1.0],
                  poissonRatio=None,
                  youngModulus=None,
                  totalMass=None):
    """
    Object with an elastic deformation law.

    Args:

        attachedTo (Sofa.Node): Where the node is created;

        name (str) : name of the Sofa.Node it will 

        surfaceMeshFileName (str): Filepath to a surface mesh (STL, OBJ). 
                                   If missing there is no visual properties to this object.

        surfaceColor (vec3f):  The default color used for the rendering of the object.

        rotation (vec3f):   Apply a 3D rotation to the object in Euler angles.

        translation (vec3f):   Apply a 3D translation to the object.

        scale (vec3f): Apply a 3D scale to the object.

        poissonRatio (float):  The poisson parameter.

        youngModulus (float):  The young modulus.

        totalMass (float):   The mass is distributed according to the geometry of the object.
    """

    liver_MOR = attachedTo.createChild(name)
    liver_MOR.createObject('EulerImplicitSolver' , rayleighStiffness = '0.0', rayleighMass = '0.0')
    liver_MOR.createObject('SparseLDLSolver' , saveMatrixToFile = 'False')
    liver_MOR.createObject('MechanicalObject' , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', template = 'Vec1d')
    liver_MOR.createObject('MechanicalMatrixMapperMOR' , object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_liver.txt', template = 'Vec1d,Vec1d', performECSW = True, nodeToParse = '@./liver',usePrecomputedMass=True, precomputedMassPath=path + '/data/UniformMass_reduced.txt', timeInvariantMapping1=True, timeInvariantMapping2=True, printLog=False)


    liver = liver_MOR.createChild('liver')
    liver.createObject('MeshVTKLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/liverFine.vtu')
    liver.createObject('TetrahedronSetTopologyContainer' , src = '@loader')
    liver.createObject('TetrahedronSetGeometryAlgorithms')
    liver.createObject('MechanicalObject')
    liver.createObject('BoxROI' , name= 'ROI1' , orientedBox= newBox([[0.0, 3.0, 0], [2.0, 0, 0], [2.0, 5.0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.5],scale) + multiply(scale[2],[3.0]).tolist(),drawBoxes=True)
    liver.createObject('BoxROI' , name= 'boxROIactuation' , orientedBox= newBox([[-5.0, 0.0, 0], [-4.0, 0, 0], [-4.0, 0.5, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.0],scale) + multiply(scale[2],[1.0]).tolist(),drawBoxes=True)
    liver.createObject('UniformMass' , totalMass = '0.3')
    liver.createObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_liver.txt', name = 'HyperReducedFEMForceField_liver', weightsPath = path + '/data/weight_liver.txt', youngModulus = '5000', modesPath = path + '/data/modes.txt', performECSW = True, poissonRatio = '0.3', nbModes = '20')
    liver.createObject('HyperReducedRestShapeSpringsForceField' , points = '@ROI1.indices', stiffness = '1e8',nbModes = '20', modesPath = path + '/data/modes.txt', performECSW = True, prepareECSW=False, nbTrainingSet=15, periodSaveGIE=10,RIDPath = path + '/data/reducedIntegrationDomain_liverRestShapeFF.txt', weightsPath = path + '/data/weights_liverRestShapeFF.txt')
#    liver.createObject('RestShapeSpringsForceField' , points = '@ROI1.indices', stiffness = '1e8')
    #liver.createObject('RestShapeSpringsForceField' , external_points = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], points = '@boxROIactuation.indices', name = 'actuatorSpring', stiffness = '1e8', external_rest_shape = '@actuator/actuatorState')
    liver.createObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/modes.txt', output = '@./MechanicalObject')


    
    ## Visualization
    if surfaceMeshFileName:
	    visu = liver.createChild('Visual')

	    visu.createObject(	'OglModel', 
	    					filename=path+'/mesh/'+surfaceMeshFileName,
                            template='ExtVec3f',
                            color=surfaceColor,
                            rotation= add(rotation,[0.0, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 0.0]),
                            scale3d = multiply(scale,[1.0, 1.0, 1.0]))

	    visu.createObject('BarycentricMapping')

    return liver


#   STLIB IMPORT
from stlib.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = 'liver-smoothUV.obj'
    rootNode.createObject('RequiredPlugin', name='SofaSparseSolver', pluginName='SofaSparseSolver')


    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=0.01,
                        gravity=[0.0,0.0,-9810])

    translate = 300
    rotationBlue = 60.0
    rotationWhite = 80
    rotationRed = 70


    Reduced_liver(rootNode,
                        name="Reduced_liver_blue", 
                        rotation=[0.0, 0.0, 0.0],
                        translation=[0.0, 0.0, 0.0],
                        surfaceColor=[0.0, 0.0, 1, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
    actuator = rootNode.createChild('actuator')
    actuator.createObject('MechanicalObject' , position = '@../Reduced_liver_blue/liver/boxROIactuation.pointsInROI', name = 'actuatorState', template = 'Vec3d')
    #actuator.createObject('PythonScriptController', filename="washingMachineController.py", classname="washingMachineController")

