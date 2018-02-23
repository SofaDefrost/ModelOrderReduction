# -*- coding: utf-8 -*-

import os
import sys

#	STLIB IMPORT
from stlib.scene import MainHeader
from stlib.solver import DefaultSolver
from stlib.physics.deformable import ElasticMaterialObject
from stlib.physics.constraints import FixedBox

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

meshPath = '/home/felix/SOFA/plugin/ModelOrderReduction/examples/Model_Reduction/1_INPUT/Mesh_Model/'

def createScene(rootNode):

	rootNode = MainHeader(rootNode, plugins=["SofaPython","SoftRobots"], gravity=[0.0,0.0,-9810])

	modelNode = ElasticMaterialObject(
		attachedTo=rootNode,
		fromVolumeMesh=meshPath+'siliconeV0.vtu',
		withName='modelNode',
        withRotation=[90, 0.0, 0.0],
        withTranslation=[0.0, 0.0, 35],
		withTotalMass=0.5,
		withConstrain=False,
		withPoissonRatio=0.45,
		withYoungModulus=450)
	
	modelNode.createObject('GenericConstraintCorrection', solverName='Solver')
    
	FixedBox(
		atPositions=[-15, -15, -40,  15, 15, 10],
		applyTo=modelNode,
		withVisualization=True) 	

	for i in range(len(actuatorsParam)):
		cable = PullingCable(
					attachedTo=modelNode,
					withName=actuatorsParam[i]['withName'],
					withCableGeometry=actuatorsParam[i]['withCableGeometry'],
					withAPullPointLocation=actuatorsParam[i]['withAPullPointLocation'],
					withValueAs="displacement")

	return rootNode 