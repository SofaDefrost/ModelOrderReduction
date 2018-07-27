# -*- coding: utf-8 -*-
import imp

#   STLIB IMPORT
from stlib.scene.wrapper import Wrapper

#   STLIB IMPORT
from mor.script.sceneCreationUtility import SceneCreationUtility

originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

paramWrapper = $PARAMWRAPPER

u = SceneCreationUtility()

def createScene(rootNode):

    stateFileName="stateFile.state"
    originalScene.createScene(rootNode)
    u.createDebug(rootNode,paramWrapper,stateFileName)