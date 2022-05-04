# -*- coding: utf-8 -*-
import os
import sys
import imp
import platform

#   STLIB IMPORT
try:
    from stlib3.scene.wrapper import Wrapper
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

# MOR IMPORT
from mor.utility import sceneCreation as u
from mor.utility import writeScene
from mor.wrapper import replaceAndSave

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"

# Our Original Scene IMPORT
originalScene = r'$ORIGINALSCENE'
originalScene = os.path.normpath(originalScene)
originalScene = imp.load_source(originalScene.split(slash)[-1], originalScene)

# Scene parameters
nbrOfModes = $NBROFMODES
paramWrapper = $PARAMWRAPPER
packageName = '$PACKAGENAME'

# We had these differents parameters to be able to save the scene
path, param = paramWrapper
param['nbrOfModes'] = $NBROFMODES
param['save'] = True
param['animationPaths'] = $ANIMATIONPATHS

def createScene(rootNode):

    print(  "This Scene will crash : it is NORMAL\n\
            Its purpose is only to save the scene (thanks to MORWrapper)\n\
            To create the package with it afterward")

    # Import Original Scene
    # Here we use a wrapper (MORWrapper) that will allow us (with MORreplace)
    # to modify the initial scene and get informations on its structures
    # For more details on the process involved additionnal doc are with :
    #       - mor.wrapper.MORWrapper
    #       - mor.script.sceneCreationUtility

    originalScene.createScene(Wrapper(rootNode, replaceAndSave.MORreplace, paramWrapper))  # 1

    # Add MOR plugin if not found
    u.addPlugin(rootNode,"ModelOrderReduction")
    pluginName = []
    plugins = u.searchObjectClassInGraphScene(rootNode,"RequiredPlugin")
    for plugin in plugins:
        pluginName.append(plugin.pluginName)

    # Modify the scene to perform hyper-reduction according
    # to the informations collected by the wrapper

    u.modifyGraphScene(rootNode,nbrOfModes,paramWrapper)

    # We collect all the informations during 1 & 2 to be able to create with
    # writeGraphScene a SOFA scene containing only our reduced model that we can instanciate
    # as a whole component with differents usefull argument (translation/rotation/color...)
    # For more details on the process involved additionnal doc are with :
    #       - mor.wrapper.writeScene

    if packageName:
        myMORModel = replaceAndSave.myMORModel
        myModel = replaceAndSave.myModel

        nodeName = paramWrapper[0].split('/')[-1]

        writeScene.writeHeader(packageName,nbrOfModes)
        writeScene.writeGraphScene(packageName,nodeName,myMORModel,myModel)
        writeScene.writeFooter(packageName,nodeName,pluginName,rootNode.dt.value,list(rootNode.gravity.value))