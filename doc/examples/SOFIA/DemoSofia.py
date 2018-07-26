import Sofa
import os

#   STLIB IMPORT
from stlib.scene import MainHeader
from stlib.scene import ContactHeader
from stlib.physics.rigid import Floor

# SOFIA IMPORT
from sofia.sofiaLeg import SofiaLeg
from sofia.reduced_sofiaLeg import Reduced_SofiaLeg
from sofia.sofiaComplete import SofiaSixLegs

path = os.path.dirname(os.path.abspath(__file__))

surfaceMeshFileName = 'sofia_leg.stl'


def createScene(rootNode):
    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=0.01,
                        gravity=[0, -9810, 0],
                        displayFlags='showVisualModels')

    rootNode.createObject('FreeMotionAnimationLoop'); 
    rootNode.createObject('LCPConstraintSolver', mu=str(1), tolerance="1.0e-15", maxIt="10000");
    rootNode.createObject('CollisionPipeline', verbose="0");
    rootNode.createObject('BruteForceDetection', name="N2");
    rootNode.createObject('CollisionResponse', response="FrictionContact");
    rootNode.createObject('LocalMinDistance', name="Proximity", alarmDistance=10, contactDistance=1.5);
    rootNode.createObject('SparseLDLSolver' , name = 'preconditioner')


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
    #                      reduced=True,
    #                      rotation=[0,0,0],
    #                      translation=[200, 0, 400])

    # Reduced_SofiaLeg(rootNode,
    #                 name="Reduced_SofiaLeg_blue_2", 
    #                 rotation=[0, 0.0, 0.0],
    #                 translation=[100, 0.0, -40.0],
    #                 surfaceColor=[0.0, 1, 0, 0.5],
    #                 surfaceMeshFileName=surfaceMeshFileName)

    # SofiaLeg(rootNode,
    #             name="SofiaLeg_green_1", 
    #             rotation=[0, 0.0, 0.0],
    #             translation=[100, 0.0, 0.0],
    #             surfaceColor=[0.0, 0.0, 1, 0.5],
    #             surfaceMeshFileName=surfaceMeshFileName)