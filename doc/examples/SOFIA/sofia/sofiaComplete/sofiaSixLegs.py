# -*- coding: utf-8 -*-
import os
import Sofa
from numpy import add,multiply
from splib.numerics import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sofiaLeg import SofiaLeg
from reduced_sofiaLeg import Reduced_SofiaLeg

from controller import SofiaController

path = os.path.dirname(os.path.abspath(__file__))
meshPath = path + '/mesh/'

def SofiaSixLegs(
                  attachedTo=None,
                  name="Reduced_sofia",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
                  scale=[1, 1, 1],
                  surfaceMeshFileName=False,
                  reduced=False,
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

        scale (vec3f): Apply a 3D scale to the object.

        poissonRatio (float):  The poisson parameter.

        youngModulus (float):  The young modulus.

        totalMass (float):   The mass is distributed according to the geometry of the object.
    """
    sofia = attachedTo.createChild(name)

    axes = [0,0,0,1]
    tmp = transformPosition([0,15,0],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale))
    tmp = tmp.tolist()
    rigidBodyPosition = tmp+axes

    rigidBodyMass = [   0.5,
                        450000,
                        0.000003,     0,            0,
                        0,            0.000075,     0, 
                        0,            0,   0.00000675]

    tmp =  [[-90, 0,  90],
            [-90, 0, -90],
            [ 90, 0,  90],
            [ 90, 0, -90],
            [ 0,  0, -105],
            [ 0,  0,  105]]

    legVisualPosition = [   transformPosition(tmp[0],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale)).tolist(),
                            transformPosition(tmp[1],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale)).tolist(),
                            transformPosition(tmp[2],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale)).tolist(),
                            transformPosition(tmp[3],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale)).tolist(),
                            transformPosition(tmp[4],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale)).tolist(),
                            transformPosition(tmp[5],TRS_to_matrix(translation, eulerRotation=rotation,scale=scale)).tolist()]
    
    # tmp = [ transformPosition(tmp[0],TRS_to_matrix([0,0,0], eulerRotation=rotation,scale=scale)).tolist(),
    #         transformPosition(tmp[1],TRS_to_matrix([0,0,0], eulerRotation=rotation,scale=scale)).tolist(),
    #         transformPosition(tmp[2],TRS_to_matrix([0,0,0], eulerRotation=rotation,scale=scale)).tolist(),
    #         transformPosition(tmp[3],TRS_to_matrix([0,0,0], eulerRotation=rotation,scale=scale)).tolist(),
    #         transformPosition(tmp[4],TRS_to_matrix([0,0,0], eulerRotation=rotation,scale=scale)).tolist(),
    #         transformPosition(tmp[5],TRS_to_matrix([0,0,0], eulerRotation=rotation,scale=scale)).tolist()]

    framePosition = []
    for i in range(len(legVisualPosition)):
        framePosition += tmp[i]+axes

    legPosition =  [[0,-15,0],
                    [0,-15,0],
                    [0,-15,0],
                    [0,-15,0],
                    [0,-15,0],
                    [0,-15,0]]



    # Body of the robot: rigid !
    BodyNode = sofia.createChild('rigidBody')
    BodyNode.createObject('EulerImplicit', name='odesolver', firstOrder=0);
    BodyNode.createObject('PCGLinearSolver', name='linearSolver',iterations=2,tolerance=1.0e-18,threshold=1.0e-30, preconditioners="preconditioner")
    BodyNode.createObject('SparseLDLSolver', name='preconditioner')
    BodyNode.createObject('MechanicalObject', template='Rigid',name='frame1', position=rigidBodyPosition) # , showObject='1', showObjectScale=15)
    BodyNode.createObject('UniformMass', showAxisSizeFactor='0.01',totalMass=0.5) #mass=rigidBodyMass) # 

    BodyNode.createObject('LinearSolverConstraintCorrection', solverName='preconditioner');
    # BodyNode.createObject('GenericConstraintCorrection', solverName='preconditioner')

    # Frame
    FramesNode= BodyNode.createChild('frames')
    FramesNode.createObject('MechanicalObject', template='Rigid',name='frame1', position=framePosition, showObject='1', showObjectScale=15)
    # FramesNode.createObject('UniformMass', totalMass=0.05, showAxisSizeFactor=0.010) # we comment it because we don't see its use
    FramesNode.createObject('RigidRigidMapping', mapMasses=0, mapForces=0)


    # RigidMappedBody
    mappedframesNode=FramesNode.createChild('mappedframesNode')
    mappedframesNode.createObject('MeshObjLoader', filename=meshPath+'body_surf.obj', name='loader', scale3d=scale, rotation=rotation, translation=translation)
    mappedframesNode.createObject('OglModel', name='mappedBodyVisual', src='@loader' ,color='blue')
    mappedframesNode.createObject('RigidMapping', globalToLocalCoords='1')

    # LEG MAPPING

    #   Here we strLink0/1/2 allow us to declare reduced & non-reduced with the same code
    #   Because with reduced leg there is a new node, ie reduced_leg --> leg, we have to adapt the paths accordingly
    if reduced:
        name = "reduced_leg"
        strLink0 = '../'
        strLink1 = 'reduced_leg'
        strLink2 = '/SofiaLeg'
        addSofia = Reduced_SofiaLeg
    else:
        name = "leg"
        strLink0 = ''
        strLink1 = 'leg'
        strLink2 = ''
        addSofia = SofiaLeg

    actuatorArg = [{'offset':40},{'offset':0},{'offset':40},{'offset':0},{'offset':40},{'offset':0}]
    actuators = []
    for i in range(6):
        
        leg , myController =    addSofia(sofia,
                                        name=name+str(i),
                                        rotation=rotation,
                                        translation=legPosition[i],
                                        scale=scale,
                                        surfaceColor=[0.0, 0.0, 1, 0.5],
                                        controller=actuatorArg[i],
                                        surfaceMeshFileName=surfaceMeshFileName)

        leg.createObject('LinearSolverConstraintCorrection', solverName='preconditioner')

        actuators.append(myController)

        if reduced:
            leg = leg.getChildren()[0]                          

        # map on rigid
        mappedLeg=leg.createChild('mappedLeg'+str(i))
        FramesNode.addChild(mappedLeg)
        mappedLeg.createObject('Mesh', position='@../../'+strLink0+strLink1+str(i)+strLink2+'/loader.position', tetrahedra='@../../'+strLink0+strLink1+str(i)+strLink2+'/loader.tetrahedra')
        mappedLeg.createObject('MechanicalObject', template='Vec3d', name='mappedLeg') # , showObject='1', showObjectScale=5)
        mappedLeg.createObject('DeformableOnRigidFrameMapping', input2='@../../'+strLink0+'rigidBody/frames', input1='@../../'+strLink0+strLink1+str(i)+strLink2+'/tetras', output='@./mappedLeg', globalToLocalCoords='0', index=i)

        #visual model
        mappedVisualLeg=mappedLeg.createChild('mappedVisaulLeg'+str(i))
        mappedVisualLeg.createObject(  'OglModel', 
                            filename=meshPath+'sofia_leg.stl',
                            template='ExtVec3f',
                            color=surfaceColor,
                            rotation= rotation,
                            translation = legVisualPosition[i],
                            scale3d = scale)
        mappedVisualLeg.createObject('BarycentricMapping')

        #mapped collision (with reduce size)
        mappedCollisionLeg=mappedLeg.createChild('mappedCollisionLeg'+str(i))
        mappedCollisionLeg.createObject('MechanicalObject', template='Vec3d', name='mappedCollisionLeg') # , showObject='1', showObjectScale=10, showColor=[1,0,1,1])
        mappedCollisionLeg.createObject('Point', color='1 0 0 1', group='1' )
        mappedCollisionLeg.createObject('SubsetMapping', indices='@../../../'+strLink0+strLink1+str(i)+strLink2+'/boxROICollision.indices', input='@../../mappedLeg'+str(i)+'/mappedLeg')

    if True:
        # print actuators
        myController = SofiaController(sofia)
        myController.init(actuators)

    return sofia


def createScene(rootNode):
    from stlib.scene import MainHeader
    from stlib.scene import ContactHeader
    from stlib.physics.rigid import Floor

    rootNode.createObject('RequiredPlugin', pluginName='SoftRobots');
    rootNode.createObject('RequiredPlugin', pluginName='ModelOrderReduction');
    rootNode.createObject('VisualStyle', displayFlags='showVisualModels showBehaviorModels showCollisionModels hideBoundingCollisionModels hideForceFields showInteractionForceFields hideWireframe');

    rootNode.findData('dt').value= 0.01;
    rootNode.findData('gravity').value= [0, -9810, 0]

    rootNode.createObject('FreeMotionAnimationLoop'); 
    rootNode.createObject('LCPConstraintSolver', mu=str(1), tolerance="1.0e-15", maxIt="10000");
    rootNode.createObject('CollisionPipeline', verbose="0");
    rootNode.createObject('BruteForceDetection', name="N2");
    rootNode.createObject('CollisionResponse', response="FrictionContact");
    rootNode.createObject('LocalMinDistance', name="Proximity", alarmDistance=10, contactDistance=1.5);


    Floor(rootNode,
        name = "Plane",
        translation=[0,-30 ,0],
        color = [1.0, 0.0, 1.0],
        isAStaticObject = True,
        uniformScale = 10)

    # With reduce legs
    SofiaSixLegs(attachedTo=rootNode,
                         name='sofia_reduced',
                         reduced=True,
                         rotation=[0,0,0],
                         translation=[-200, 0, -400])
    # Without reduced legs
    # SofiaSixLegs(attachedTo=rootNode,
    #                      name='sofia',
    #                      translation=[200, 0, 400])

    # To test translation and rotation of our obj
    # TODO fix rotation

    # translate = 600
    # rotationBlue = 60.0
    # rotationWhite = 42
    # rotationRed = 83
    
    # for i in range(5):

    #     SofiaSixLegs(rootNode,
    #                     name="Reduced_sofia_blue_"+str(i),
    #                     reduced=True, 
    #                     rotation=[ 0.0,rotationBlue*i, 0.0],
    #                     translation=[i*translate, 0.0, 0.0],
    #                     surfaceColor=[0.0, 0.0, 1, 0.5])

    # for i in range(5):

    #     SofiaSixLegs(rootNode,
    #                     name="Reduced_sofia_white_"+str(i),
    #                     reduced=True, 
    #                     rotation=[0.0, rotationWhite*i, 0.0],
    #                     translation=[i*translate, translate, -translate],
    #                     surfaceColor=[0.5, 0.5, 0.5, 0.5])

    # for i in range(5):

    #     SofiaSixLegs(rootNode,
    #                     name="Reduced_sofia_red_"+str(i),
    #                     reduced=True, 
    #                     rotation=[0.0, i*rotationRed, 0.0],
    #                     translation=[i*translate, 2*translate, -2*translate],
    #                     scale=[2,2,2],
    #                     surfaceColor=[1, 0.0, 0.0, 0.5])
