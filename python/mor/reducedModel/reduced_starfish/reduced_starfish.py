# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,subtract
from splib.numerics import *

path = os.path.dirname(os.path.abspath(__file__))

def TRSinOrigin(positions,modelPosition,translation,rotation):
    posOrigin = subtract(positions , modelPosition)
    if any(isinstance(el, list) for el in positions):
        posOriginTRS = transformPositions(posOrigin,translation,rotation)
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

    model_MOR = attachedTo.createChild(name)
    model_MOR.createObject('EulerImplicit' , firstOrder = 'false', rayleighStiffness = '0.1', name = 'odesolver', rayleighMass = '0.1')
    model_MOR.createObject('SparseLDLSolver' , name = 'preconditioner', template = 'CompressedRowSparseMatrix3d')
    model_MOR.createObject('GenericConstraintCorrection' , solverName = 'preconditioner')
    model_MOR.createObject('MechanicalObject' , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', template = 'Vec1d')
    model_MOR.createObject('MappedMatrixForceFieldAndMassMOR' , mappedForceField = '@./model/HyperReducedFEMForceField_model', object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_model.txt', template = 'Vec1d,Vec1d', mappedForceField2 = '@./model/modelSubTopo/HyperReducedFEMForceField_modelSubTopo', performECSW = 'True', mappedMass = '@./model/UniformMass')


    model = model_MOR.createChild('model')
    model.createObject('MeshVTKLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/full_quadriped_SMALL.vtk')
    model.createObject('TetrahedronSetTopologyContainer' , src = '@loader', edges = '', name = 'container', tetrahedra = '@loader.tetrahedra', position = '@loader.position')
    model.createObject('TetrahedronSetTopologyModifier')
    model.createObject('TetrahedronSetTopologyAlgorithms' , template = 'Vec3d')
    model.createObject('TetrahedronSetGeometryAlgorithms' , template = 'Vec3d')
    model.createObject('MechanicalObject' , showIndices = 'false', rx = '0', showIndicesScale = '4e-5', name = 'tetras', template = 'Vec3d')
    model.createObject('UniformMass' , totalmass = '0.200')
    model.createObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_model.txt', name = 'HyperReducedFEMForceField_model', weightsPath = path + '/data/weight_model.txt', youngModulus = '70', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.05', nbModes = '75')
    model.createObject('BoxROI' , name= 'boxROISubTopo' , orientedBox= newBox([[0.0, 0.0, 0], [150.0, 0, 0], [150.0, -100.0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.5])+[1.0],drawBoxes=True)
    model.createObject('BoxROI' , name= 'membraneROISubTopo' , orientedBox= newBox([[0.0, 0.0, 0], [150.0, 0, 0], [150.0, -100.0, 0]] , [0.0, 0.0, 0.0],translation,rotation,[0, 0, 0.0])+[0.2],drawBoxes=True)
    model.createObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/test_modes.txt', output = '@./tetras')


    modelSubTopo = model.createChild('modelSubTopo')
    modelSubTopo.createObject('TriangleSetTopologyContainer' , position = '@loader.position', name = 'container', triangles = '@membraneROISubTopo.trianglesInROI')
    modelSubTopo.createObject('HyperReducedTriangleFEMForceField' , RIDPath = path + '/data/RID_modelSubTopo.txt', name = 'HyperReducedFEMForceField_modelSubTopo', weightsPath = path + '/data/weight_modelSubTopo.txt', youngModulus = '5000', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.49', nbModes = '75')


    centerCavity = model.createChild('centerCavity')
    centerCavity.createObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Center-cavityREMESHEDlighter.stl')
    centerCavity.createObject('Mesh' , src = '@loader', name = 'topo')
    centerCavity.createObject('MechanicalObject' , name = 'centerCavity')
    centerCavity.createObject('SurfacePressureConstraint' , visualization = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.00', showVisuScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    centerCavity.createObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    rearLeftCavity = model.createChild('rearLeftCavity')
    rearLeftCavity.createObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Rear-Left-cavity_collis.stl')
    rearLeftCavity.createObject('Mesh' , src = '@loader', name = 'topo')
    rearLeftCavity.createObject('MechanicalObject' , name = 'rearLeftCavity')
    rearLeftCavity.createObject('SurfacePressureConstraint' , visualization = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.000', showVisuScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    rearLeftCavity.createObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    rearRightCavity = model.createChild('rearRightCavity')
    rearRightCavity.createObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Rear-Right-cavity_collis.stl')
    rearRightCavity.createObject('Mesh' , src = '@loader', name = 'topo')
    rearRightCavity.createObject('MechanicalObject' , name = 'rearRightCavity')
    rearRightCavity.createObject('SurfacePressureConstraint' , visualization = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.00', showVisuScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    rearRightCavity.createObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    frontLeftCavity = model.createChild('frontLeftCavity')
    frontLeftCavity.createObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Front-Left-cavity_collis.stl')
    frontLeftCavity.createObject('Mesh' , src = '@loader', name = 'topo')
    frontLeftCavity.createObject('MechanicalObject' , name = 'frontLeftCavity')
    frontLeftCavity.createObject('SurfacePressureConstraint' , visualization = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.000', showVisuScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    frontLeftCavity.createObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')


    frontRightCavity = model.createChild('frontRightCavity')
    frontRightCavity.createObject('MeshSTLLoader' , translation = add(translation,[0.0, 0.0, 0.0]), rotation = add(rotation,[0.0, 0.0, 0.0]), name = 'loader', filename = path + '/mesh/quadriped_Front-Right-cavity_collis.stl')
    frontRightCavity.createObject('Mesh' , src = '@loader', name = 'topo')
    frontRightCavity.createObject('MechanicalObject' , name = 'frontRightCavity')
    frontRightCavity.createObject('SurfacePressureConstraint' , visualization = '0', name = 'SurfacePressureConstraint', valueType = 'volumeGrowth', value = '0.000', showVisuScale = '0.0002', template = 'Vec3d', triangles = '@topo.triangles')
    frontRightCavity.createObject('BarycentricMapping' , mapMasses = 'false', name = 'mapping', mapForces = 'false')

    ## Visualization
    if surfaceMeshFileName:
	    visu = model.createChild('Visual')

	    visu.createObject(	'OglModel', 
	    					filename=path+'/mesh/'+surfaceMeshFileName,
                            template='ExtVec3f',
                            color=surfaceColor,
                            rotation= add(rotation,[0.0, 0.0, 0.0]),
                            translation = add(translation,[0.0, 0.0, 0.0]))

	    visu.createObject('BarycentricMapping')

    return model


#   STLIB IMPORT
from stlib.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = 'quadriped_collision.stl'

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=1,
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
