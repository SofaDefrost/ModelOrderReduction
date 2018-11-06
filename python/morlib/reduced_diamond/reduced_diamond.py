# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract
from splib.numerics import *

path = os.path.dirname(os.path.abspath(__file__))

def TRSinOrigin(positions,modelPosition,translation,rotation):
    posOrigin = subtract(positions , modelPosition)
    if any(isinstance(el, list) for el in positions):
        posOriginTRS = transformPositions(posOrigin,translation,rotation)
    else:
        posOriginTRS = transformPosition(posOrigin,TRS_to_matrix(translation,eulerRotation=rotation))
    return add(posOriginTRS,modelPosition).tolist()
    
def newBox(positions,modelPosition,translation,rotation,offset):
    pos = TRSinOrigin(positions,modelPosition,translation,rotation)
    offset =transformPositions([offset],eulerRotation=rotation)[0]
    return add(pos,offset).tolist()
    
def Reduced_diamond(
                  attachedTo=None,
                  name="Reduced_diamond",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
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

        poissonRatio (float):  The poisson parameter.

        youngModulus (float):  The young modulus.

        totalMass (float):   The mass is distributed according to the geometry of the object.
    """

    modelNode_MOR = attachedTo.createChild(name)
    modelNode_MOR.createObject('EulerImplicit')
    modelNode_MOR.createObject('SparseLDLSolver' , name = 'Solver')
    modelNode_MOR.createObject('GenericConstraintCorrection' , solverName = 'Solver')
    modelNode_MOR.createObject('MechanicalObject' , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', template = 'Vec1d')
    modelNode_MOR.createObject('MechanicalMatrixMapperMOR' , object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_modelNode.txt', template = 'Vec1d,Vec1d', performECSW = 'True', nodeToParse = '@./modelNode')


    modelNode = modelNode_MOR.createChild('modelNode')
    modelNode.createObject('MeshVTKLoader' , rotation = add(rotation,[90, 0.0, 0.0]), translation = add(translation,[0.0, 0.0, 35]), name = 'MeshLoader', filename = path + '/mesh/siliconeV0.vtu')
    modelNode.createObject('TetrahedronSetTopologyContainer' , src = '@MeshLoader', name = 'container')
    modelNode.createObject('MechanicalObject' , template = 'Vec3d')
    modelNode.createObject('UniformMass' , totalmass = '0.5')
    modelNode.createObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_modelNode.txt', name = 'HyperReducedFEMForceField_modelNode', weightsPath = path + '/data/weight_modelNode.txt', youngModulus = '450', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.45', nbModes = '28')
    modelNode.createObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/test_modes.txt', output = '@./MechanicalObject')


    nord = modelNode.createChild('nord')
    nord.createObject('MechanicalObject' , position = TRSinOrigin([[0, 97, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    nord.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([0, 10, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    nord.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    ouest = modelNode.createChild('ouest')
    ouest.createObject('MechanicalObject' , position = TRSinOrigin([[-97, 0, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    ouest.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([-10, 0, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    ouest.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    sud = modelNode.createChild('sud')
    sud.createObject('MechanicalObject' , position = TRSinOrigin([[0, -97, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    sud.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([0, -10, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    sud.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    est = modelNode.createChild('est')
    est.createObject('MechanicalObject' , position = TRSinOrigin([[97, 0, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    est.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([10, 0, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    est.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')

    ## Visualization
    if surfaceMeshFileName:

        visu = modelNode.createChild('Visual')
        meshType = surfaceMeshFileName.split('.')[-1]
        if meshType == 'stl':
            visu.createObject(  'MeshSTLLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)
        elif meshType == 'obj':
            visu.createObject(  'MeshObjLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)

        visu.createObject(  'OglModel',
                            src='@loader',
                            template='ExtVec3f',
                            color=surfaceColor,
                            rotation= add(rotation,[90, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 35]))

        visu.createObject('BarycentricMapping')

    return modelNode


#   STLIB IMPORT
from stlib.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = 'surface.stl'

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=1,
                        gravity=[0.0,0.0,-9810])

    translate = 300
    rotationBlue = 60.0
    rotationWhite = 80
    rotationRed = 70

    for i in range(3):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_blue", 
                        rotation=[rotationBlue*i, 0.0, 0.0],
                        translation=[i*translate, 0.0, 0.0],
                        surfaceColor=[0.0, 0.0, 1, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
    for i in range(3):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_white", 
                        rotation=[0.0, rotationWhite*i, 0.0],
                        translation=[i*translate, translate, -translate],
                        surfaceColor=[0.5, 0.5, 0.5, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)

    for i in range(3):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_red", 
                        rotation=[0.0, 0.0, i*rotationRed],
                        translation=[i*translate, 2*translate, -2*translate],
                        surfaceColor=[1, 0.0, 0.0, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
