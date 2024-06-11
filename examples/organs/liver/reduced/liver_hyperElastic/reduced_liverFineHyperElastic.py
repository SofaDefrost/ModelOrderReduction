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
pathMesh = path + "/../.."

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

    liver_MOR = modelRoot.addChild('liver_MOR')
    liver_MOR.addObject('EulerImplicitSolver' , rayleighStiffness = 0.0, rayleighMass = 0.0)
    liver_MOR.addObject('SparseLDLSolver' , template = 'CompressedRowSparseMatrixMat3x3d')
    liver_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    liver = liver_MOR.addChild('liver')
    liver.addObject('MeshVTKLoader' , name = 'loader', filename = pathMesh + r'/mesh/liverFine.vtu', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    liver.addObject('TetrahedronSetTopologyContainer' , src = '@loader')
    liver.addObject('MechanicalObject')
    liver.addObject('BoxROI' , name= 'ROI1' , orientedBox= newBox([[0.0, 5.0, -1.0], [0.0, 3.0, -1.0], [2.0, 3.0, -1.0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 1.5],scale) + multiply(scale[2],[3.0]).tolist(),drawBoxes=True)
    liver.addObject('BoxROI' , name= 'boxROIactuation' , orientedBox= newBox([[-5.0, 0.5, -0.5], [-5.0, 0.0, -0.5], [-4.0, 0.0, -0.5]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.5],scale) + multiply(scale[2],[1.0]).tolist(),drawBoxes=True)
    liver.addObject('UniformMass' , totalMass = 0.3)
    liver.addObject('HyperReducedTetrahedronHyperelasticityFEMForceField' , materialName = 'NeoHookean', ParameterSet = '1923.076923076923 4166.666666666666', AnisotropyDirections = '', name = 'reducedFF_liver_0', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_liver_0_RID.txt', weightsPath = path + r'/data/reducedFF_liver_0_weight.txt')
    liver.addObject('HyperReducedRestShapeSpringsForceField' , points = '@ROI1.indices', stiffness = '1e8', name = 'reducedFF_liver_1', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_liver_1_RID.txt', weightsPath = path + r'/data/reducedFF_liver_1_weight.txt')
    liver.addObject('HyperReducedRestShapeSpringsForceField' , external_points = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], points = '@boxROIactuation.indices', name = 'reducedFF_liver_2', stiffness = '1e8', external_rest_shape = '@actuator/actuatorState', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_liver_2_RID.txt', weightsPath = path + r'/data/reducedFF_liver_2_weight.txt')
    liver.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./MechanicalObject')


    visu = liver.addChild('visu')
    visu.addObject('MeshOBJLoader' , name = 'loader', filename = pathMesh + r'/mesh/liver-smoothUV.obj', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    visu.addObject('OglModel' , src = '@loader')
    visu.addObject('BarycentricMapping')


    actuator = modelRoot.addChild('actuator')
    actuator.addObject('MechanicalObject' , name = 'actuatorState', position = '@../liver_MOR/liver/boxROIactuation.pointsInROI', template = 'Vec3d')

    return liver


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SoftRobots","ModelOrderReduction"],
                        dt=0.01,
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
