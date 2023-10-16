# -*- coding: utf-8 -*-
import imp
from sys import argv

#	STLIB IMPORT
from stlib3.scene.wrapper import Wrapper

# MOR IMPORT
from mor.script import sceneCreationUtility as u

originalScene = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/diamondRobot.py'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

paramWrapper = [('/modelNode', {'paramForcefield': {'periodSaveGIE': 11, 'prepareECSW': True, 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/diamond/data/test_modes.txt', 'nbTrainingSet': 128}, 'paramMORMapping': {'input': '@../MechanicalObject', 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/diamond/data/test_modes.txt'}, 'paramMappedMatrixMapping': {'object1': '@./MechanicalObject', 'object2': '@./MechanicalObject', 'performECSW': False, 'template': 'Vec1d,Vec1d'}})]

u = SceneCreationUtility()

def createScene(rootNode):

    if (len(argv) > 1):
        stateFileName = str(argv[1])
    else:	
        stateFileName="stateFile.state"
    originalScene.createScene(rootNode)
    u.createDebug(rootNode,paramWrapper)
