# -*- coding: utf-8 -*-
import imp

#	STLIB IMPORT
try:
    from splib.animation import AnimationManager , animate
    from stlib.scene.wrapper import Wrapper
    from splib.scenegraph import *
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

# MOR IMPORT
from mor import animation
from mor.reduction import ObjToAnimate
from mor.utility import sceneCreation as u

# Our Original Scene IMPORT
originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

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

    path, param = paramWrapper[0]
    myParent = get(rootNode,path[1:])

    # We need rest_position and because it is normally always the same we record it one time
    # during the first phase with the argument writeX0 put to True
    if phase == phaseToSave:
        myParent.createObject('WriteState', filename="stateFile.state",period=listObjToAnimate[0].params["incrPeriod"]*dt,
                                            writeX="1", writeX0="1", writeV="0")
    else :
        myParent.createObject('WriteState', filename="stateFile.state", period=listObjToAnimate[0].params["incrPeriod"]*dt,
                                            writeX="1", writeX0="0", writeV="0")

    myParent.createObject('WriteState', filename="stateFileVelocity.state",period=listObjToAnimate[0].params["incrPeriod"]*dt,
                                          writeX = "0", writeX0 = "0", writeV = "1")