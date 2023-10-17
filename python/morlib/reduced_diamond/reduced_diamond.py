# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract
from splib3.numerics import *

path = os.path.dirname(os.path.abspath(__file__))

def TRSinOrigin(positions,modelPosition,translation,rotation):
    posOrigin = subtract(positions , modelPosition)
    if any(isinstance(el, list) for el in positions):
        posOriginTRS = transformPositions(posOrigin,translation,eulerRotation=rotation)
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

    modelNode_MOR = attachedTo.addChild(name)
    modelNode_MOR.addObject('EulerImplicitSolver')
    modelNode_MOR.addObject('SparseLDLSolver' , name = 'Solver')
    modelNode_MOR.addObject('GenericConstraintCorrection' , solverName = 'Solver')
    modelNode_MOR.addObject('MechanicalObject' , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', template = 'Vec1d')
    modelNode_MOR.addObject('MechanicalMatrixMapperMOR' , object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_modelNode.txt', template = 'Vec1d,Vec1d', performECSW = 'True', nodeToParse = '@./modelNode')


    modelNode = modelNode_MOR.addChild('modelNode')
    modelNode.addObject('MeshVTKLoader' , rotation = add(rotation,[90, 0.0, 0.0]), translation = add(translation,[0.0, 0.0, 35]), name = 'MeshLoader', filename = path + '/mesh/siliconeV0.vtu')
    modelNode.addObject('TetrahedronSetTopologyContainer' , src = '@MeshLoader', name = 'container')
    modelNode.addObject('MechanicalObject' , template = 'Vec3d')
    modelNode.addObject('UniformMass' , totalMass = '0.5')
    modelNode.addObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_modelNode.txt', name = 'HyperReducedFEMForceField_modelNode', weightsPath = path + '/data/weight_modelNode.txt', youngModulus = '450', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.45', nbModes = '28')
    modelNode.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/test_modes.txt', output = '@./MechanicalObject')


    nord = modelNode.addChild('nord')
    nord.addObject('MechanicalObject' , position = TRSinOrigin([[0, 97, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    nord.addObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([0, 10, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    nord.addObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    ouest = modelNode.addChild('ouest')
    ouest.addObject('MechanicalObject' , position = TRSinOrigin([[-97, 0, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    ouest.addObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([-10, 0, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    ouest.addObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    sud = modelNode.addChild('sud')
    sud.addObject('MechanicalObject' , position = TRSinOrigin([[0, -97, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    sud.addObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([0, -10, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    sud.addObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    est = modelNode.addChild('est')
    est.addObject('MechanicalObject' , position = TRSinOrigin([[97, 0, 45]] , [0.0, 0.0, 35],translation,rotation), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    est.addObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = TRSinOrigin([10, 0, 30] , [0.0, 0.0, 35],translation,rotation), value = '0.0')
    est.addObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')

    ## Visualization
    if surfaceMeshFileName:

        visu = modelNode.addChild('Visual')
        meshType = surfaceMeshFileName.split('.')[-1]
        if meshType == 'stl':
            visu.addObject(  'MeshSTLLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)
        elif meshType == 'obj':
            visu.addObject(  'MeshOBJLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)

        visu.addObject(  'OglModel',
                            src='@loader',
                            template='Vec3d',
                            color=surfaceColor,
                            rotation= add(rotation,[90, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 35]))

        visu.addObject('BarycentricMapping')

    return modelNode


#   STLIB IMPORT
from stlib3.scene import MainHeader
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
