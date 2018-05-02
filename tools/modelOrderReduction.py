# -*- coding: utf-8 -*-
'''
    README

    to use this python script you need :

        - bla

        - & blabla
'''

#######################################################################
####################       IMPORT           ###########################
import os
import sys
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../python') # TO CHANGE


# MOR IMPORT
from mor.animation import defaultShaking
from mor.script import morUtilityFunctions
from mor.script import ReduceModel
from mor.script import ObjToAnimate

#######################################################################
####################       PARAMETERS       ###########################

# Select Output Dir and original scene name & path
originalScene = morUtilityFunctions.openFileName('Select the SOFA scene you want to reduce')
meshDir = morUtilityFunctions.openDirName('Select the directory containing the mesh of your scene')
outputDir = morUtilityFunctions.openDirName('Select the directory tha will contain all the results')

# originalScene = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/diamondRobot.py'
# meshDir = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/mesh'
# outputDir = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/test'

### DIAMOND ROBOT PARAM
nodesToReduce = ['/modelNode']
nord = ObjToAnimate("nord","animation.defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
sud = ObjToAnimate("sud","animation.defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
est = ObjToAnimate("est","animation.defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
ouest = ObjToAnimate("ouest","animation.defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
listObjToAnimate = [nord,ouest,sud,est]
addRigidBodyModes = [0,0,0]

### STARFISH ROBOT PARAM
# nodesToReduce =[('/model','/model/modelSubTopo')]
# centerCavity = ObjToAnimate("centerCavity","animation.defaultShaking", incr=350,incrPeriod=2,rangeOfAction=3500)
# rearLeftCavity = ObjToAnimate("rearLeftCavity","animation.defaultShaking", incr=200,incrPeriod=2,rangeOfAction=2000)
# rearRightCavity = ObjToAnimate("rearRightCavity","animation.defaultShaking", incr=200,incrPeriod=2,rangeOfAction=2000)
# frontLeftCavity = ObjToAnimate("frontLeftCavity","animation.defaultShaking", incr=200,incrPeriod=2,rangeOfAction=2000)
# frontRightCavity = ObjToAnimate("frontRightCavity","animation.defaultShaking", incr=200,incrPeriod=2,rangeOfAction=2000)
# listObjToAnimate = [centerCavity,rearLeftCavity,rearRightCavity,frontLeftCavity,frontRightCavity]
# addRigidBodyModes = [1,1,1]

### OCTOPUS PARAM
# nodesToReduce = ['/octopus']
# animationParam["toAnimate"] = ["actuatorTentacle0","actuatorTentacle1","actuatorTentacle2","actuatorTentacle3","actuatorTentacle04"]

# nbActuator = len(animationParam["toAnimate"])
# animationParam["increment"] = [5]*nbActuator
# animationParam["breathTime"] = [10]*nbActuator
# animationParam["maxPull"] = [60]*nbActuator
# addRigidBodyModes = [0,0,0]

### TRUNK PARAM 
# nodesToReduce = ['/trunk']
# animationParam["toAnimate"] = ["cableL0","cableL1","cableL2","cableL3","cableS0","cableS1","cableS2","cableS3"]

# nbActuator = len(animationParam["toAnimate"])
# animationParam["increment"] = [6]*4+[3]*4
# animationParam["breathTime"] = [4]*nbActuator
# animationParam["maxPull"] = [30]*4+[15]*4
# addRigidBodyModes = [0,0,0]

# Tolerance
tolModes = 0.001
tolGIE =  0.05

# Optionnal
verbose = False

packageName = 'test'
addToLib = False

#######################################################################
####################      INITIALIZATION     ##########################
reduceMyModel = ReduceModel(    originalScene,  
                                nodesToReduce,
                                listObjToAnimate,
                                tolModes,tolGIE,
                                outputDir,
                                meshDir,
                                packageName = packageName,
                                addToLib = addToLib,
                                verbose = verbose,
                                addRigidBodyModes = addRigidBodyModes)


#######################################################################
####################       EXECUTION        ###########################

reduceMyModel.performReduction() # phasesToExecute=list(range(8)),nbrOfModes=18)

# ####################    SOFA LAUNCHER       ##########################
# #                                                                    #
# #                           PHASE 1                                  #
# #                                                                    #
# #      We modify the original scene to do the first step of MOR :    #
# #   we add animation to each actuators we want for our model         #
# #   add a writeState componant to save the shaking resulting states  #
# #                                                                    #
# ######################################################################
# reduceMyModel.phase1()


# ####################    PYTHON SCRIPT       ##########################
# #                                                                    #
# #                           PHASE 2                                  #
# #                                                                    #
# #      With the previous result we combine all the generated         #
# #       state files into one to be able to extract from it           #
# #                       the different mode                           #
# #                                                                    #
# ######################################################################
# reduceMyModel.phase2()


# ####################    SOFA LAUNCHER       ##########################
# #                                                                    #
# #                           PHASE 3                                  #
# #                                                                    #
# #      We launch again a set of sofa scene with the sofa launcher    #
# #      with the same previous arguments but with a different scene   #
# #      This scene take the previous one and add the model order      #
# #      reduction component:                                          #
# #            - HyperReducedFEMForceField                             #
# #            - MappedMatrixForceFieldAndMass                         #
# #            - ModelOrderReductionMapping                            #
# #       and produce an Hyper Reduced description of the model        #
# #                                                                    #
# ######################################################################
# reduceMyModel.phase3()


# ####################    PYTHON SCRIPT       ##########################
# #                                                                    #
# #                           PHASE 4                                  #
# #                                                                    #
# #      Final step : we gather again all the results of the           #
# #      previous scenes into one and then compute the RID and Weigts  #
# #      with it. Additionnally we also compute the Active Nodes       #
# #                                                                    #
# ######################################################################
# reduceMyModel.phase4()