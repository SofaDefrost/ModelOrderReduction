# -*- coding: utf-8 -*-
import os
import imp
import platform
from sys import argv

#   STLIB IMPORT
try:
	from stlib3.scene.wrapper import Wrapper
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

# MOR IMPORT
from mor.utility import sceneCreation as u

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"

# Our Original Scene IMPORT
originalScene = r'C:\projects\sofa_dev\sofa_plugins\MOR\tools\test\sofa_test_scene\hexaBeam_gravity.py'
originalScene = os.path.normpath(originalScene)
originalScene = imp.load_source(originalScene.split(slash)[-1], originalScene)

paramWrapper = ('/M1', {'paramForcefield': {'prepareECSW': True, 'modesPath': 'C:\\projects\\sofa_dev\\sofa_plugins\\MOR\\tools\\test\\sofa_test_scene\\hexaBeam_test_Res\\data\\modes.txt', 'periodSaveGIE': 6, 'nbTrainingSet': 5}, 'paramMORMapping': {'input': '@../MechanicalObject', 'modesPath': 'C:\\projects\\sofa_dev\\sofa_plugins\\MOR\\tools\\test\\sofa_test_scene\\hexaBeam_test_Res\\data\\modes.txt'}, 'paramMappedMatrixMapping': {'nodeToParse': '@.//M1', 'template': 'Vec1d,Vec1d', 'object1': '@./MechanicalObject', 'object2': '@./MechanicalObject', 'timeInvariantMapping1': True, 'timeInvariantMapping2': True, 'performECSW': False}})

def createScene(rootNode):

    if (len(argv) > 1):
        stateFileName = str(argv[1])
    else:	
        stateFileName="stateFile.state"
    originalScene.createScene(rootNode)

    path , param = paramWrapper
    pathToNode = path[1:]

    u.createDebug(rootNode,pathToNode,stateFileName)