import Sofa

#   STLIB IMPORT
from stlib.scene import MainHeader

# MOR IMPORT
from mor.reducedModel.reduced_diamond import Reduced_diamond

def createScene(rootNode):
    surfaceMeshFileName = 'surface.stl'

    MainHeader(rootNode,plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
                        dt=1,
                        gravity=[0.0,0.0,-9810])

    translate = 200
    rotationBlue = 60.0
    rotationWhite = 80
    rotationRed = 70

    for i in range(5):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_blue", 
                        rotation=[rotationBlue*i, 0.0, 0.0],
                        translation=[i*translate, 0.0, 0.0],
                        surfaceColor=[0.0, 0.0, 1, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)
    for i in range(5):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_white", 
                        rotation=[0.0, rotationWhite*i, 0.0],
                        translation=[i*translate, translate, -translate],
                        surfaceColor=[0.5, 0.5, 0.5, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)

    for i in range(5):

        Reduced_diamond(rootNode,
                        name="Reduced_diamond_red", 
                        rotation=[0.0, 0.0, i*rotationRed],
                        translation=[i*translate, 2*translate, -2*translate],
                        surfaceColor=[1, 0.0, 0.0, 0.5],
                        surfaceMeshFileName=surfaceMeshFileName)