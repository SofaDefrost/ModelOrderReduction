#   STLIB IMPORT
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import saveReducedModelWrapper

import mySavedScene as originalScene

nodesToReduce = '/modelNode'
animationParam = ["nord","ouest","sud","est"]

paramWrapper = {
	'nodesToReduce' : nodesToReduce,
	'toKeep' : animationParam,
	'originalScene' : 'diamond'
}

def MORreplace(node,type,newParam,initialParam):
	# do nothing
	return None

def createScene(rootNode):
    
    originalScene.createScene(saveReducedModelWrapper.MORWrapper(rootNode, MORreplace, paramWrapper, log='log.py')) 
