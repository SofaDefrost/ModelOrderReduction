import Sofa
import os

#   STLIB IMPORT
from stlib3.scene import MainHeader
from stlib3.scene import ContactHeader
from stlib3.physics.rigid import Floor

# SOFIA IMPORT
from sofia.sofiaLeg import SofiaLeg
from sofia.reduced_sofiaLeg import Reduced_SofiaLeg
from sofia.sofiaComplete import SofiaSixLegs

path = os.path.dirname(os.path.abspath(__file__))

surfaceMeshFileName = 'sofia_leg.stl'


def createScene(rootNode):
    MainHeader(rootNode,plugins=["SofaPython","ModelOrderReduction"],
                        dt=0.01,
                        gravity=[0, -9810, 0])
    rootNode.VisualStyle.displayFlags='showVisualModels'
    rootNode.addObject('FreeMotionAnimationLoop');
    rootNode.addObject('LCPConstraintSolver', mu=str(1), tolerance="1.0e-15", maxIt="10000");
    rootNode.addObject('CollisionPipeline', verbose="0");
    rootNode.addObject('BruteForceBroadPhase', name="N2")
    rootNode.addObject('BVHNarrowPhase')
    rootNode.addObject('CollisionResponse', response="FrictionContact");
    rootNode.addObject('LocalMinDistance', name="Proximity", alarmDistance=10, contactDistance=1.5);
    rootNode.addObject('SparseLDLSolver' , name = 'preconditioner')


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
