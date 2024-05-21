# -*- coding: utf-8 -*-
'''
    From this file you can launch the reduction of the different examples
    present inside the plugin:
        - diamond
        - multiGait
        - finger
        - hexaBeam
        - liver
        - caduceus
        - sofiaLeg

    You will find here presets parameters and it can serve you has a little tutorial
    by launching the different examples by yourself to understand the reduction process.

    To do that comment/uncomment the different phases to perform them in succession or 
    if your sure of your process you can uncomment reduceMyModel.performReduction and do 
    them all in one go.

    You can then add your new reduction parameters for your particular case in the same manner.


    TO USE:
        execute it via a terminal
'''

#######################################################################
####################       IMPORT           ###########################
import os
import sys
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../python') # TO CHANGE

useGui = True

# MOR IMPORT
if useGui:
    from mor.gui import utility

from mor.reduction import ReduceModel
from mor.reduction.container import ObjToAnimate

#######################################################################
####################       PARAMETERS       ###########################

# Select Output Dir and original scene name & path
if useGui:
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    originalScene = utility.openFileName('Select the SOFA scene you want to reduce')
    outputDir = utility.openDirName('Select the directory that will contain all the results')
else:
    originalScene = None # replace with absolute path to your python SOFA scene
    outputDir = None # replace with path to folder where results will be exported

phasesToExecute = None

### DIAMOND ROBOT PARAM
# nodeToReduce = '/modelNode'
# # north = ObjToAnimate("modelNode/north", incr=5,incrPeriod=10,rangeOfAction=40)
# # south = ObjToAnimate("modelNode/south", incr=5,incrPeriod=10,rangeOfAction=40)
# # east = ObjToAnimate("modelNode/east", incr=5,incrPeriod=10,rangeOfAction=40)
# # west = ObjToAnimate("modelNode/west", incr=5,incrPeriod=10,rangeOfAction=40)
# north = ObjToAnimate("modelNode/north", incr=5,incrPeriod=10,rangeOfAction=10)
# south = ObjToAnimate("modelNode/south", incr=5,incrPeriod=10,rangeOfAction=10)
# east = ObjToAnimate("modelNode/east", incr=5,incrPeriod=10,rangeOfAction=10)
# west = ObjToAnimate("modelNode/west", incr=5,incrPeriod=10,rangeOfAction=10)
# listObjToAnimate = [north,west,south,east]
# addRigidBodyModes = [0,0,0]

## FINGER PARAM
# nodeToReduce = '/finger'
# cable = ObjToAnimate("finger/cable/cable", incr=5,incrPeriod=10,rangeOfAction=40)
# listObjToAnimate = [cable]
# addRigidBodyModes = [0,0,0]

### MULTIGAIT ROBOT PARAM
# nodeToReduce ='/model'
# centerCavity = ObjToAnimate("model/centerCavity", incr=350,incrPeriod=2,rangeOfAction=3500)
# rearLeftCavity = ObjToAnimate("model/rearLeftCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# rearRightCavity = ObjToAnimate("model/rearRightCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# frontLeftCavity = ObjToAnimate("model/frontLeftCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# frontRightCavity = ObjToAnimate("model/frontRightCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# listObjToAnimate = [centerCavity,rearLeftCavity,rearRightCavity,frontLeftCavity,frontRightCavity]
# addRigidBodyModes = [1,1,1]

### SOFIA
# nodeToReduce ='/SofiaLeg'
# actuator = ObjToAnimate("SofiaLeg_actuator/actuatorState","doingCircle",incr=0.05,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.7)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]

### LIVER
# nodeToReduce ='/liver'
# actuator = ObjToAnimate("actuator/actuatorState","doingCircle",incr=0.4,incrPeriod=2.5,rangeOfAction=6.2,dataToWorkOn="position",angle=0,rodRadius=0.4)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]

### HEXABEAM
#nodeToReduce ='/M1'
#actuator = ObjToAnimate("M1/cableNodeTip", incr=1,incrPeriod=5,rangeOfAction=5)
#actuator2 = ObjToAnimate("M1/cableNodeSide", incr=1,incrPeriod=5,rangeOfAction=5)
#listObjToAnimate = [actuator, actuator2]
#addRigidBodyModes = [0,0,0]

## SNAKE
# nodeToReduce ='/Snake'
# actuator = ObjToAnimate("Snake/MechanicalObject","doingNothing",incr=1,incrPeriod=1,rangeOfAction=50)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]
# phasesToExecute = [0]


# Tolerance
tolModes = 0.001
tolGIE =  0.05

# Optional
verbose = True
nbrCPU = 4

packageName = 'test'
addToLib = False

#######################################################################
####################      INITIALIZATION     ##########################
reduceMyModel = ReduceModel(    originalScene,  
                                nodeToReduce,
                                listObjToAnimate,
                                tolModes,tolGIE,
                                outputDir,
                                packageName = packageName,
                                addToLib = addToLib,
                                verbose = verbose,
                                addRigidBodyModes = addRigidBodyModes)


#######################################################################
####################       EXECUTION        ###########################
### TO PERFORM THE REDUCTION ALL AT ONCE:
# reduceMyModel.performReduction(phasesToExecute=phasesToExecute)

### TO PERFORM THE REDUCTION STEP BY STEP:
####################    SOFA LAUNCHER       ##########################
#                                                                    #
#            PHASE 1 : Snapshot Database Computation                 #
#                                                                    #
#      We modify the original scene to do the first step of MOR :    #
#   we add animation to each actuators we want for our model         #
#   add a writeState componant to save the shaking resulting states  #
#                                                                    #
######################################################################
# reduceMyModel.phase1(phasesToExecute=phasesToExecute)


####################    PYTHON SCRIPT       ##########################
#                                                                    #
#  PHASE 2 : Computation of the reduced basis with SVD decomposition #
#                                                                    #
#      With the previous result we combine all the generated         #
#       state files into one to be able to extract from it           #
#                       the different mode                           #
#                                                                    #
######################################################################
# reduceMyModel.phase2()


####################    SOFA LAUNCHER       ##########################
#                                                                    #
#            PHASE 3 : Reduced Snapshot Computation                  #
#     to store projected FEM internal forces  contributions          #
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
# reduceMyModel.phase3(phasesToExecute=phasesToExecute)


####################    PYTHON SCRIPT       ##########################
#                                                                    #
# PHASE 4 :  Computation of the reduced integration domain           #
#                in terms of elements and nodes                      #
#                                                                    #
#      Final step : we gather again all the results of the           #
#      previous scenes into one and then compute the RID and Weigts  #
#      with it. Additionnally we also compute the Active Nodes       #
#                                                                    #
######################################################################
# reduceMyModel.phase4()
