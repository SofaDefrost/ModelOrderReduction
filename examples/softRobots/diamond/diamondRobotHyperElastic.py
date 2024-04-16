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
        {'withName' : 'north',
         'withCableGeometry' : [[0, 97, 45]],
         'withAPullPointLocation' : [0, 10, 30]
        },
        {'withName' : 'west',
         'withCableGeometry' : [[-97, 0, 45]],
         'withAPullPointLocation' : [-10, 0, 30]
        },
        {'withName' : 'south',
         'withCableGeometry' : [[0, -97, 45]],
         'withAPullPointLocation' : [0, -10, 30]
        },
        {'withName' : 'east',
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

    rootNode.addObject('VisualStyle', displayFlags='showVisualModels showForceFields')

    rootNode.findData('gravity').value=[0.0,0.0,-9810];
    rootNode.findData('dt').value=0.1

    rootNode.addObject('RequiredPlugin', pluginName=plugins, printLog=False)
        
    rootNode.addObject('OglSceneFrame', style="Arrows", alignment="TopRight")

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', tolerance="1e-6", maxIterations="1000")

    modelNode = rootNode.addChild('modelNode')
    modelNode.addObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
    modelNode.addObject('SparseLDLSolver', name="solver")
    modelNode.addObject('MeshVTKLoader', name="loader", filename=meshPath+'diamond_4k_tet.vtu', rotation=[90,0,0], translation=[0,0,35])
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
