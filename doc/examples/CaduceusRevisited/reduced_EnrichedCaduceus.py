# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract,multiply
try:
    from splib3.numerics import *
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

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

def Reduced_test(
                  attachedTo=None,
                  name="Reduced_test",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
                  scale=[1.0, 1.0, 1.0],
                  surfaceMeshFileName=False,
                  surfaceColor=[1.0, 1.0, 1.0],
                  nbrOfModes=7,
                  hyperReduction=True):
    """
    Object with an elastic deformation law.

        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | argument            | type      | definition                                                                                      |
        +=====================+===========+=================================================================================================+
        | attachedTo          | Sofa.Node | Where the node is created;                                                                      |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | name                | str       | name of the Sofa.Node it will                                                                   |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | rotation            | vec3f     | Apply a 3D rotation to the object in Euler angles.                                              |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | translation         | vec3f     | Apply a 3D translation to the object.                                                           |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | scale               | vec3f     | Apply a 3D scale to the object.                                                                 |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | surfaceMeshFileName | str       | Filepath to a surface mesh (STL, OBJ). If missing there is no visual properties to this object. |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | surfaceColor        | vec3f     | The default color used for the rendering of the object.                                         |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | nbrOfModes          | int       | Number of modes we want our reduced model to work with                                          |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+
        | hyperReduction      | Bool      | Controlled if we have the simple reduction or the hyper-reduction                               |
        +---------------------+-----------+-------------------------------------------------------------------------------------------------+

    """

    modelRoot = attachedTo.addChild(name)

    Snake_MOR = modelRoot.addChild('Snake_MOR')
    Snake_MOR.addObject('EulerImplicitSolver' , rayleighStiffness = '0.1', rayleighMass = '0.1')
    Snake_MOR.addObject('SparseLDLSolver' , name = 'preconditioner')
    Snake_MOR.addObject('GenericConstraintCorrection' , linearSolver = "@preconditioner")
    Snake_MOR.addObject('MechanicalObject' , position = [0]*nbrOfModes, template = 'Vec1d')
    #Snake_MOR.addObject('MechanicalMatrixMapperMOR' , object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + r'/data/listActiveNodes.txt', template = 'Vec1d,Vec1d', usePrecomputedMass = True, timeInvariantMapping2 = True, performECSW = hyperReduction, timeInvariantMapping1 = True, precomputedMassPath = path + r'/data/UniformMass_reduced.txt', nodeToParse = '@./Snake')


    actuatorDummy = modelRoot.addChild('actuatorDummy')
    actuatorDummy.addObject('MechanicalObject' , name = 'actuatorState', template = 'Vec3d')


    Snake = Snake_MOR.addChild('Snake')
    Snake.addObject('MeshVTKLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), rotation = add(rotation,[-90, 0, 0]), translation = add(translation,[0, 5, 0]), name = 'loader', filename = path + r'/mesh/snake0.vtu')
    Snake.addObject('TetrahedronSetTopologyContainer' , src = '@loader')
    Snake.addObject('MechanicalObject')
    Snake.addObject('UniformMass' , totalMass = '1.0')
    Snake.addObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + r'/data/reducedFF_Snake_0_RID.txt', name = 'reducedFF_Snake_0', weightsPath = path + r'/data/reducedFF_Snake_0_weight.txt', youngModulus = '10000.0', modesPath = path + r'/data/modes.txt', performECSW = hyperReduction, method = 'large', poissonRatio = '0.4', nbModes = nbrOfModes)
    Snake.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./MechanicalObject')


    collis = Snake.addChild('collis')
    collis.addObject('MeshOBJLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0, 5, 0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/meca_snake_900tri.obj')
    collis.addObject('Mesh' , src = '@loader', name = 'topo')
    collis.addObject('MechanicalObject' , name = 'CollisModel')
    collis.addObject('TriangleCollisionModel' , selfCollision = True)
    collis.addObject('LineCollisionModel' , selfCollision = True)
    collis.addObject('PointCollisionModel' , selfCollision = True)
    collis.addObject('BarycentricMapping')


    VisuBody = Snake.addChild('VisuBody')
    VisuBody.addObject('MeshOBJLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/snake_body.obj')
    VisuBody.addObject('OglModel' , color = [1, 1, 1, 0.6], src = '@loader', translation = [0, 5, 0], texturename = 'textures/snakeColorMap.png', name = 'VisualBody')
    VisuBody.addObject('BarycentricMapping')


    VisuCornea = Snake.addChild('VisuCornea')
    VisuCornea.addObject('MeshOBJLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/snake_cornea.obj')
    VisuCornea.addObject('OglModel' , src = '@loader', translation = [0, 5, 0], name = 'VisuCornea')
    VisuCornea.addObject('BarycentricMapping')


    VisualEye = Snake.addChild('VisualEye')
    VisualEye.addObject('MeshOBJLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/snake_yellowEye.obj')
    VisualEye.addObject('OglModel' , src = '@loader', translation = [0, 5, 0], name = 'VisualEye')
    VisualEye.addObject('BarycentricMapping')

    return Snake


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SofaPython3","SoftRobots","ModelOrderReduction"],
                        dt=0.02,
                        gravity=[0.0, -981.0, 0.0])
    rootNode.VisualStyle.displayFlags="showForceFields"
    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', printLog='0', tolerance="1e-6", maxIterations="500")
    rootNode.addObject('CollisionPipeline', verbose="0")
    rootNode.addObject('BruteForceBroadPhase', name="N2")
    rootNode.addObject('BVHNarrowPhase')
    rootNode.addObject('CollisionResponse', response="FrictionContactConstraint", responseParams="mu=0.7")
    rootNode.addObject('LocalMinDistance', name="Proximity", alarmDistance="2.5", contactDistance="0.1", angleCone="0.05")

    Reduced_test(rootNode,
                        name="Reduced_test",
                        surfaceMeshFileName=surfaceMeshFileName, hyperReduction=True)
    base = rootNode.addChild("base")
    
    stick = base.addChild("stick")
    stick.addObject('MeshOBJLoader',name="loader", filename="mesh/collision_batons.obj")
    stick.addObject('Mesh', src='@loader', name='topo')
    stick.addObject('MechanicalObject', name='stickCollisModel')
    stick.addObject('LineCollisionModel',simulated="false", moving="false")
    stick.addObject('PointCollisionModel',simulated="false", moving="false")
    stick.addObject('UncoupledConstraintCorrection')
    
    blobs = base.addChild("blobs")
    blobs.addObject('MeshOBJLoader',name="loader", filename="mesh/collision_boules_V3.obj")
    blobs.addObject('Mesh', src='@loader', name='topo')
    blobs.addObject('MechanicalObject', name='blobsCollisModel')
    blobs.addObject('TriangleCollisionModel',simulated="false", moving="false")
    blobs.addObject('LineCollisionModel',simulated="false", moving="false")
    blobs.addObject('PointCollisionModel',simulated="false", moving="false")
    blobs.addObject('UncoupledConstraintCorrection')

    foot = base.addChild("foot")
    foot.addObject('MeshOBJLoader',name="loader", filename="mesh/collision_pied.obj")
    foot.addObject('Mesh', src='@loader', name='topo')
    foot.addObject('MechanicalObject', name='footCollisModel')
    foot.addObject('TriangleCollisionModel',simulated="false", moving="false")
    foot.addObject('LineCollisionModel',simulated="false", moving="false")
    foot.addObject('PointCollisionModel',simulated="false", moving="false")
    foot.addObject('UncoupledConstraintCorrection')
    
    visu = base.addChild("visu")
    visu.addObject('MeshOBJLoader', name="SOFA_pod", filename="mesh/SOFA_pod.obj", handleSeams="1" )
    visu.addObject('OglModel' , src = '@SOFA_pod', name = 'VisuPOD',color=[1,69.0/255.0,0])

