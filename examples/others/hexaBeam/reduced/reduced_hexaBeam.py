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

    M1_MOR = modelRoot.addChild('M1_MOR')
    M1_MOR.addObject('EulerImplicitSolver' , rayleighStiffness = '0.1', rayleighMass = '0.1')
    M1_MOR.addObject('SparseLDLSolver' , name = 'preconditioner')
    M1_MOR.addObject('GenericConstraintCorrection')
    M1_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    M1 = M1_MOR.addChild('M1')
    M1.addObject('MechanicalObject')
    M1.addObject('UniformMass' , totalMass = '0.1')
    M1.addObject('RegularGrid' , nx = '4', ny = '4', nz = '20', xmin = '-9', xmax = '-6', ymin = '0', ymax = '3', zmin = '0', zmax = '19')
    M1.addObject('HyperReducedRestShapeSpringsForceField' , points = '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15', stiffness = 1000000000000.0, name = 'reducedFF_M1_0', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_M1_0_RID.txt', weightsPath = path + r'/data/reducedFF_M1_0_weight.txt')
    M1.addObject('HyperReducedHexahedronFEMForceField' , name = 'reducedFF_M1_1', youngModulus = '4000', poissonRatio = '0.3', method = 'large', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_M1_1_RID.txt', weightsPath = path + r'/data/reducedFF_M1_1_weight.txt')
    M1.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./MechanicalObject')


    cableNodeTip = M1.addChild('cableNodeTip')
    cableNodeTip.addObject('MechanicalObject' , name = 'actuatedTip', template = 'Vec3d', position = '-7.5 1.5 18.5')
    cableNodeTip.addObject('CableConstraint' , name = 'tipCable', indices = '0', pullPoint = '-7.5 10 18.5', valueType = 'displacement')
    cableNodeTip.addObject('BarycentricMapping' , mapForces = 'false', mapMasses = 'false')


    cableNodeSide = M1.addChild('cableNodeSide')
    cableNodeSide.addObject('MechanicalObject' , name = 'actuatedSide', template = 'Vec3d', position = '-7.5 1.5 18.5')
    cableNodeSide.addObject('CableConstraint' , name = 'sideCable', indices = '0', pullPoint = '1 10 18.5', valueType = 'displacement')
    cableNodeSide.addObject('BarycentricMapping' , mapForces = 'false', mapMasses = 'false')

    return M1


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SoftRobots","ModelOrderReduction"],
                        dt=0.02,
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
