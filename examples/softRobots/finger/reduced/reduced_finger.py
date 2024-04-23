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
                  nbrOfModes=3,
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

    finger_MOR = modelRoot.addChild('finger_MOR')
    finger_MOR.addObject('EulerImplicitSolver' , rayleighStiffness = 0.0, rayleighMass = 0.0)
    finger_MOR.addObject('SparseLDLSolver' , template = 'CompressedRowSparseMatrixMat3x3d')
    finger_MOR.addObject('GenericConstraintCorrection')
    finger_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    finger = finger_MOR.addChild('finger')
    finger.addObject('MeshVTKLoader' , name = 'loader', filename = pathMesh + r'/mesh/finger.vtk', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    finger.addObject('TetrahedronSetTopologyContainer' , position = '@loader.position', tetrahedra = '@loader.tetrahedra')
    finger.addObject('MechanicalObject')
    finger.addObject('UniformMass' , totalMass = 0.05)
    finger.addObject('HyperReducedTetrahedronFEMForceField' , poissonRatio = '0.45', youngModulus = '600', name = 'reducedFF_finger_0', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_finger_0_RID.txt', weightsPath = path + r'/data/reducedFF_finger_0_weight.txt')
    finger.addObject('BoxROI' , name= 'ROI1' , orientedBox= newBox([[-15, 10, 0], [-15, 0, 0], [5, 0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 7.5],scale) + multiply(scale[2],[15]).tolist(),drawBoxes=True)
    finger.addObject('HyperReducedRestShapeSpringsForceField' , points = '@ROI1.indices', stiffness = 1000000000000.0, name = 'reducedFF_finger_1', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_finger_1_RID.txt', weightsPath = path + r'/data/reducedFF_finger_1_weight.txt')
    finger.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./MechanicalObject')


    cable = finger.addChild('cable')
    cable.addObject('MechanicalObject' , position = TRSinOrigin([[-17.5, 12.5, 2.5], [-32.5, 12.5, 2.5], [-47.5, 12.5, 2.5], [-62.5, 12.5, 2.5], [-77.5, 12.5, 2.5], [-83.5, 12.5, 4.5], [-85.5, 12.5, 6.5], [-85.5, 12.5, 8.5], [-83.5, 12.5, 10.5], [-77.5, 12.5, 12.5], [-62.5, 12.5, 12.5], [-47.5, 12.5, 12.5], [-32.5, 12.5, 12.5], [-17.5, 12.5, 12.5]] , [0.0, 0.0, 0.0],translation,rotation,scale))
    cable.addObject('CableConstraint' , name = 'cable', indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], pullPoint = TRSinOrigin([0.0, 12.5, 2.5] , [0.0, 0.0, 0.0],translation,rotation,scale))
    cable.addObject('BarycentricMapping')

    return finger


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
