# -*- coding: utf-8 -*-
import sys
import os

#   STLIB IMPORT
from stlib3.physics.constraints import FixedBox
from stlib3.visuals import VisualModel
from stlib3.physics.deformable import ElasticMaterialObject

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

    rootNode.addObject('RequiredPlugin', pluginName=plugins, printLog=False)
    
    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver', tolerance="1e-6", maxIterations="1000")
    rootNode.addObject('OglSceneFrame', style="Arrows", alignment="TopRight")
    rootNode.addObject('VisualStyle', displayFlags='showVisualModels showForceFields')

    rootNode.findData('gravity').value=[0.0,0.0,-9810];
    rootNode.findData('dt').value=1


    volumeMeshFileName=meshPath+'diamond_4k_tet.vtu'
    rotation=[90, 0.0, 0.0]
    translation=[0.0, 0.0, 35]
    totalMass=0.5
    surfaceMeshFileName=meshPath+'surface.stl'
    surfaceColor=[0.7, 0.7, 0.7, 0.7]
    poissonRatio=0.45
    youngModulus=450
    scale=[1., 1., 1.]


    modelNode = rootNode.addChild('modelNode')
    modelNode.addObject('EulerImplicitSolver', name='integration')
    modelNode.addObject('SparseLDLSolver', name="solver", template='CompressedRowSparseMatrixMat3x3d')
    loader = modelNode.addObject('MeshVTKLoader', name='loader', filename=volumeMeshFileName,
                                 rotation=list(rotation), translation=list(translation),
                                 scale3d=list(scale))

    # loader.tetras.getLinkPath() AND loader.position.getLinkPath() ---> DO NOT WORK
    # When you change the scene for the HyperReduction, seems to update the link path to correct new path
    # BUT does not load the loader data anymore
    modelNode.addObject('TetrahedronSetTopologyContainer', position='@loader.position',
                                    tetras='@loader.tetrahedra', name='container')
    modelNode.addObject('MechanicalObject', template='Vec3', name='dofs')
    modelNode.addObject('UniformMass', totalMass=totalMass, name='mass')
    modelNode.addObject('TetrahedronFEMForceField', template='Vec3',
                                     method='large', name='forcefield',
                                     poissonRatio=poissonRatio, youngModulus=youngModulus)

    visualmodel = modelNode.addChild('visualmodel')
    visualmodel.addObject('MeshSTLLoader', name='loader', filename=surfaceMeshFileName)
    visualmodel.addObject('OglModel', name="OglModel", src="@loader",
                   rotation=list(rotation),
                   translation=list(translation),
                   scale3d=list(scale),
                   color=list(surfaceColor), updateNormals=False)
    visualmodel.addObject('BarycentricMapping', name='mapping')

    modelNode.addObject('GenericConstraintCorrection', linearSolver='@solver')

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