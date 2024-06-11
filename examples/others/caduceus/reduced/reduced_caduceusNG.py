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
pathMesh = path + "/.."

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
                  nbrOfModes=8,
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
    Snake_MOR.addObject('GenericConstraintCorrection' , linearSolver = '@preconditioner')
    Snake_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    Snake = Snake_MOR.addChild('Snake')
    Snake.addObject('MeshVTKLoader' , name = 'loader', filename = pathMesh + r'/mesh/snake0.vtu', rotation = add(rotation,[-90, 0, 0]), translation = add(translation,[0, 5, 0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    Snake.addObject('TetrahedronSetTopologyContainer' , src = '@loader')
    Snake.addObject('MechanicalObject')
    Snake.addObject('UniformMass' , totalMass = '1.0')
    Snake.addObject('HyperReducedTetrahedronFEMForceField' , name = 'reducedFF_Snake_0', youngModulus = '10000.0', poissonRatio = '0.4', method = 'large', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_Snake_0_RID.txt', weightsPath = path + r'/data/reducedFF_Snake_0_weight.txt')
    Snake.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./MechanicalObject')


    collis = Snake.addChild('collis')
    collis.addObject('MeshOBJLoader' , name = 'loader', filename = pathMesh + r'/mesh/meca_snake_900tri.obj', translation = add(translation,[0, 5, 0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    collis.addObject('Mesh' , src = '@loader', name = 'topo')
    collis.addObject('MechanicalObject' , name = 'CollisModel')
    collis.addObject('TriangleCollisionModel' , selfCollision = False)
    collis.addObject('LineCollisionModel' , selfCollision = False)
    collis.addObject('PointCollisionModel' , selfCollision = False)
    collis.addObject('BarycentricMapping')


    VisuBody = Snake.addChild('VisuBody')
    VisuBody.addObject('MeshOBJLoader' , name = 'loader', filename = pathMesh + r'/mesh/snake_body.obj', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    VisuBody.addObject('OglModel' , name = 'VisualBody', src = '@loader', texturename = 'textures/snakeColorMap.png', color = [1, 1, 1, 0.6], translation = [0, 5, 0])
    VisuBody.addObject('BarycentricMapping')


    VisuCornea = Snake.addChild('VisuCornea')
    VisuCornea.addObject('MeshOBJLoader' , name = 'loader', filename = pathMesh + r'/mesh/snake_cornea.obj', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    VisuCornea.addObject('OglModel' , name = 'VisuCornea', src = '@loader', translation = [0, 5, 0])
    VisuCornea.addObject('BarycentricMapping')


    VisualEye = Snake.addChild('VisualEye')
    VisualEye.addObject('MeshOBJLoader' , name = 'loader', filename = pathMesh + r'/mesh/snake_yellowEye.obj', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    VisualEye.addObject('OglModel' , name = 'VisualEye', src = '@loader', translation = [0, 5, 0])
    VisualEye.addObject('BarycentricMapping')

    return Snake


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SoftRobots","ModelOrderReduction"],
                        dt=0.02,
                        gravity=[0.0, -981.0, 0.0])
    rootNode.VisualStyle.displayFlags="showForceFields"
    
    Reduced_test(rootNode,
                        name="Reduced_test",
                        surfaceMeshFileName=surfaceMeshFileName)

    # translate = 300
    # rotationBlue = 60.0
    # rotationWhite = 80
    # rotationRed = 70

    # for i in range(3):

    #     Reduced_test(rootNode,
    #                    name="Reduced_test_blue_"+str(i),
    #                    rotation=[rotationBlue*i, 0.0, 0.0],
    #                    translation=[i*translate, 0.0, 0.0],
    #                    surfaceColor=[0.0, 0.0, 1, 0.5],
    #                    surfaceMeshFileName=surfaceMeshFileName)
    # for i in range(3):

    #     Reduced_test(rootNode,
    #                    name="Reduced_test_white_"+str(i),
    #                    rotation=[0.0, rotationWhite*i, 0.0],
    #                    translation=[i*translate, translate, -translate],
    #                    surfaceColor=[0.5, 0.5, 0.5, 0.5],
    #                    surfaceMeshFileName=surfaceMeshFileName)

    # for i in range(3):

    #     Reduced_test(rootNode,
    #                    name="Reduced_test_red_"+str(i),
    #                    rotation=[0.0, 0.0, i*rotationRed],
    #                    translation=[i*translate, 2*translate, -2*translate],
    #                    surfaceColor=[1, 0.0, 0.0, 0.5],
    #                    surfaceMeshFileName=surfaceMeshFileName)
