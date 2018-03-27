# -*- coding: utf-8 -*-
'''
	README

	to use this python script you need :

		- bla

		- & blabla
'''

#######################################################################
####################       IMPORT 	     	###########################
import sys
sys.path.append('/home/felix/SOFA/plugin/ModelOrderReduction/python')

from mor.script import morUtilityFunctions
from mor.script import ReduceModel


#######################################################################
####################       PARAMETERS     	###########################
"Select Directory"
# Output Dir and original scene name & path
originalScene = morUtilityFunctions.openFileName('Select the SOFA scene you want to reduce')
meshDir = morUtilityFunctions.openDirName('Select the directory containing the mesh of your scene')
# originalScene = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/quadruped_snapshotGeneration.py'
# meshDir = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/mesh'
outputDir = morUtilityFunctions.openDirName('Select the directory tha will contain all the results')

# Aniamtion Arguments
animationParam = {}

### DIAMOND ROBOT PARAM
# nodesToReduce = ['/modelNode']
# animationParam["toAnimate"] = ["nord","ouest","sud","est"]

# nbActuator = len(animationParam["toAnimate"])
# animationParam["increment"] = [5]*nbActuator
# animationParam["breathTime"] = [10]*nbActuator
# animationParam["maxPull"] = [40]*nbActuator
# addRigidBodyModes = False


### STARFISH ROBOT PARAM
nodesToReduce =[('/model','/model/modelSubTopo')]
animationParam["toAnimate"] = ["centerCavity","rearLeftCavity","rearRightCavity","frontLeftCavity","frontRightCavity"]

nbActuator = len(animationParam["toAnimate"])
animationParam["increment"] = [350,200,200,200,200]
animationParam["breathTime"] = [2]*nbActuator
animationParam["maxPull"] = [x*10 for x in animationParam["increment"]]
addRigidBodyModes = True


# Tolerance
tolModes = 0.001
tolGIE =  0.05

# Optionnal
verbose = False


#######################################################################
####################      INITIALIZATION     ##########################
reduceMyModel = ReduceModel(	originalScene,	
					            nodesToReduce,
					            animationParam,
					            tolModes,tolGIE,
					            outputDir,
					            meshDir,
					            verbose,
					            addRigidBodyModes)


#######################################################################
####################       EXECUTION     	###########################

####################    SOFA LAUNCHER       ##########################
#                                                                    #
#                           PHASE 1                                  #
#                                                                    #
#      We modify the original scene to do the first step of MOR :    #
#   we add animation to each actuators we want for our model         #
#   add a writeState componant to save the shaking resulting states  #
#                                                                    #
######################################################################
reduceMyModel.phase1()


####################    PYTHON SCRIPT       ##########################
#                                                                    #
#                           PHASE 2                                  #
#                                                                    #
#      With the previous result we combine all the generated         #
#       state files into one to be able to extract from it           #
#                       the different mode                           #
#                                                                    #
######################################################################
reduceMyModel.phase2()


####################    SOFA LAUNCHER       ##########################
#                                                                    #
#                           PHASE 3                                  #
#                                                                    #
#      We launch again a set of sofa scene with the sofa launcher    #
#      with the same previous arguments but with a different scene   #
#      This scene take the previous one and add the model order      #
#      reduction component:                                          #
#            - HyperReducedFEMForceField                             #
#            - MappedMatrixForceFieldAndMass                         #
#            - ModelOrderReductionMapping                            #
#       and produce an Hyper Reduced description of the model        #
#                                                                    #
######################################################################
reduceMyModel.phase3()


####################    PYTHON SCRIPT       ##########################
#                                                                    #
#                           PHASE 4                                  #
#                                                                    #
#      Final step : we gather again all the results of the           #
#      previous scenes into one and then compute the RID and Weigts  #
#      with it. Additionnally we also compute the Active Nodes       #
#                                                                    #
######################################################################
reduceMyModel.phase4()