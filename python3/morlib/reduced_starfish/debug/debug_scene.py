# -*- coding: utf-8 -*-
import imp
from sys import argv

#   STLIB IMPORT
from stlib3.scene.wrapper import Wrapper

# MOR IMPORT
from mor.script import sceneCreationUtility as u

originalScene = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/quadruped_snapshotGeneration.py'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

paramWrapper = [('/model', {'paramForcefield': {'periodSaveGIE': 3, 'prepareECSW': True, 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/star/data/test_modes.txt', 'nbTrainingSet': 320}, 'paramMORMapping': {'input': '@../MechanicalObject', 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/star/data/test_modes.txt'}, 'subTopo': 'modelSubTopo', 'paramMappedMatrixMapping': {'object1': '@./MechanicalObject', 'object2': '@./MechanicalObject', 'performECSW': False, 'template': 'Vec1d,Vec1d'}}), ('/model/modelSubTopo', {'paramForcefield': {'periodSaveGIE': 3, 'prepareECSW': True, 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/star/data/test_modes.txt', 'nbTrainingSet': 320}})]

def createScene(rootNode):

    if (len(argv) > 1):
        stateFileName = str(argv[1])
    else:	
        stateFileName="stateFile.state"
    originalScene.createScene(rootNode)
    u.createDebug(rootNode,paramWrapper)
