# -*- coding: utf-8 -*-

import os
import sys

#	STLIB IMPORT
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

	rootNode = MainHeader(	rootNode, 
							plugins=["SofaPython","SoftRobots","ModelOrderReduction"],
							dt=1,
							gravity=[0.0,0.0,-9810])

	modelNode = ElasticMaterialObject(
		attachedTo=rootNode,
		volumeMeshFileName=meshPath+'siliconeV0.vtu',
		name='modelNode',
        rotation=[90, 0.0, 0.0],
        translation=[0.0, 0.0, 35],
		totalMass=0.5,
		withConstrain=False,
		# surfaceMeshFileName=meshPath+'surface.stl',
		# surfaceColor=[0.7, 0.7, 0.7, 0.7],
		poissonRatio=0.45,
		youngModulus=450)
	
	modelNode.addObject('GenericConstraintCorrection', solverName='Solver')
	# modelNode.addObject('WriteState', filename="init_myDiamondQuiteFine.vtu.state", period='0.1',writeX="0", writeX0="1", writeV="0")

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
