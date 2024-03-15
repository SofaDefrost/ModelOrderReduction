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
from mor.gui import utility
from mor.reduction import ReduceModel
from mor.reduction.container import ObjToAnimate

#######################################################################
####################       PARAMETERS       ###########################

# Select Output Dir and original scene name & path
from PyQt5 import QtWidgets
app = QtWidgets.QApplication(sys.argv)

originalScene = utility.openFileName('Select the SOFA scene you want to reduce')
outputDir = utility.openDirName('Select the directory that will contain all the results')

### DIAMOND ROBOT PARAM
# nodeToReduce = '/modelNode'
# nord = ObjToAnimate("modelNode/nord", incr=5,incrPeriod=10,rangeOfAction=40)
# # # sud = ObjToAnimate("modelNode/sud", incr=5,incrPeriod=10,rangeOfAction=40)
# # # est = ObjToAnimate("modelNode/est", incr=5,incrPeriod=10,rangeOfAction=40)
# # # ouest = ObjToAnimate("modelNode/ouest", incr=5,incrPeriod=10,rangeOfAction=40)
# # # listObjToAnimate = [nord,ouest,sud,est]
# listObjToAnimate = [nord]
# addRigidBodyModes = [0,0,0]

## FINGER PARAM
#nodeToReduce = '/finger'
#cable = ObjToAnimate("finger/cable/cable", incr=5,incrPeriod=10,rangeOfAction=40)
#listObjToAnimate = [cable]
#addRigidBodyModes = [0,0,0]

### STARFISH ROBOT PARAM
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
# actuator = ObjToAnimate("SofiaLeg_actuator/actuatorState","shakingSofia",incr=0.05,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.7)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]

# ### LIVER
# nodeToReduce ='/liver'
# actuator = ObjToAnimate("actuator/actuatorState","shakingLiver",incr=0.4,incrPeriod=2.5,rangeOfAction=6.2,dataToWorkOn="position",angle=0,rodRadius=0.4)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]

### HEXABEAM
# nodeToReduce ='/M1'
# actuator = ObjToAnimate("M1/cableNodeTip", incr=1,incrPeriod=5,rangeOfAction=5)
# actuator2 = ObjToAnimate("M1/cableNodeSide", incr=1,incrPeriod=5,rangeOfAction=5)
# listObjToAnimate = [actuator, actuator2]
# addRigidBodyModes = [0,0,0]

# ### MeshRefinement_bench01
nodeToReduce ='/HexaBeams/Beam_01'
actuator = ObjToAnimate("actuator/actuatorState", incr=5,incrPeriod=10,rangeOfAction=40,dataToWorkOn="position")
listObjToAnimate = [actuator]
addRigidBodyModes = [0,0,0]

### SNAKE
# nodeToReduce ='/Snake'
# actuator = ObjToAnimate("actuatorDummy/actuatorState","shakingSofia",incr=0.4,incrPeriod=3,rangeOfAction=6.2,dataToWorkOn="position",angle=0,rodRadius=0.7)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]


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
reduceMyModel.performReduction()

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
# reduceMyModel.phase1()


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
# reduceMyModel.phase3()


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
