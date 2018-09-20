# -*- coding: utf-8 -*-
import imp
from sys import argv

#   STLIB IMPORT
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.script import sceneCreationUtility as u

originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

paramWrapper = $PARAMWRAPPER

def createScene(rootNode):

    if (len(argv) > 1):
        stateFileName = str(argv[1])
    else:	
        stateFileName="stateFile.state"
    originalScene.createScene(rootNode)
    u.createDebug(rootNode,paramWrapper,stateFileName)