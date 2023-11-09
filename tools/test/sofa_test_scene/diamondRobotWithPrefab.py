# -*- coding: utf-8 -*-
import sys
import os

#   STLIB IMPORT
from stlib3.scene import MainHeader
from stlib3.physics.constraints import FixedBox
from stlib3.physics.deformable import ElasticMaterialObject

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

plugins=["SofaPython3","SoftRobots","ModelOrderReduction","STLIB",
         # normally plugin Sofa.Component is enough but still warning
         "Sofa.Component.Visual",
         "Sofa.Component.AnimationLoop",
         "Sofa.GL.Component.Rendering3D",
         "Sofa.Component.Constraint.Lagrangian.Solver",
         'Sofa.Component.IO.Mesh',
         'Sofa.Component.Playback',
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

meshPath = os.path.dirname(os.path.abspath(__file__))+'/mesh/'

def createScene(rootNode):

    MainHeader(rootNode,plugins=plugins,
               dt=1.0,
               gravity=[0.0, 0.0, -9810.0])

    # not in Mainheader anymore, need some update
    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', tolerance="1e-6", maxIterations="1000")
    rootNode.VisualStyle.displayFlags = 'showVisualModels showForceFields'
    # -------------------------------------------

    modelNode = ElasticMaterialObject(
        parent=rootNode,
        volumeMeshFileName=meshPath+'siliconeV0.vtu',
        name='modelNode',
        rotation=[90, 0.0, 0.0],
        translation=[0.0, 0.0, 35],
        totalMass=0.5,
        withConstrain=False,
        surfaceMeshFileName=meshPath+'surface.stl',
        surfaceColor=[0.7, 0.7, 0.7, 0.7],
        poissonRatio=0.45,
        youngModulus=450)

    FixedBox(
        atPositions=[-15, -15, -40,  15, 15, 10],
        applyTo=modelNode,
        doVisualization=True)

    for i in range(len(actuatorsParam)):
        PullingCable(
            attachedTo=modelNode,
            name=actuatorsParam[i]['withName'],
            cableGeometry=actuatorsParam[i]['withCableGeometry'],
            pullPointLocation=actuatorsParam[i]['withAPullPointLocation'],
            valueType="displacement")

    return rootNode
