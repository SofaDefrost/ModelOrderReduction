# -*- coding: utf-8 -*-
import imp

# MOR IMPORT
from mor.utility import graphScene as u

# Our Original Scene IMPORT
originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

###############################################################################

def createScene(rootNode):
    # Import Original scene
    originalScene.createScene(rootNode)

    u.dumpGraphScene(rootNode)