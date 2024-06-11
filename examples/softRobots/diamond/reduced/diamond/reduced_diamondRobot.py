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
                  nbrOfModes=32,
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

    modelNode_MOR = modelRoot.addChild('modelNode_MOR')
    modelNode_MOR.addObject('EulerImplicitSolver' , name = 'integration')
    modelNode_MOR.addObject('SparseLDLSolver' , name = 'solver', template = 'CompressedRowSparseMatrixMat3x3d')
    modelNode_MOR.addObject('GenericConstraintCorrection' , linearSolver = '@solver')
    modelNode_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    modelNode = modelNode_MOR.addChild('modelNode')
    modelNode.addObject('MeshVTKLoader' , name = 'loader', filename = pathMesh + r'/mesh/diamond_4k_tet.vtu', rotation = add(rotation,[90, 0.0, 0.0]), translation = add(translation,[0.0, 0.0, 35]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    modelNode.addObject('TetrahedronSetTopologyContainer' , position = '@loader.position', tetras = '@loader.tetrahedra', name = 'container')
    modelNode.addObject('MechanicalObject' , template = 'Vec3', name = 'dofs')
    modelNode.addObject('UniformMass' , totalMass = 0.5, name = 'mass')
    modelNode.addObject('HyperReducedTetrahedronFEMForceField' , template = 'Vec3', method = 'large', name = 'reducedFF_modelNode_0', poissonRatio = 0.45, youngModulus = 450, nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_modelNode_0_RID.txt', weightsPath = path + r'/data/reducedFF_modelNode_0_weight.txt')
    modelNode.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./dofs')


    visualmodel = modelNode.addChild('visualmodel')
    visualmodel.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/surface.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    visualmodel.addObject('OglModel' , name = 'OglModel', src = '@loader', rotation = [90, 0.0, 0.0], translation = [0.0, 0.0, 35], scale3d = [1.0, 1.0, 1.0], color = [0.7, 0.7, 0.7, 0.7], updateNormals = False)
    visualmodel.addObject('BarycentricMapping' , name = 'mapping')


    FixedBox = modelNode.addChild('FixedBox')
    FixedBox.addObject('BoxROI' , name= 'BoxROI' , orientedBox= newBox([[-15, 15, -40], [-15, -15, -40], [15, -15, -40]] , [0.0, 0.0, 35],translation,rotation,[0, 0, 25.0],scale) + multiply(scale[2],[50]).tolist(),drawBoxes=True)
    FixedBox.addObject('HyperReducedRestShapeSpringsForceField' , points = '@BoxROI.indices', stiffness = 1000000000000.0, name = 'reducedFF_FixedBox_1', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_FixedBox_1_RID.txt', weightsPath = path + r'/data/reducedFF_FixedBox_1_weight.txt')


    north = modelNode.addChild('north')
    north.addObject('MechanicalObject' , position = TRSinOrigin([[0, 97, 45]] , [0.0, 0.0, 35],translation,rotation,scale), rotation = [0.0, 0.0, 0.0], translation = [0.0, 0.0, 0.0], scale = 1.0)
    north.addObject('CableConstraint' , indices = [0], pullPoint = TRSinOrigin([0, 10, 30] , [0.0, 0.0, 35],translation,rotation,scale), value = 0.0, valueType = 'displacement', hasPullPoint = True)
    north.addObject('BarycentricMapping' , name = 'Mapping', mapForces = False, mapMasses = False)


    west = modelNode.addChild('west')
    west.addObject('MechanicalObject' , position = TRSinOrigin([[-97, 0, 45]] , [0.0, 0.0, 35],translation,rotation,scale), rotation = [0.0, 0.0, 0.0], translation = [0.0, 0.0, 0.0], scale = 1.0)
    west.addObject('CableConstraint' , indices = [0], pullPoint = TRSinOrigin([-10, 0, 30] , [0.0, 0.0, 35],translation,rotation,scale), value = 0.0, valueType = 'displacement', hasPullPoint = True)
    west.addObject('BarycentricMapping' , name = 'Mapping', mapForces = False, mapMasses = False)


    south = modelNode.addChild('south')
    south.addObject('MechanicalObject' , position = TRSinOrigin([[0, -97, 45]] , [0.0, 0.0, 35],translation,rotation,scale), rotation = [0.0, 0.0, 0.0], translation = [0.0, 0.0, 0.0], scale = 1.0)
    south.addObject('CableConstraint' , indices = [0], pullPoint = TRSinOrigin([0, -10, 30] , [0.0, 0.0, 35],translation,rotation,scale), value = 0.0, valueType = 'displacement', hasPullPoint = True)
    south.addObject('BarycentricMapping' , name = 'Mapping', mapForces = False, mapMasses = False)


    east = modelNode.addChild('east')
    east.addObject('MechanicalObject' , position = TRSinOrigin([[97, 0, 45]] , [0.0, 0.0, 35],translation,rotation,scale), rotation = [0.0, 0.0, 0.0], translation = [0.0, 0.0, 0.0], scale = 1.0)
    east.addObject('CableConstraint' , indices = [0], pullPoint = TRSinOrigin([10, 0, 30] , [0.0, 0.0, 35],translation,rotation,scale), value = 0.0, valueType = 'displacement', hasPullPoint = True)
    east.addObject('BarycentricMapping' , name = 'Mapping', mapForces = False, mapMasses = False)

    return modelNode


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SoftRobots","ModelOrderReduction"],
                        dt=1.0,
                        gravity=[0.0, 0.0, -9810.0])
    rootNode.VisualStyle.displayFlags="showForceFields"
    
    Reduced_test(rootNode,
                        name="Reduced_test",
                        surfaceMeshFileName=surfaceMeshFileName)