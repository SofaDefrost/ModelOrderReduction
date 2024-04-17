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
                  nbrOfModes=6,
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

    SofiaLeg_MOR = modelRoot.addChild('SofiaLeg_MOR')
    SofiaLeg_MOR.addObject('EulerImplicitSolver' , firstOrder = '0', name = 'odesolver')
    SofiaLeg_MOR.addObject('SparseLDLSolver' , name = 'preconditioner', template = 'CompressedRowSparseMatrixd')
    SofiaLeg_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    SofiaLeg = SofiaLeg_MOR.addChild('SofiaLeg')
    SofiaLeg.addObject('MeshVTKLoader' , name = 'loader', scale3d = multiply(scale,[1.0, 1.0, 1.0]), translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), filename = pathMesh + r'/mesh/sofia_leg.vtu')
    SofiaLeg.addObject('TetrahedronSetTopologyContainer' , name = 'container', position = '@loader.position', tetrahedra = '@loader.tetrahedra', checkConnexity = '1', createTriangleArray = '1')
    SofiaLeg.addObject('MechanicalObject' , name = 'tetras', showIndices = 'false', showIndicesScale = '4e-5', template = 'Vec3d', position = '@loader.position')
    SofiaLeg.addObject('UniformMass' , totalMass = 0.01)
    SofiaLeg.addObject('HyperReducedTetrahedronFEMForceField' , youngModulus = 300, poissonRatio = 0.45, name = 'reducedFF_SofiaLeg_0', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_SofiaLeg_0_RID.txt', weightsPath = path + r'/data/reducedFF_SofiaLeg_0_weight.txt')
    SofiaLeg.addObject('BoxROI' , name = 'boxROITop', orientedBox = [[-12.0, 53.0, 0.0], [12.0, 53.0, 0.0], [12.0, 64.0, 0.0], 16.0], drawBoxes = True)
    SofiaLeg.addObject('HyperReducedRestShapeSpringsForceField' , name = 'reducedFF_SofiaLeg_1', points = '@boxROITop.indices', stiffness = '1e8', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_SofiaLeg_1_RID.txt', weightsPath = path + r'/data/reducedFF_SofiaLeg_1_weight.txt')
    SofiaLeg.addObject('BoxROI' , name = 'boxROICollision', orientedBox = [[-25.0, -41.0, -7.0], [25.0, -42.0, -7.0], [25.0, -39.0, -7.0], 2.0, [-25.0, -42.0, 7.0], [25.0, -42.0, 7.0], [25.0, -39.0, 7.0], 2.0], drawPoints = '0', computeEdges = '0', computeTriangles = '0', computeTetrahedra = '0', computeHexahedra = '0', computeQuad = '0', drawSize = 5, drawBoxes = True)
    SofiaLeg.addObject('BoxROI' , name = 'boxROIMiddle', orientedBox = [[-2.5, -8.5, 0.0], [2.5, -8.5, 0.0], [2.5, -3.5, 0.0], 18.0], drawBoxes = True)
    SofiaLeg.addObject('HyperReducedRestShapeSpringsForceField' , external_points = [0, 1, 2], points = '@boxROIMiddle.indices', name = 'reducedFF_SofiaLeg_2', stiffness = '1e8', external_rest_shape = '@../../SofiaLeg_actuator/actuatorState', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_SofiaLeg_2_RID.txt', weightsPath = path + r'/data/reducedFF_SofiaLeg_2_weight.txt')
    SofiaLeg.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./tetras')


    SofiaLeg_actuator = modelRoot.addChild('SofiaLeg_actuator')
    SofiaLeg_actuator.addObject('MechanicalObject' , name = 'actuatorState', position = '@../SofiaLeg_MOR/SofiaLeg/boxROIMiddle.pointsInROI', template = 'Vec3d', showObject = True, showObjectScale = 5)


    Visual = SofiaLeg.addChild('Visual')
    Visual.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/sofia_leg.stl', rotation = add(rotation,[0.0, 0.0, 0.0]), translation = add(translation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    Visual.addObject('OglModel' , src = '@loader', template = 'Vec3d', color = [1.0, 1.0, 1.0])
    Visual.addObject('BarycentricMapping')

    return SofiaLeg


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SoftRobots","ModelOrderReduction"],
                        dt=0.01,
                        gravity=[0.0, -9810.0, 0.0])
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
