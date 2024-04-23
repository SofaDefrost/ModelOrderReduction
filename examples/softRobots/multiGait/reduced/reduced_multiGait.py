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
                  nbrOfModes=89,
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

    model_MOR = modelRoot.addChild('model_MOR')
    model_MOR.addObject('EulerImplicitSolver', name='odesolver', rayleighStiffness='0.1', rayleighMass='0.1')
    model_MOR.addObject('SparseLDLSolver' , name = 'preconditioner', template = 'CompressedRowSparseMatrixMat3x3d')
    model_MOR.addObject('GenericConstraintCorrection' , linearSolver = '@preconditioner')
    model_MOR.addObject('MechanicalObject' , template = 'Vec1d', position = [0]*nbrOfModes)


    model = model_MOR.addChild('model')
    model.addObject('MeshVTKLoader' , name = 'loader', filename = pathMesh + r'/mesh/full_quadriped_SMALL.vtk', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    model.addObject('TetrahedronSetTopologyContainer' , position = '@loader.position', tetrahedra = '@loader.tetrahedra', name = 'container')
    model.addObject('MechanicalObject' , name = 'tetras', template = 'Vec3d', showIndices = 'false', showIndicesScale = '4e-5', rx = '0')
    model.addObject('UniformMass' , totalMass = '0.035')
    model.addObject('HyperReducedTetrahedronFEMForceField' , template = 'Vec3d', name = 'reducedFF_model_0', method = 'large', poissonRatio = '0.05', youngModulus = '70', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_model_0_RID.txt', weightsPath = path + r'/data/reducedFF_model_0_weight.txt')
    model.addObject('BoxROI' , name= 'boxROISubTopo' , orientedBox= newBox([[0.0, -100.0, 0.0], [0.0, 0.0, 0.0], [150.0, 0.0, 0.0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.5],scale) + multiply(scale[2],[1.0]).tolist(),drawBoxes=True)
    model.addObject('BoxROI' , name= 'membraneROISubTopo' , orientedBox= newBox([[0.0, -100.0, -0.1], [0.0, 0.0, -0.1], [150.0, 0.0, -0.1]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.1],scale) + multiply(scale[2],[0.2]).tolist(),drawBoxes=True)
    model.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + r'/data/modes.txt', output = '@./tetras')


    modelSubTopo = model.addChild('modelSubTopo')
    modelSubTopo.addObject('TriangleSetTopologyContainer' , position = '@../membraneROISubTopo.pointsInROI', triangles = '@../membraneROISubTopo.trianglesInROI', name = 'container')
    modelSubTopo.addObject('HyperReducedTriangleFEMForceField' , template = 'Vec3d', name = 'reducedFF_modelSubTopo_1', method = 'large', poissonRatio = '0.49', youngModulus = '5000', nbModes = nbrOfModes, performECSW = hyperReduction, modesPath = path + r'/data/modes.txt', RIDPath = path + r'/data/reducedFF_modelSubTopo_1_RID.txt', weightsPath = path + r'/data/reducedFF_modelSubTopo_1_weight.txt')


    centerCavity = model.addChild('centerCavity')
    centerCavity.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_Center-cavityREMESHEDlighter.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    centerCavity.addObject('MeshTopology' , src = '@loader', name = 'topo')
    centerCavity.addObject('MechanicalObject' , name = 'centerCavity')
    centerCavity.addObject('SurfacePressureConstraint' , name = 'SurfacePressureConstraint', template = 'Vec3d', value = '0.00', triangles = '@topo.triangles', drawPressure = '0', drawScale = '0.0002', valueType = 'volumeGrowth')
    centerCavity.addObject('BarycentricMapping' , name = 'mapping', mapForces = 'false', mapMasses = 'false')


    rearLeftCavity = model.addChild('rearLeftCavity')
    rearLeftCavity.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_Rear-Left-cavity_collis.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    rearLeftCavity.addObject('MeshTopology' , src = '@loader', name = 'topo')
    rearLeftCavity.addObject('MechanicalObject' , name = 'rearLeftCavity')
    rearLeftCavity.addObject('SurfacePressureConstraint' , name = 'SurfacePressureConstraint', template = 'Vec3d', valueType = 'volumeGrowth', value = '0.000', triangles = '@topo.triangles', drawPressure = '0', drawScale = '0.0002')
    rearLeftCavity.addObject('BarycentricMapping' , name = 'mapping', mapForces = 'false', mapMasses = 'false')


    rearRightCavity = model.addChild('rearRightCavity')
    rearRightCavity.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_Rear-Right-cavity_collis.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    rearRightCavity.addObject('MeshTopology' , src = '@loader', name = 'topo')
    rearRightCavity.addObject('MechanicalObject' , name = 'rearRightCavity')
    rearRightCavity.addObject('SurfacePressureConstraint' , name = 'SurfacePressureConstraint', template = 'Vec3d', value = '0.00', triangles = '@topo.triangles', drawPressure = '0', drawScale = '0.0002', valueType = 'volumeGrowth')
    rearRightCavity.addObject('BarycentricMapping' , name = 'mapping', mapForces = 'false', mapMasses = 'false')


    frontLeftCavity = model.addChild('frontLeftCavity')
    frontLeftCavity.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_Front-Left-cavity_collis.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    frontLeftCavity.addObject('MeshTopology' , src = '@loader', name = 'topo')
    frontLeftCavity.addObject('MechanicalObject' , name = 'frontLeftCavity')
    frontLeftCavity.addObject('SurfacePressureConstraint' , name = 'SurfacePressureConstraint', template = 'Vec3d', value = '0.000', triangles = '@topo.triangles', drawPressure = '0', drawScale = '0.0002', valueType = 'volumeGrowth')
    frontLeftCavity.addObject('BarycentricMapping' , name = 'mapping', mapForces = 'false', mapMasses = 'false')


    frontRightCavity = model.addChild('frontRightCavity')
    frontRightCavity.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_Front-Right-cavity_collis.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    frontRightCavity.addObject('MeshTopology' , src = '@loader', name = 'topo')
    frontRightCavity.addObject('MechanicalObject' , name = 'frontRightCavity')
    frontRightCavity.addObject('SurfacePressureConstraint' , name = 'SurfacePressureConstraint', template = 'Vec3d', value = '0.000', triangles = '@topo.triangles', drawPressure = '0', drawScale = '0.0002', valueType = 'volumeGrowth')
    frontRightCavity.addObject('BarycentricMapping' , name = 'mapping', mapForces = 'false', mapMasses = 'false')


    modelCollis = model.addChild('modelCollis')
    modelCollis.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_collision.stl', rotation = '0 0 0', translation = '0 0 0', scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    modelCollis.addObject('TriangleSetTopologyContainer' , position = '@loader.position', triangles = '@loader.triangles', name = 'container')
    modelCollis.addObject('MechanicalObject' , name = 'collisMO', template = 'Vec3d')
    modelCollis.addObject('TriangleCollisionModel' , group = '0')
    modelCollis.addObject('LineCollisionModel' , group = '0')
    modelCollis.addObject('PointCollisionModel' , group = '0')
    modelCollis.addObject('BarycentricMapping')


    visu = model.addChild('visu')
    visu.addObject('MeshSTLLoader' , name = 'loader', filename = pathMesh + r'/mesh/quadriped_collision.stl', translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), scale3d = multiply(scale,[1.0, 1.0, 1.0]))
    visu.addObject('OglModel' , src = '@loader', template = 'Vec3d', color = '0.7 0.7 0.7 0.6')
    visu.addObject('BarycentricMapping')

    return model


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=['SoftRobots',
                                'ModelOrderReduction',
                                'Sofa.Component.Collision.Geometry', 
                                'Sofa.Component.Constraint.Lagrangian.Correction', 
                                'Sofa.Component.Engine.Select', 
                                'Sofa.Component.IO.Mesh', 
                                'Sofa.Component.LinearSolver.Direct', 
                                'Sofa.Component.Mapping.Linear', 
                                'Sofa.Component.Mass', 
                                'Sofa.Component.StateContainer', 
                                'Sofa.Component.Topology.Container.Constant', 
                                'Sofa.Component.Topology.Container.Dynamic', 
                                'Sofa.Component.Visual', 
                                'Sofa.GL.Component.Rendering3D'], 

                        dt=0.01,
                        gravity=[0.0, -9.81, 0.0])
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
