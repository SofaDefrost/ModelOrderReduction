# -*- coding: utf-8 -*-
import os
import platform

# MOR IMPORT
from mor.utility import graphScene 
from mor.utility import utility as u 


# Our Original Scene IMPORT
originalScene = r'$ORIGINALSCENE'
originalScene = os.path.normpath(originalScene)
originalScene = u.load_source(originalScene.split(os.sep)[-1], originalScene)


def createScene(rootNode):
    # Import Original scene
    originalScene.createScene(rootNode)

    graphScene.dumpGraphScene(rootNode)