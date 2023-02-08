# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract,multiply
from splib3.numerics import *
from controller import SofiaLegController

path = os.path.dirname(os.path.abspath(__file__))
meshPath = path + '/mesh/'

def TRSinOrigin(positions,modelPosition,translation,rotation,scale=[1.0,1.0,1.0]):
    posOrigin = subtract(positions , modelPosition)
    if any(isinstance(el, list) for el in positions):
        posOriginTRS = transformPositions(posOrigin,translation,eulerRotation=rotation,scale=scale)
    else:
        posOriginTRS = transformPosition(posOrigin,TRS_to_matrix(translation,eulerRotation=rotation,scale=scale))
    return add(posOriginTRS,modelPosition).tolist()
    
def newBox(positions,modelPosition,translation,rotation,offset,scale=[1.0,1.0,1.0]):
    pos = TRSinOrigin(positions,modelPosition,translation,rotation,scale)
    offset =transformPositions([offset],eulerRotation=rotation,scale=scale)[0]
    return add(pos,offset).tolist()

def Reduced_SofiaLeg(
                  attachedTo=None,
                  name="Reduced_SofiaLeg",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
                  scale=[1.0, 1.0, 1.0],
                  surfaceMeshFileName=False,
                  surfaceColor=[1.0, 1.0, 1.0],
                  poissonRatio=None,
                  youngModulus=300000,
                  totalMass=0.01,
                  controller=None):
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

    SofiaLeg_MOR = attachedTo.addChild(name)
    SofiaLeg_MOR.addObject('EulerImplicitSolver' , firstOrder = '0', name = 'odesolver',rayleighStiffness=0.1,rayleighMass=0.1)
    SofiaLeg_MOR.addObject('SparseLDLSolver' , name = 'preconditioner')
    SofiaLeg_MOR.addObject('MechanicalObject' , position = '0 0 0 0 0 0', template = 'Vec1d')
    SofiaLeg_MOR.addObject('MechanicalMatrixMapperMOR', nodeToParse = '@./SofiaLeg', object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_SofiaLeg.txt', template = 'Vec1d,Vec1d', performECSW = 'True')


    SofiaLeg = SofiaLeg_MOR.addChild('SofiaLeg')
    SofiaLeg.addObject('MeshVTKLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/sofia_leg.vtu')
    SofiaLeg.addObject('TetrahedronSetTopologyContainer' , position = '@loader.position', createTriangleArray = '1', name = 'container', tetrahedra = '@loader.tetrahedra', checkConnexity = '1')
    SofiaLeg.addObject('MechanicalObject' , showIndices = 'false', showIndicesScale = '4e-5', name = 'tetras', template = 'Vec3d', position = '@loader.position')
    SofiaLeg.addObject('UniformMass' , totalMass = totalMass)
    SofiaLeg.addObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_SofiaLeg.txt', name = 'HyperReducedFEMForceField_SofiaLeg', weightsPath = path + '/data/weight_SofiaLeg.txt', youngModulus = youngModulus, modesPath = path + '/data/modes.txt', performECSW = 'True', poissonRatio = '0.45', nbModes = '6')
    SofiaLeg.addObject('BoxROI', name='boxROICollision', orientedBox= newBox(
                                                                    [[-25.0, -41.0, 0],[25.0, -42, 0],[25.0, -39, 0]], [0.0, 0.0, 0.0],
                                                                    translation,rotation,[0, 0, -7.0],scale) + multiply(scale[2],[2.0]).tolist()
                                                                +newBox(
                                                                    [[-25.0, -42, 0],[25.0, -42, 0],[25.0, -39, 0]], [0.0, 0.0, 0.0],
                                                                    translation,rotation,[0, 0, 7.0],scale) + multiply(scale[2],[2.0]).tolist(),
                                                    drawPoints='0', computeEdges='0',computeTriangles='0', computeTetrahedra='0',
                                                    computeHexahedra='0', computeQuad='0',drawSize=5, drawBoxes=False)
    SofiaLeg.addObject('BoxROI' , name= 'boxROIMiddle' , orientedBox= newBox([[-2.5, -8.5, 0], [2.5, -8.5, 0], [2.5, -3.5, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.0],scale) + multiply(scale[2],[18.0]).tolist(),drawBoxes=False)
    SofiaLeg.addObject('RestShapeSpringsForceField' , external_points = [0, 1, 2], points = '@boxROIMiddle.indices', name = 'actuatorSpring', stiffness = '1e12', external_rest_shape = '@../../'+name+'_actuator/actuatorState')
    SofiaLeg.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/modes.txt', output = '@./tetras')


    SofiaLeg_actuator = attachedTo.addChild(name+'_actuator')
    SofiaLeg_actuator.addObject('MechanicalObject' , position = '@../'+name+'/SofiaLeg/boxROIMiddle.pointsInROI', name = 'actuatorState', template = 'Vec3d')

    ## Visualization
    if surfaceMeshFileName:
        visu = SofiaLeg.addChild('Visual')

        meshType = surfaceMeshFileName.split('.')[-1]
        if meshType == 'stl':
            visu.addObject(  'MeshSTLLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)
        elif meshType == 'obj':
            visu.addObject(  'MeshOBJLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)

        visu.addObject(  'OglModel',
                            src='@loader',
                            template='Vec3d',
                            color=surfaceColor,
                            rotation= add(rotation,[0.0, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 0.0]),
                            scale3d = multiply(scale,[1.0, 1.0, 1.0]))

        visu.addObject('BarycentricMapping')

    if controller != None:
        myController = SofiaLegController(SofiaLeg_actuator)
        myController.init(**controller)

        return SofiaLeg_MOR , myController

    return SofiaLeg_MOR

def createScene(rootNode):
    from stlib3.scene import MainHeader
    surfaceMeshFileName = 'sofia_leg.stl'

    MainHeader(rootNode,plugins=["SofaPython","ModelOrderReduction"],
                        dt=0.01,
                        gravity=[0, -9810, 0])

    Reduced_SofiaLeg(rootNode,
                    name="Reduced_SofiaLeg_blue_1", 
                    rotation=[0, 0.0, 0.0],
                    translation=[0, 0.0, 0.0],
                    surfaceColor=[0.0, 0.0, 1, 0.5],
                    controller={'offset':40},
                    surfaceMeshFileName=surfaceMeshFileName)

    Reduced_SofiaLeg(rootNode,
                    name="Reduced_SofiaLeg_blue_2", 
                    rotation=[0, 0.0, 0.0],
                    translation=[0, 0.0, -40.0],
                    surfaceColor=[0.0, 1, 0, 0.5],
                    controller={},
                    surfaceMeshFileName=surfaceMeshFileName)
