# -*- coding: utf-8 -*-

#	STLIB IMPORT
from stlib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.animation import defaultShaking

# Because sofa launcher create a template of our scene, we need to indicate the path to our original scene
import sys
import os
import ntpath
import importlib

#### Run manually diamond
# import originalScene
# # A list of what you want to animate in your scene and with which parameters
# toAnimate = ["nord","ouest","sud","est"]

# nbActuator = len(toAnimate)
# increment = [5]*nbActuator
# breathTime = [10]*nbActuator
# maxPull = [40]*nbActuator
# nbIterations = [0]*nbActuator
# periodSaveGIE = [x+1 for x in breathTime]

# for i in range(nbActuator):
#     nbIterations[i] = ((maxPull[i]/increment[i])*breathTime[i]) + (maxPull[i]/increment[i])

# phase = [1,1,1,1]
##################

#### Run manually starfish
# import quadruped_snapshotGeneration as originalScene
# # A list of what you want to animate in your scene and with which parameters
# toAnimate = ["centerCavity","rearLeftCavity","rearRightCavity","frontLeftCavity","frontRightCavity"]

# nbActuator = len(toAnimate)
# increment = [350,200,200,200,200]
# breathTime = [2]*nbActuator
# maxPull = [x*10 for x in increment]
# nbIterations = [0]*nbActuator
# periodSaveGIE = [x+1 for x in breathTime]

# for i in range(nbActuator):
#     nbIterations[i] = ((maxPull[i]/increment[i])*breathTime[i]) + (maxPull[i]/increment[i])

# phase = [1,1,1,1,1]
##################

#### with launcher
originalScene = '$ORIGINALSCENE'

sys.path.insert(0,os.path.dirname(os.path.abspath(originalScene)))
filename, file_extension = os.path.splitext(originalScene)
importScene = str(ntpath.basename(filename))
originalScene = importlib.import_module(importScene)
# print importScene

toAnimate= $TOANIMATE
maxPull = $MAXPULL
breathTime = $BREATHTIME
increment = $INCREMENT
phase = $PHASE
nbIterations = $nbIterations
periodSaveGIE = $PERIODSAVEGIE
##################


timeExe = 0.0
dt = 0.0
print "Scene Phase :",phase
###############################################################################

class SingletonTmp(object):
	def __init__(self, breathTime):
		self.tmp = list(breathTime)

mySingleton = SingletonTmp(breathTime)

tmpFind = 0
def searchChildAndAnimate(node,toAnimate):
    global tmpFind
    for child in node.getChildren():
        if child.name in toAnimate and tmpFind < len(toAnimate):
            print ('Animate : '+child.name)
            animate(defaultShaking, {
            "target" : child ,
            "phaseTest" : phase, 
            "actuatorNb" : tmpFind,
            "actuatorMaxPull" : maxPull[tmpFind],
            "actuatorBreathTime" : breathTime[tmpFind],
            "actuatorIncrement" : increment[tmpFind],
            "breathTimeCounter" : mySingleton}, timeExe)
            tmpFind+=1

        if tmpFind == len(toAnimate):
            myParent = child.getParents()[0]
            if phase == [0]*len(phase):
                myParent.createObject('WriteState', filename="stateFile.state", period=periodSaveGIE[0]*dt,writeX="1", writeX0="1", writeV="0") 
            else :
                myParent.createObject('WriteState', filename="stateFile.state", period=periodSaveGIE[0]*dt,writeX="1", writeX0="0", writeV="0")
            tmpFind += 1
            return None
        else:
            searchChildAndAnimate(child,toAnimate)


def createScene(rootNode):
	global timeExe, dt

	originalScene.createScene(rootNode)
	dt = rootNode.dt
	timeExe = nbIterations * dt 
	# timeExe = nbIterations[0] * rootNode.dt
	print "timeExe :",timeExe

	if isinstance(rootNode, Wrapper):
		AnimationManager(rootNode.node)
		searchChildAndAnimate(rootNode.node,toAnimate)
	else:
		AnimationManager(rootNode)
		searchChildAndAnimate(rootNode,toAnimate)
