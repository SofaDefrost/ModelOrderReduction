import Sofa
import os

#   STLIB IMPORT
from stlib.scene import MainHeader
from stlib.scene import ContactHeader
from stlib.physics.rigid import Floor

# MOR IMPORT
from morlib.reduced_diamond import Reduced_diamond
from morlib.reduced_starfish import Reduced_starfish
from morlib.reduced_sofiaLeg import Reduced_SofiaLeg

path = os.path.dirname(os.path.abspath(__file__))

def createScene(rootNode):
    surfaceMeshFileNameDiamond = 'surface.stl'
    surfaceMeshFileNameStrafish = 'quadriped_collision.stl'
    surfaceMeshFileNameSofia = 'sofia_leg.stl'

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=1,
                        gravity=[0.0,-9810,0.0])

    ContactHeader(rootNode,
        alarmDistance=5,
        contactDistance=1,
        frictionCoef=0.7)

    Floor(rootNode,
        name = "Plane",
        color = [1.0, 0.0, 1.0],
        isAStaticObject = True,
        uniformScale = 10)

    Reduced_diamond(rootNode,
                    name="Reduced_diamond_white",
                    rotation=[-90, 0.0, 0.0],
                    translation=[0, 50.0, 0.0],
                    surfaceColor=[0.5, 0.5, 0.5, 0.5],
                    surfaceMeshFileName=surfaceMeshFileNameDiamond)

    Reduced_starfish(rootNode,
                    name="Reduced_starfish_red",
                    rotation=[0, 90.0, 120.0],
                    translation=[300, 400.0, 100.0],
                    surfaceColor=[1, 0.0, 0.0, 0.5],
                    surfaceMeshFileName=surfaceMeshFileNameStrafish)

    Reduced_SofiaLeg(rootNode,
                    name="Reduced_sofiaLeg_blue",
                    rotation=[0, 0.0, 0.0],
                    translation=[-400, 60.0, 100.0],
                    surfaceColor=[0.0, 0.0, 1, 0.5],
                    surfaceMeshFileName=surfaceMeshFileNameSofia)