# -*- coding: utf-8 -*-

#	STLIB IMPORT
from stlib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.animation import DefaultShaking

# Because sofa launcher create a template of our scene, we need to indicate the path to our original scene
import sys
sys.path.insert(0,'/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests')

import originalScene 


#### Run manually
# A list of what you want to animate in your scene and with which parameters
toAnimate = ["nord","ouest","sud","est"]

nbActuator = len(toAnimate)
dt = 1
increment = [5]*nbActuator
breathTime = [20]*nbActuator
maxPull = [40]*nbActuator
nbIterations = [0]*nbActuator

for i in range(nbActuator):
    nbIterations[i] = ((maxPull[i]/increment[i])-1)*breathTime[i]+ (maxPull[i]/increment[i])-1

timeExe = nbIterations[0] * dt
phase = [1,1,1,1]
##################


#### with launcher
# toAnimate= $TOANIMATE
# dt = $DT
# maxPull = $MAXPULL
# breathTime = $BREATHTIME
# increment = $INCREMENT
# phase = $PHASE
# nbIterations = $nbIterations
# timeExe = nbIterations * dt
##################

print "Scene Phase :",phase
print "timeExe :",timeExe

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
			animate(DefaultShaking, {
								"target" : child ,
								"phaseTest" : phase, 
								"actuatorNb" : tmpFind,
								"actuatorMaxPull" : maxPull[tmpFind],
								"actuatorBreathTime" : breathTime[tmpFind],
								"actuatorIncrement" : increment[tmpFind],
								"breathTimeCounter" : mySingleton}, timeExe)
			tmpFind+=1
		if tmpFind >= len(toAnimate):
			myParent = child.getParents()[0]
			myParent.createObject('WriteState', filename="stateFile.state", period='0.1',writeX="1", writeX0="", writeV="0") 
			return None
		else:
			searchChildAndAnimate(child,toAnimate)


def createScene(rootNode):

	originalScene.createScene(rootNode)

	if isinstance(rootNode, Wrapper):
		AnimationManager(rootNode.node)
		searchChildAndAnimate(rootNode.node,toAnimate)
	else:
		AnimationManager(rootNode)
		searchChildAndAnimate(rootNode,toAnimate)
