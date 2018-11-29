# -*- coding: utf-8 -*-
import imp
from sys import argv

#   STLIB IMPORT
try:
	from stlib.scene.wrapper import Wrapper
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

# MOR IMPORT
from mor.utility import sceneCreation as u

originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

paramWrapper = $PARAMWRAPPER

def createScene(rootNode):

    if (len(argv) > 1):
        stateFileName = str(argv[1])
    else:	
        stateFileName="stateFile.state"
    originalScene.createScene(rootNode)

    path , param = paramWrapper[0]  
    pathToNode = path[1:]

    u.createDebug(rootNode,paramWrapper,stateFileName)