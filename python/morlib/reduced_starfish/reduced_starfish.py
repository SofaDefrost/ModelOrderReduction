# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract
from splib3.numerics import *

path = os.path.dirname(os.path.abspath(__file__))

def TRSinOrigin(positions,modelPosition,translation,rotation):
    posOrigin = subtract(positions , modelPosition)
    if any(isinstance(el, list) for el in positions):
        posOriginTRS = transformPositions(posOrigin,translation,eulerRotation=rotation)
    else:
        posOriginTRS = transformPosition(posOrigin,TRS_to_matrix(translation,eulerRotation=rotation))
    return add(posOriginTRS,modelPosition).tolist()
    
def newBox(positions,modelPosition,translation,rotation,offset):
    pos = TRSinOrigin(positions,modelPosition,translation,rotation)
    offset =transformPositions([offset],eulerRotation=rotation)[0]
    return add(pos,offset).tolist()

def Reduced_starfish(
                  attachedTo=None,
                  name="Reduced_starfish",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
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

        poissonRatio (float):  The poisson parameter.

        youngModulus (float):  The young modulus.

        totalMass (float):   The mass is distributed according to the geometry of the object.
    """

    model_MOR = attachedTo.addChild(name)
    model_MOR.addObject('EulerImplicitSolver' , firstOrder = 'false', rayleighStiffness = '0.1', name = 'odesolver', rayleighMass = '0.1')
    model_MOR.addObject('SparseLDLSolver' , name = 'preconditioner', template = 'CompressedRowSparseMatrixMat3x3d')
    model_MOR.addObject('GenericConstraintCorrection' , solverName = 'preconditioner')
    model_MOR.addObject('MechanicalObject' , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', template = 'Vec1d')
    model_MOR.addObject('MechanicalMatrixMapperMOR' , nodeToParse='@./model', object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_model.txt', template = 'Vec1d,Vec1d', performECSW = 'True')


    model = model_MOR.addChild('model')
    model.addObject('MeshVTKLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/full_quadriped_SMALL.vtk')
    model.addObject('TetrahedronSetTopologyContainer' , src = '@loader', edges = '', name = 'container', tetrahedra = '@loader.tetrahedra', position = '@loader.position')
    model.addObject('TetrahedronSetTopologyModifier')
    model.addObject('MechanicalObject' , showIndices = 'false', rx = '0', showIndicesScale = '4e-5', name = 'tetras', template = 'Vec3d')
    model.addObject('TetrahedronSetGeometryAlgorithms' , template = 'Vec3d')
    model.addObject('UniformMass' , totalMass = '0.200')
    model.addObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_model.txt', name = 'HyperReducedFEMForceField_model', weightsPath = path + '/data/weight_model.txt', youngModulus = '70', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.05', nbModes = '75')
    model.addObject('BoxROI' , name= 'boxROISubTopo' , orientedBox= newBox([[0.0, 0.0, 0], [150.0, 0, 0], [150.0, -100.0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.5])+[1.0],drawBoxes=True)
    model.addObject('BoxROI' , name= 'membraneROISubTopo' , orientedBox= newBox([[0.0, 0.0, 0], [150.0, 0, 0], [150.0, -100.0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.0])+[0.2],drawBoxes=True)
    model.addObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/test_modes.txt', output = '@./tetras')


    modelSubTopo = model.addChild('modelSubTopo')
    modelSubTopo.addObject('TriangleSetTopologyContainer' , position = '@loader.position', name = 'container', triangles = '@membraneROISubTopo.trianglesInROI')
    modelSubTopo.addObject('HyperReducedTriangleFEMForceField' , RIDPath = path + '/data/RID_modelSubTopo.txt', name = 'HyperReducedFEMForceField_modelSubTopo', weightsPath = path + '/data/weight_modelSubTopo.txt', youngModulus = '5000', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.49', nbModes = '75')


    centerCavity = model.addChild('centerCavity')
    centerCavity.addObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Center-cavityREMESHEDlighter.stl')
    centerCavity.addObject('Mesh' , src = '@loader', name = 'topo')
    centerCavity.addObject('MechanicalObject' , name = 'centerCavity')
    centerCavity.addObject('SurfacePressureConstraint' , drawPressure = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.00', drawScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    centerCavity.addObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    rearLeftCavity = model.addChild('rearLeftCavity')
    rearLeftCavity.addObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Rear-Left-cavity_collis.stl')
    rearLeftCavity.addObject('Mesh' , src = '@loader', name = 'topo')
    rearLeftCavity.addObject('MechanicalObject' , name = 'rearLeftCavity')
    rearLeftCavity.addObject('SurfacePressureConstraint' , drawPressure = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.000', drawScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    rearLeftCavity.addObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    rearRightCavity = model.addChild('rearRightCavity')
    rearRightCavity.addObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Rear-Right-cavity_collis.stl')
    rearRightCavity.addObject('Mesh' , src = '@loader', name = 'topo')
    rearRightCavity.addObject('MechanicalObject' , name = 'rearRightCavity')
    rearRightCavity.addObject('SurfacePressureConstraint' , drawPressure = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.00', drawScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    rearRightCavity.addObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    frontLeftCavity = model.addChild('frontLeftCavity')
    frontLeftCavity.addObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Front-Left-cavity_collis.stl')
    frontLeftCavity.addObject('Mesh' , src = '@loader', name = 'topo')
    frontLeftCavity.addObject('MechanicalObject' , name = 'frontLeftCavity')
    frontLeftCavity.addObject('SurfacePressureConstraint' , drawPressure = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.000', drawScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    frontLeftCavity.addObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    frontRightCavity = model.addChild('frontRightCavity')
    frontRightCavity.addObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Front-Right-cavity_collis.stl')
    frontRightCavity.addObject('Mesh' , src = '@loader', name = 'topo')
    frontRightCavity.addObject('MechanicalObject' , name = 'frontRightCavity')
    frontRightCavity.addObject('SurfacePressureConstraint' , drawPressure = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.000', drawScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    frontRightCavity.addObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')

    ## Visualization
    if surfaceMeshFileName:
        visu = model.addChild('Visual')
        meshType = surfaceMeshFileName.split('.')[-1]
        if meshType == 'stl':
            visu.addObject(  'MeshSTLLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)
        elif meshType == 'obj':
            visu.addObject(  'MeshOBJLoader', name= 'loader', filename=path+'/mesh/'+surfaceMeshFileName)

        visu.addObject(  'OglModel',
                            src='@loader',
                            template='Vec3d',
                            color=surfaceColor,
                            rotation= add(rotation,[0.0, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 0.0]))

        visu.addObject('BarycentricMapping')

    return model


#   STLIB IMPORT
from stlib3.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = 'quadriped_collision.stl'

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=0.001,
                        gravity=[0.0,0.0,-9810])

    translate = 300
    rotationBlue = 60.0
    rotationWhite = 80
    rotationRed = 70

    for i in range(3):

        Reduced_starfish(rootNode,
                        name="Reduced_starfish_blue", 
                        rotation=[rotationBlue*i, 0.0, 0.0],
                        translation=[i*translate, 0.0, 0.0],
                        surfaceColor=[0.0, 0.0, 1, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
    for i in range(3):

        Reduced_starfish(rootNode,
                        name="Reduced_starfish_white", 
                        rotation=[0.0, rotationWhite*i, 0.0],
                        translation=[i*translate, translate, -translate],
                        surfaceColor=[0.5, 0.5, 0.5, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)

    for i in range(3):

        Reduced_starfish(rootNode,
                        name="Reduced_starfish_red", 
                        rotation=[0.0, 0.0, i*rotationRed],
                        translation=[i*translate, 2*translate, -2*translate],
                        surfaceColor=[1, 0.0, 0.0, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
