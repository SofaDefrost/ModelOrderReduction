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
    rootNode.findData('dt').value=1

    plugins=["SofaPython3","SoftRobots","ModelOrderReduction","STLIB",
             "Sofa.Component.Visual",
             "Sofa.Component.AnimationLoop",
             "Sofa.GL.Component.Rendering3D",
             "Sofa.Component.Constraint.Lagrangian.Solver",
             'Sofa.Component.Constraint.Lagrangian.Correction', # Needed to use components [GenericConstraintCorrection]  
             'Sofa.Component.Engine.Select', # Needed to use components [BoxROI]  
             'Sofa.Component.LinearSolver.Direct', # Needed to use components [SparseLDLSolver]  
             'Sofa.Component.Mapping.Linear', # Needed to use components [BarycentricMapping]  
             'Sofa.Component.Mass', # Needed to use components [UniformMass]  
             'Sofa.Component.ODESolver.Backward', # Needed to use components [EulerImplicitSolver]  
             'Sofa.Component.SolidMechanics.FEM.Elastic', # Needed to use components [TetrahedronFEMForceField]  
             'Sofa.Component.SolidMechanics.Spring', # Needed to use components [RestShapeSpringsForceField]  
             'Sofa.Component.StateContainer', # Needed to use components [MechanicalObject]  
             'Sofa.Component.Topology.Container.Dynamic'] # Needed to use components [TetrahedronSetTopologyContainer]  

    for name in plugins:
        rootNode.addObject('RequiredPlugin', name=name, printLog=False)
        
    rootNode.addObject('OglSceneFrame', style="Arrows", alignment="TopRight")

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', tolerance="1e-6", maxIterations="1000")


    modelNode = rootNode.addChild(ElasticMaterialObject(
        attachedTo=rootNode,
        volumeMeshFileName=meshPath+'siliconeV0.vtu',
        name='modelNode',
        rotation=[90, 0.0, 0.0],
        translation=[0.0, 0.0, 35],
        totalMass=0.5,
        withConstrain=False,
        surfaceMeshFileName=meshPath+'surface.stl',
        surfaceColor=[0.7, 0.7, 0.7, 0.7],
        poissonRatio=0.45,
        youngModulus=450))
    
    modelNode.addObject('GenericConstraintCorrection', linearSolver='@solver')

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
