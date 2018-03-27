#   STLIB IMPORT
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import saveReducedModelWrapper

import mySavedScene as originalScene

nodesToReduce ='/model'
toKeep = ["model","model_MOR","modelSubTopo","centerCavity","rearLeftCavity","rearRightCavity","frontLeftCavity","frontRightCavity"]

paramWrapper = {
	'nodesToReduce' : nodesToReduce,
	'toKeep' : toKeep,
	'originalScene' : 'diamond'
}

def MORreplace(node,type,newParam,initialParam):
	# do nothing
	return None

def createScene(rootNode):
    
    originalScene.createScene(saveReducedModelWrapper.MORWrapper(rootNode, MORreplace, paramWrapper, log='log.py')) 
