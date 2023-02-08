# -*- coding: utf-8 -*-

import os
import sys

#   STLIB IMPORT
from stlib3.scene import MainHeader
from stlib3.solver import DefaultSolver
from stlib3.physics.deformable import ElasticMaterialObject
from stlib3.physics.constraints import FixedBox

# SOFTROBOTS IMPORT
from softrobots.actuators import PullingCable

actuatorsParam = [
        {'withName' : 'nord',
         'withCableGeometry' : [[0, 97, 45]],
         'withAPullPointLocation' : [0, 10, 30]
        },
        {'withName' : 'ouest',
         'withCableGeometry' : [[-97, 0, 45]],
         'withAPullPointLocation' : [-10, 0, 30]
        },
        {'withName' : 'sud',
         'withCableGeometry' : [[0, -97, 45]],
         'withAPullPointLocation' : [0, -10, 30]
        },
        {'withName' : 'est',
         'withCableGeometry' : [[97, 0, 45]],
         'withAPullPointLocation' : [10, 0, 30]
        }
    ]

meshPath = os.path.dirname(os.path.abspath(__file__))+'/mesh/'

def createScene(rootNode):

    rootNode.addObject('VisualStyle', displayFlags='showVisualModels showForceFields')

    rootNode.findData('gravity').value=[0.0,0.0,-9810];
    rootNode.findData('dt').value=0.1

    plugins=["SofaPython","SoftRobots","ModelOrderReduction"]
    for name in plugins:
        rootNode.addObject('RequiredPlugin', name=name, printLog=False)
        
    rootNode.addObject('OglSceneFrame', style="Arrows", alignment="TopRight")

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', tolerance="1e-6", maxIterations="1000")

    modelNode = rootNode.addChild('modelNode')
    modelNode.addObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
    modelNode.addObject('SparseLDLSolver', name="solver")
    modelNode.addObject('MeshVTKLoader', name="loader", filename=meshPath+'siliconeV0.vtu', rotation=[90,0,0], translation=[0,0,35])
    modelNode.addObject('TetrahedronSetTopologyContainer', src="@loader")
    modelNode.addObject('MechanicalObject', name="tetras", template="Vec3d", showIndices="false", showIndicesScale="4e-5")
    modelNode.addObject('UniformMass', totalMass="0.5")
    poissonRatio = 0.45
    youngModulus = 450
    mu_ = youngModulus/(2*(1+poissonRatio))
    lambda_ = youngModulus*poissonRatio/((1-2*poissonRatio)*(1+poissonRatio))
    k0_ = youngModulus/(3*(1-2*poissonRatio))
    modelNode.addObject('TetrahedronHyperelasticityFEMForceField',materialName="StVenantKirchhoff", ParameterSet=str(mu_) + " " + str(lambda_),AnisotropyDirections="",printLog=False)
    #modelNode.addObject('TetrahedronHyperelasticityFEMForceField',materialName="NeoHookean", ParameterSet=str(mu_) + " " + str(k0_), AnisotropyDirections="")

    
    modelNode.addObject('GenericConstraintCorrection', solverName='solver')

    FixedBox(
        atPositions=[-15, -15, -40,  15, 15, 10],
        applyTo=modelNode,
        doVisualization=True)       

    for i in range(len(actuatorsParam)):
        cable = PullingCable(
                    attachedTo=modelNode,
                    name=actuatorsParam[i]['withName'],
                    cableGeometry=actuatorsParam[i]['withCableGeometry'],
                    pullPointLocation=actuatorsParam[i]['withAPullPointLocation'],
                    valueType="displacement")

    return rootNode
