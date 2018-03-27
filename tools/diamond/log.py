# -*- coding: utf-8 -*-
import Sofa

def Reduced_diamond(
                  attachedTo=None,
                  name="Reduced_diamond",
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



    modelNode_MOR = attachedTo.createChild(name)
    modelNode_MOR.createObject('MechanicalObject' , name = 'MechanicalObject'  , template = 'Vec1d'  , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0'  , size = '28' )
    modelNode_MOR.createObject('EulerImplicitSolver' , name = 'EulerImplicit'  , template = '' )
    modelNode_MOR.createObject('SparseLDLSolver' , name = 'Solver'  , template = 'CompressedRowSparseMatrix3f' )
    modelNode_MOR.createObject('GenericConstraintCorrection' , solverName = 'Solver'  , name = 'GenericConstraintCorrection'  , template = '' )
    modelNode_MOR.createObject('MappedMatrixForceFieldAndMass' , name = 'MappedMatrixForceFieldAndMass'  , mappedForceField = '@./modelNode/HyperReducedFEMForceField_modelNode'  , object1 = '@./MechanicalObject'  , object2 = '@./MechanicalObject'  , listActiveNodesPath = 'data/conectivity_modelNode.txt'  , template = 'Vec1d,Vec1d'  , performECSW = '1'  , mappedMass = '@./modelNode/UniformMass' )


    modelNode = modelNode_MOR.createChild('modelNode')
    modelNode.createObject('MeshVTKLoader' , translation = translation  , rotation = rotation  , name = 'MeshLoader'  , template = ''  , filename = 'mesh/siliconeV0.vtu' )
    modelNode.createObject('TetrahedronSetTopologyContainer' , name = 'container'  , edges = '@MeshLoader.edges'  , tetrahedra = '@MeshLoader.tetras'  , template = ''  , position = '@MeshLoader.position'  , triangles = '@MeshLoader.triangles' )
    modelNode.createObject('MechanicalObject' , name = 'MechanicalObject'  , topology = '@container'  , template = 'Vec3d' )
    modelNode.createObject('UniformMass' , name = 'UniformMass'  , totalmass = '0.5'  , filename = 'unused'  , mass = '0.000307125'  , template = 'Vec3d' )
    modelNode.createObject('HyperReducedTetrahedronFEMForceField' , RIDPath = 'data/RID_modelNode.txt'  , name = 'HyperReducedFEMForceField_modelNode'  , modesPath = 'data/test_modes.txt'  , gatherBsize = ' '  , weightsPath = 'data/weight_modelNode.txt'  , youngModulus = '450'  , template = 'Vec3d'  , gatherPt = ' '  , performECSW = '1'  , method = 'large'  , poissonRatio = '0.45'  , nbModes = '28' )
    modelNode.createObject('ModelOrderReductionMapping' , input = '@../MechanicalObject'  , modesPath = 'data/test_modes.txt'  , name = 'ModelOrderReductionMapping'  , template = 'Vec1d,Vec3d'  , output = '@./MechanicalObject' )




    nord = modelNode.createChild('nord')
    nord.createObject('MechanicalObject' , scale3d = '1 1 1'  , name = 'MechanicalObject'  , template = 'Vec3d'  , translation = '0 0 0'  , rotation = '0 0 0' )
    nord.createObject('CableConstraint' , pullPoint = '0 10 30'  , name = 'CableConstraint'  , hasPullPoint = '1'  , valueType = 'displacement'  , value = '0'  , cableLength = '88.2836'  , template = 'Vec3d'  , indices = '0'  , initialCableLength = '88.2836' )
    nord.createObject('BarycentricMapping' , name = 'Mapping'  , mapForces = '0'  , mapMasses = '0'  , template = 'Vec3d,Vec3d'  , output = '@./'  , input = '@../' )


    ouest = modelNode.createChild('ouest')
    ouest.createObject('MechanicalObject' , scale3d = '1 1 1'  , name = 'MechanicalObject'  , template = 'Vec3d'  , translation = '0 0 0'  , rotation = '0 0 0' )
    ouest.createObject('CableConstraint' , pullPoint = '-10 0 30'  , name = 'CableConstraint'  , hasPullPoint = '1'  , valueType = 'displacement'  , value = '0'  , cableLength = '88.2836'  , template = 'Vec3d'  , indices = '0'  , initialCableLength = '88.2836' )
    ouest.createObject('BarycentricMapping' , name = 'Mapping'  , mapForces = '0'  , mapMasses = '0'  , template = 'Vec3d,Vec3d'  , output = '@./'  , input = '@../' )


    sud = modelNode.createChild('sud')
    sud.createObject('MechanicalObject' , scale3d = '1 1 1'  , name = 'MechanicalObject'  , template = 'Vec3d'  , translation = '0 0 0'  , rotation = '0 0 0' )
    sud.createObject('CableConstraint' , pullPoint = '0 -10 30'  , name = 'CableConstraint'  , hasPullPoint = '1'  , valueType = 'displacement'  , value = '0'  , cableLength = '88.2836'  , template = 'Vec3d'  , indices = '0'  , initialCableLength = '88.2836' )
    sud.createObject('BarycentricMapping' , name = 'Mapping'  , mapForces = '0'  , mapMasses = '0'  , template = 'Vec3d,Vec3d'  , output = '@./'  , input = '@../' )


    est = modelNode.createChild('est')
    est.createObject('MechanicalObject' , scale3d = '1 1 1'  , name = 'MechanicalObject'  , template = 'Vec3d'  , translation = '0 0 0'  , rotation = '0 0 0' )
    est.createObject('CableConstraint' , pullPoint = '10 0 30'  , name = 'CableConstraint'  , hasPullPoint = '1'  , valueType = 'displacement'  , value = '0'  , cableLength = '88.2836'  , template = 'Vec3d'  , indices = '0'  , initialCableLength = '88.2836' )
    est.createObject('BarycentricMapping' , name = 'Mapping'  , mapForces = '0'  , mapMasses = '0'  , template = 'Vec3d,Vec3d'  , output = '@./'  , input = '@../' )
