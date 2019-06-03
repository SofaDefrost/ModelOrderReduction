# -*- coding: utf-8 -*-
import os
import imp
import platform

#   STLIB IMPORT
try:
    from splib.animation import AnimationManager , animate
    from stlib.scene.wrapper import Wrapper
    from splib.scenegraph import *
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

# MOR IMPORT
from mor import animation
from mor.reduction.container import ObjToAnimate
from mor.utility import sceneCreation as u

slash = '/'
if "Windows" in platform.platform():
    slash = "\\"

# Our Original Scene IMPORT
originalScene = r'$ORIGINALSCENE'
originalScene = os.path.normpath(originalScene)
originalScene = imp.load_source(originalScene.split(slash)[-1], originalScene)

# Animation parameters
listObjToAnimate = []
#for $obj in $LISTOBJTOANIMATE:
listObjToAnimate.append(ObjToAnimate('$obj.location',$obj.animFct,duration=$obj.duration,**$obj.params))
#end for
phase = []
#for $item in $PHASE
phase.append($item)
#end for
nbIterations = $nbIterations
paramWrapper = $PARAMWRAPPER
phaseToSave = $PHASETOSAVE

###############################################################################

def createScene(rootNode):
    print ("Scene Phase :"+str(phase))

    # Import Original scene

    originalScene.createScene(rootNode)
    dt = rootNode.dt
    timeExe = nbIterations * dt

    # Add Animation Manager to Scene
    # (ie: python script controller to which we will pass our differents animations)
    # more details at splib.animation.AnimationManager (https://stlib.readthedocs.io/en/latest/)

    if isinstance(rootNode, Wrapper):
        AnimationManager(rootNode.node)
    else:
        AnimationManager(rootNode)

    # Now that we have the AnimationManager & a list of the nodes we want to animate
    # we can add an animation to then according to the arguments in listObjToAnimate

    u.addAnimation(rootNode,phase,timeExe,dt,listObjToAnimate)

    # Now that all the animations are defined we need to record their results
    # for that we take the parent node normally given as an argument in paramWrapper

    path, param = paramWrapper
    myParent = get(rootNode,path[1:])

    # We need rest_position and because it is normally always the same we record it one time
    # during the first phase with the argument writeX0 put to True
    if phase == phaseToSave:
        myParent.createObject('WriteState', filename="stateFile.state",period=listObjToAnimate[0].params["incrPeriod"]*dt,
                                            writeX="1", writeX0="1", writeV="0")
    else :
        myParent.createObject('WriteState', filename="stateFile.state", period=listObjToAnimate[0].params["incrPeriod"]*dt,
                                            writeX="1", writeX0="0", writeV="0")

    # If you want to save also the velocity uncomment the what is below.
    # Then after if you give to **ReduceModel** *saveVelocitySnapshots = True* as parameter
    # all the different velocity saved will be added to one file as the stateFile

    # myParent.createObject('WriteState', filename="stateFileVelocity.state",period=listObjToAnimate[0].params["incrPeriod"]*dt,
    #                                       writeX = "0", writeX0 = "0", writeV = "1")