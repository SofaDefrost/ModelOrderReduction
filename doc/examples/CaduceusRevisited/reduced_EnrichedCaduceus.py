# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract,multiply
try:
    from splib.numerics import *
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

    modelRoot = attachedTo.createChild(name)

    Snake_MOR = modelRoot.createChild('Snake_MOR')
    Snake_MOR.createObject('EulerImplicitSolver' , rayleighStiffness = '0.1', rayleighMass = '0.1')
    Snake_MOR.createObject('SparseLDLSolver' , name = 'preconditioner')
    Snake_MOR.createObject('GenericConstraintCorrection' , solverName = 'preconditioner')
    Snake_MOR.createObject('MechanicalObject' , position = [0]*nbrOfModes, template = 'Vec1d')
    Snake_MOR.createObject('MechanicalMatrixMapperMOR' , object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + r'/data/listActiveNodes.txt', template = 'Vec1d,Vec1d', usePrecomputedMass = True, timeInvariantMapping2 = True, performECSW = hyperReduction, timeInvariantMapping1 = True, precomputedMassPath = path + r'/data/UniformMass_reduced.txt', nodeToParse = '@./Snake')


    actuatorDummy = modelRoot.createChild('actuatorDummy')
    actuatorDummy.createObject('MechanicalObject' , name = 'actuatorState', template = 'Vec3d')


    Snake = Snake_MOR.createChild('Snake')
    Snake.createObject('MeshVTKLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), rotation = add(rotation,[-90, 0, 0]), translation = add(translation,[0, 5, 0]), name = 'loader', filename = path + r'/mesh/snake0.vtu')
    Snake.createObject('TetrahedronSetTopologyContainer' , src = '@loader')
    Snake.createObject('MechanicalObject')
    Snake.createObject('UniformMass' , totalMass = '1.0')
    Snake.createObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + r'/data/reducedFF_Snake_0_RID.txt', name = 'reducedFF_Snake_0', weightsPath = path + r'/data/reducedFF_Snake_0_weight.txt', youngModulus = '10000.0', modesPath = path + r'/data/modes.txt', performECSW = hyperReduction, method = 'large', poissonRatio = '0.4', nbModes = nbrOfModes)
    Snake.createObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./MechanicalObject')


    collis = Snake.createChild('collis')
    collis.createObject('MeshObjLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0, 5, 0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/meca_snake_900tri.obj')
    collis.createObject('Mesh' , src = '@loader', name = 'topo')
    collis.createObject('MechanicalObject' , name = 'CollisModel')
    collis.createObject('Triangle' , selfCollision = True)
    collis.createObject('Line' , selfCollision = True)
    collis.createObject('Point' , selfCollision = True)
    collis.createObject('BarycentricMapping')


    VisuBody = Snake.createChild('VisuBody')
    VisuBody.createObject('MeshObjLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/snake_body.obj')
    VisuBody.createObject('OglModel' , color = [1, 1, 1, 0.6], src = '@loader', translation = [0, 5, 0], texturename = 'textures/snakeColorMap.png', name = 'VisualBody')
    VisuBody.createObject('BarycentricMapping')


    VisuCornea = Snake.createChild('VisuCornea')
    VisuCornea.createObject('MeshObjLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/snake_cornea.obj')
    VisuCornea.createObject('OglModel' , src = '@loader', translation = [0, 5, 0], name = 'VisuCornea')
    VisuCornea.createObject('BarycentricMapping')


    VisualEye = Snake.createChild('VisualEye')
    VisualEye.createObject('MeshObjLoader' , scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + r'/mesh/snake_yellowEye.obj')
    VisualEye.createObject('OglModel' , src = '@loader', translation = [0, 5, 0], name = 'VisualEye')
    VisualEye.createObject('BarycentricMapping')

    return Snake


#   STLIB IMPORT
from stlib.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=0.02,
                        gravity=[0.0, -981.0, 0.0])
    rootNode.VisualStyle.displayFlags="showForceFields"
    rootNode.createObject('FreeMotionAnimationLoop')
    rootNode.createObject('GenericConstraintSolver', printLog='0', tolerance="1e-6", maxIterations="500")
    rootNode.createObject('CollisionPipeline', verbose="0")
    rootNode.createObject('BruteForceDetection', name="N2")
    rootNode.createObject('CollisionResponse', response="FrictionContact", responseParams="mu=0.7")
    rootNode.createObject('LocalMinDistance', name="Proximity", alarmDistance="2.5", contactDistance="0.1", angleCone="0.05")

    Reduced_test(rootNode,
                        name="Reduced_test",
                        surfaceMeshFileName=surfaceMeshFileName)
    base = rootNode.createChild("base")
    
    stick = base.createChild("stick")
    stick.createObject('MeshObjLoader',name="loader", filename="mesh/collision_batons.obj")
    stick.createObject('Mesh', src='@loader', name='topo')
    stick.createObject('MechanicalObject', name='stickCollisModel')
    stick.createObject('Line',simulated="false", moving="false")
    stick.createObject('Point',simulated="false", moving="false")
    stick.createObject('UncoupledConstraintCorrection')
    
    blobs = base.createChild("blobs")
    blobs.createObject('MeshObjLoader',name="loader", filename="mesh/collision_boules_V3.obj")
    blobs.createObject('Mesh', src='@loader', name='topo')
    blobs.createObject('MechanicalObject', name='blobsCollisModel')
    blobs.createObject('Triangle',simulated="false", moving="false")
    blobs.createObject('Line',simulated="false", moving="false")
    blobs.createObject('Point',simulated="false", moving="false")
    blobs.createObject('UncoupledConstraintCorrection')

    foot = base.createChild("foot")
    foot.createObject('MeshObjLoader',name="loader", filename="mesh/collision_pied.obj")
    foot.createObject('Mesh', src='@loader', name='topo')
    foot.createObject('MechanicalObject', name='footCollisModel')
    foot.createObject('Triangle',simulated="false", moving="false")
    foot.createObject('Line',simulated="false", moving="false")
    foot.createObject('Point',simulated="false", moving="false")
    foot.createObject('UncoupledConstraintCorrection')
    
    visu = base.createChild("visu")
    visu.createObject('MeshObjLoader', name="SOFA_pod", filename="mesh/SOFA_pod.obj", handleSeams="1" )
    visu.createObject('OglModel' , src = '@SOFA_pod', name = 'VisuPOD',color=[1,69.0/255.0,0])

