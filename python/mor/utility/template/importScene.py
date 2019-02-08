# -*- coding: utf-8 -*-
import os
import imp
import platform

# MOR IMPORT
from mor.utility import graphScene as u

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"

# Our Original Scene IMPORT
originalScene = r'$ORIGINALSCENE'
originalScene = os.path.normpath(originalScene)
originalScene = imp.load_source(originalScene.split(slash)[-1], originalScene)

###############################################################################

def createScene(rootNode):
    # Import Original scene
    originalScene.createScene(rootNode)

    u.dumpGraphScene(rootNode)