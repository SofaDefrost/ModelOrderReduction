# -*- coding: utf-8 -*-
import os
import Sofa
import Sofa.Core
from numpy import add,subtract,multiply
from splib3.numerics import *

path = os.path.dirname(os.path.abspath(__file__))

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
    POD = False
    liver_MOR = attachedTo.addChild(name)
    liver_MOR.addObject('EulerImplicitSolver' , rayleighStiffness=0.1, rayleighMass=0.1)
    liver_MOR.addObject('SparseLDLSolver',name='preconditioner')
    liver_MOR.addObject('GenericConstraintCorrection', solverName='preconditioner')

    if POD:
        liver_MOR.addObject('MechanicalObject' , position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], template = 'Vec1d')
    else:
        liver_MOR.addObject('MechanicalObject' , position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], template = 'Vec1d')
    liver_MOR.addObject('MechanicalMatrixMapperMOR' , object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_liver.txt', template = 'Vec1d,Vec1d', performECSW = True, nodeToParse = '@./liver',printLog=False)


    liver = liver_MOR.addChild('liver')
    if POD:
        liver.addObject('MeshVTKLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/liverSemiFine.vtu')
    else:
        liver.addObject('MeshVTKLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/liverFine.vtu')
    
    liver.addObject('TetrahedronSetTopologyContainer' , src = '@loader')
    liver.addObject('MechanicalObject')
    liver.addObject('TetrahedronSetGeometryAlgorithms')
    liver.addObject('BoxROI' , name= 'ROI1' , orientedBox= newBox([[0.0, 3.0, 0], [2.0, 0, 0], [2.0, 5.0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.5],scale) + multiply(scale[2],[3.0]).tolist(),drawBoxes=True)
    liver.addObject('BoxROI' , name= 'boxROIactuation' , orientedBox= newBox([[-5.0, 0.0, 0], [-4.0, 0, 0], [-4.0, 0.5, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.0],scale) + multiply(scale[2],[1.0]).tolist(),drawBoxes=True)
    liver.addObject('UniformMass' , totalMass = 1.3)
    liver.addObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_liver.txt', name = 'HyperReducedFEMForceField_liver', weightsPath = path + '/data/weight_liver.txt', youngModulus = 5000, modesPath = path + '/data/modes.txt', performECSW =True, poissonRatio = 0.3, nbModes = 10)
    #liver.addObject('RestShapeSpringsForceField' , points = '@ROI1.indices', stiffness = '1e8')
 #   liver.addObject('RestShapeSpringsForceField' , external_points = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], points = '@boxROIactuation.indices', name = 'actuatorSpring', stiffness = '1e8', external_rest_shape = '@actuator/actuatorState')
    if POD:
        liver.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/modes.txt', output = '@./MechanicalObject')
    else:
        #liver.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/normalModesCoarse.txt', output = '@./MechanicalObject')
        liver.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/modes.txt', output = '@./MechanicalObject')
    #liver.addObject('StiffSpringForceField', object1 ='@../../mouseNode/fakeMousPos', object2 ='@./MechanicalObject', rayleighStiffness=0, stiffness=100, spring=[0,194, 1000, 0, 2.5])

    #modelCollis = liver.addChild('modelCollis')
    #modelCollis.addObject('MeshOBJLoader', name='loader', filename=path+'/mesh/'+surfaceMeshFileName)
    #modelCollis.addObject('TriangleSetTopologyContainer', src='@loader', name='container')
    #modelCollis.addObject('MechanicalObject', name='collisMO', template='Vec3d')
    #modelCollis.addObject('TriangleCollisionModel',group="0")
    #modelCollis.addObject('LineCollisionModel',group="0")
    #modelCollis.addObject('PointCollisionModel',group="0")
    #modelCollis.addObject('BarycentricMapping')

    ## Visualization
    print('test surfaceMeshFileName')
    if surfaceMeshFileName:
        print('Its TRUE !!!')
        visu = liver.addChild('Visual')
        visu.addObject(	'OglModel',
                            filename=path+'/mesh/'+surfaceMeshFileName,
                            template='Vec3d',
                            color=surfaceColor,
                            rotation= add(rotation,[0.0, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 0.0]),
                            scale3d = multiply(scale,[1.0, 1.0, 1.0]))
        visu.addObject('BarycentricMapping')

    return liver


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = 'liver-smoothUV.obj'

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=0.01,
                        gravity=[0.0,-981, 0.0])
    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', printLog='0', tolerance="1e-6", maxIterations="500")
    rootNode.addObject('CollisionPipeline', verbose="0")
    rootNode.addObject('BruteForceBroadPhase', name="N2")
    rootNode.addObject('BVHNarrowPhase')
    rootNode.addObject('CollisionResponse', response="FrictionContact", responseParams="mu=0.7")
    rootNode.addObject('LocalMinDistance', name="Proximity", alarmDistance="2.5", contactDistance="0.5", angleCone="0.01")


    Reduced_liver(rootNode,
                        name="Reduced_liver_blue", 
                        rotation=[0.0, 0.0, 0.0],
                        translation=[0.0, 0.0, 0.0],
                        surfaceColor=[0.0, 0.0, 1, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
