# -*- coding: utf-8 -*-
import Sofa
import os
from math import cos,sin,pi

path = os.path.dirname(os.path.abspath(__file__))

def addTripletList(newTriplet,oldTriplet):
    # print('oldTriplet : ',oldTriplet)
    if any(isinstance(el, list) for el in oldTriplet):
        # print('List : ',newTriplet)
        triplet = []
        for pts in oldTriplet:
            triplet.append( [newTriplet[i]+pts[i] for i in range(len(newTriplet))] )
            # print('triplet : ',oldTriplet)
        return triplet
    else:
        # print('PTS : ',newTriplet)
        triplet = [newTriplet[i]+oldTriplet[i] for i in range(len(newTriplet))] 
        # print('triplet : ',oldTriplet)
        return triplet

def subTripletList(newTriplet,oldTriplet):
    if any(isinstance(el, list) for el in oldTriplet):
        triplet = []
        for pts in oldTriplet:
            triplet.append( [pts[i]-newTriplet[i] for i in range(len(newTriplet))] )
        return triplet
    else:
        triplet = [oldTriplet[i]-newTriplet[i] for i in range(len(newTriplet))] 
        return triplet

def rotate(rotation,boxRoiPts):
    # convert rad
    thetaX = rotation[0] * pi / 180
    thetaY = rotation[1] * pi / 180
    thetaZ = rotation[2] * pi / 180

    if any(isinstance(el, list) for el in boxRoiPts):
        # print('List : ',newTriplet)
        triplet = []
        for pts in boxRoiPts:

            x = pts[0]
            y = pts[1]
            z = pts[2]
            
            # X rotation
            Y =  y*cos(thetaX) - z*sin(thetaX)
            Z =  y*sin(thetaX) + z*cos(thetaX)
            # Y rotation
            tmp = x
            X =  x*cos(thetaY) + Z*sin(thetaY) 
            Z =  Z*cos(thetaY) - tmp*sin(thetaY) 
            # Z rotation
            tmp = X
            X =  X*cos(thetaZ) - Y*sin(thetaZ) 
            Y =  tmp*sin(thetaZ) + Y*cos(thetaZ) 


            pts[0] = X
            pts[1] = Y
            pts[2] = Z

            # print('rotate boxRoiPts :'+str(boxRoiPts))
            return boxRoiPts


    else:


        x = boxRoiPts[0]
        y = boxRoiPts[1]
        z = boxRoiPts[2]
        
        # X rotation
        Y =  y*cos(thetaX) - z*sin(thetaX)
        Z =  y*sin(thetaX) + z*cos(thetaX)
        # Y rotation
        tmp = x
        X =  x*cos(thetaY) + Z*sin(thetaY) 
        Z =  Z*cos(thetaY) - tmp*sin(thetaY) 
        # Z rotation
        tmp = X
        X =  X*cos(thetaZ) - Y*sin(thetaZ) 
        Y =  tmp*sin(thetaZ) + Y*cos(thetaZ) 


        boxRoiPts[0] = X
        boxRoiPts[1] = Y
        boxRoiPts[2] = Z

        # print('rotate boxRoiPts :'+str(boxRoiPts))
        return boxRoiPts

# for i in range(len(pts)/3):

#     x = boxRoiPts[i*3]
#     y = boxRoiPts[i*3+1]
#     z = boxRoiPts[i*3+2]
    
#     # X rotation
#     Y =  y*cos(thetaX) - z*sin(thetaX)
#     Z =  y*sin(thetaX) + z*cos(thetaX)
#     # Y rotation
#     tmp = x
#     X =  x*cos(thetaY) + Z*sin(thetaY) 
#     Z =  Z*cos(thetaY) - tmp*sin(thetaY) 
#     # Z rotation
#     tmp = X
#     X =  X*cos(thetaZ) - Y*sin(thetaZ) 
#     Y =  tmp*sin(thetaZ) + Y*cos(thetaZ) 


#     boxRoiPts[i*3] = X
#     boxRoiPts[i*3+1] = Y
#     boxRoiPts[i*3+2] = Z

# # print('rotate boxRoiPts :'+str(boxRoiPts))
# return boxRoiPts

def translate(translation,boxRoiPts):
    print(translation)
    print(boxRoiPts)
    for i in range(len(boxRoiPts)/3):
        boxRoiPts[i*3] += translation[0]
        boxRoiPts[i*3+1] += translation[1]
        boxRoiPts[i*3+2] += translation[2]

    print('translate boxRoiPts :'+str(boxRoiPts))
    return boxRoiPts

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
    modelNode_MOR.createObject('EulerImplicit')
    modelNode_MOR.createObject('SparseLDLSolver' , name = 'Solver')
    modelNode_MOR.createObject('GenericConstraintCorrection' , solverName = 'Solver')
    modelNode_MOR.createObject('MechanicalObject' , position = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', template = 'Vec1d')
    modelNode_MOR.createObject('MappedMatrixForceFieldAndMass' , mappedForceField = '@./modelNode/HyperReducedFEMForceField_modelNode', object1 = '@./MechanicalObject', object2 = '@./MechanicalObject', listActiveNodesPath = path + '/data/conectivity_modelNode.txt', template = 'Vec1d,Vec1d', performECSW = 'True', mappedMass = '@./modelNode/UniformMass')


    modelNode = modelNode_MOR.createChild('modelNode')
    modelNode.createObject('MeshVTKLoader' , rotation = addTripletList(rotation,[90, 0.0, 0.0]), translation = addTripletList(translation,[0.0, 0.0, 35]), name = 'MeshLoader', filename = path + '/mesh/siliconeV0.vtu')
    modelNode.createObject('TetrahedronSetTopologyContainer' , src = '@MeshLoader', name = 'container')
    modelNode.createObject('MechanicalObject' , template = 'Vec3d')
    modelNode.createObject('UniformMass' , totalmass = '0.5')
    modelNode.createObject('HyperReducedTetrahedronFEMForceField' , RIDPath = path + '/data/RID_modelNode.txt', name = 'HyperReducedFEMForceField_modelNode', weightsPath = path + '/data/weight_modelNode.txt', youngModulus = '450', modesPath = path + '/data/test_modes.txt', performECSW = 'True', poissonRatio = '0.45', nbModes = '28')
    modelNode.createObject('ModelOrderReductionMapping' , input = '@../MechanicalObject', modesPath = path + '/data/test_modes.txt', output = '@./MechanicalObject')


    nord = modelNode.createChild('nord')
    nord.createObject('MechanicalObject' , position = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [[0, 97, 45]])))), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    nord.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [0, 10, 30])))), value = '0.0')
    nord.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    ouest = modelNode.createChild('ouest')
    ouest.createObject('MechanicalObject' , position = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [[-97, 0, 45]])))), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    ouest.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [-10, 0, 30])))), value = '0.0')
    ouest.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    sud = modelNode.createChild('sud')
    sud.createObject('MechanicalObject' , position = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [[0, -97, 45]])))), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    sud.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [0, -10, 30])))), value = '0.0')
    sud.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')


    est = modelNode.createChild('est')
    est.createObject('MechanicalObject' , position = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [[97, 0, 45]])))), rotation = [0.0, 0.0, 0.0], scale = '1.0', translation = [0.0, 0.0, 0.0])
    est.createObject('CableConstraint' , indices = [0], hasPullPoint = 'True', valueType = 'displacement', pullPoint = addTripletList([0.0, 0.0, 35] , addTripletList(translation,rotate(rotation, subTripletList ([0.0, 0.0, 35] , [10, 0, 30])))), value = '0.0')
    est.createObject('BarycentricMapping' , mapMasses = 'False', name = 'Mapping', mapForces = 'False')

    ## Visualization
    if surfaceMeshFileName:
	    visu = modelNode.createChild('Visual')

	    visu.createObject(	'OglModel', 
	    					filename=path+'/mesh/'+surfaceMeshFileName,
                            template='ExtVec3f',
                            color=surfaceColor,
                            rotation= addTripletList(rotation,[90, 0.0, 0.0]),
                            translation = addTripletList(translation,[0.0, 0.0, 35]))

	    visu.createObject('BarycentricMapping')

    return modelNode


#   STLIB IMPORT
from stlib.scene import MainHeader
def createScene(rootNode):
    surfaceMeshFileName = ''

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=1,
                        gravity=[0.0,0.0,-9810])

    for i in range(5):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_blue", 
                        rotation=[60.0*i, 0.0, 0.0],
                        translation=[i*200, 0.0, 0.0],
                        surfaceColor=[0.0, 0.0, 1, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
    for i in range(5):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_white", 
                        rotation=[0.0, 80.0*i, 0.0],
                        translation=[i*200, 200.0, -200.0],
                        surfaceColor=[0.5, 0.5, 0.5, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)

    for i in range(5):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_red", 
                        rotation=[0.0, 0.0, i*70.0],
                        translation=[i*200, 400.0, -400.0],
                        surfaceColor=[1, 0.0, 0.0, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
