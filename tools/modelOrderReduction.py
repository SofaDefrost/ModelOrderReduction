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
from mor.reduction import ObjToAnimate

#######################################################################
####################       PARAMETERS       ###########################

# Select Output Dir and original scene name & path
from PyQt4 import QtCore, QtGui
app = QtGui.QApplication(sys.argv)

#originalScene = utility.openFileName('Select the SOFA scene you want to reduce')
#meshes = utility.openFilesNames('Select the meshes & visual of your scene')
#outputDir = utility.openDirName('Select the directory tha will contain all the results')

### DIAMOND ROBOT PARAM
#nodesToReduce = ['/modelNode']
#nord = ObjToAnimate("modelNode/nord","defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
#sud = ObjToAnimate("modelNode/sud","defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
#est = ObjToAnimate("modelNode/est","defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
#ouest = ObjToAnimate("modelNode/ouest","defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)
#listObjToAnimate = [nord,ouest,sud,est]
#addRigidBodyModes = [0,0,0]

### STARFISH ROBOT PARAM
# nodesToReduce =[('/model','/model/modelSubTopo')]
# centerCavity = ObjToAnimate("model/centerCavity", incr=350,incrPeriod=2,rangeOfAction=3500)
# rearLeftCavity = ObjToAnimate("model/rearLeftCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# rearRightCavity = ObjToAnimate("model/rearRightCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# frontLeftCavity = ObjToAnimate("model/frontLeftCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# frontRightCavity = ObjToAnimate("model/frontRightCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
# listObjToAnimate = [centerCavity,rearLeftCavity,rearRightCavity,frontLeftCavity,frontRightCavity]
# addRigidBodyModes = [1,1,1]

### SOFIA
# nodesToReduce =['/SofiaLeg']
# actuator = ObjToAnimate("SofiaLeg_actuator/actuatorState","shakingSofia",incr=0.05,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.7)
# # actuator = ObjToAnimate("SofiaLeg_actuator","shakingSofia",'MechanicalObject',incr=0.05,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.7)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]

### LIVER
#nodesToReduce =['/liver']
#actuator = ObjToAnimate("actuator/actuatorState","shakingSofia",incr=0.4,incrPeriod=3,rangeOfAction=6.2,dataToWorkOn="position",angle=0,rodRadius=0.7)
#listObjToAnimate = [actuator]
#addRigidBodyModes = [0,0,0]



####################### TO TEST #######################

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


### PNEUNETS PARAM
# nodesToReduce =['/model']
# cavity = ObjToAnimate("cavity", incr=1000,incrPeriod=2000,rangeOfAction=25000)
# listObjToAnimate = [cavity]
# addRigidBodyModes = [0,0,0]

### LIVER
# nodesToReduce =['/liver']
# actuator = ObjToAnimate("actuator","shakingSofia",'MechanicalObject',incr=0.20,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.4)
# # # actuator = ObjToAnimate("SofiaLeg_actuator","shakingSofia",'MechanicalObject',incr=0.05,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.7)
# listObjToAnimate = [actuator]
# addRigidBodyModes = [0,0,0]

### ARM3D
# nodesToReduce = ['/node']
# cav_S0_topright = ObjToAnimate("node/controlledPoints/cav_S0_topright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S0_topleft = ObjToAnimate("node/controlledPoints/cav_S0_topleft", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S0_bottomright = ObjToAnimate("node/controlledPoints/cav_S0_bottomright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S0_bottomleft = ObjToAnimate("node/controlledPoints/cav_S0_bottomleft", incr=1,incrPeriod=2,rangeOfAction=6)

# cav_S1_topright = ObjToAnimate("node/controlledPoints/cav_S1_topright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S1_topleft = ObjToAnimate("node/controlledPoints/cav_S1_topleft", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S1_bottomright = ObjToAnimate("node/controlledPoints/cav_S1_bottomright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S1_bottomleft = ObjToAnimate("node/controlledPoints/cav_S1_bottomleft", incr=1,incrPeriod=2,rangeOfAction=6)

# cav_S2_topright = ObjToAnimate("node/controlledPoints/cav_S2_topright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S2_topleft = ObjToAnimate("node/controlledPoints/cav_S2_topleft", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S2_bottomright = ObjToAnimate("node/controlledPoints/cav_S2_bottomright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S2_bottomleft = ObjToAnimate("node/controlledPoints/cav_S2_bottomleft", incr=1,incrPeriod=2,rangeOfAction=6)

# cav_S3_topright = ObjToAnimate("node/controlledPoints/cav_S3_topright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S3_topleft = ObjToAnimate("node/controlledPoints/cav_S3_topleft", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S3_bottomright = ObjToAnimate("node/controlledPoints/cav_S3_bottomright", incr=1,incrPeriod=2,rangeOfAction=6)
# cav_S3_bottomleft = ObjToAnimate("node/controlledPoints/cav_S3_bottomleft", incr=1,incrPeriod=2,rangeOfAction=6)

# listObjToAnimate = [
#                     cav_S0_topright,cav_S0_topleft,cav_S0_bottomright,cav_S0_bottomleft,
#                     cav_S1_topright,cav_S1_topleft,cav_S1_bottomright,cav_S1_bottomleft,
#                     cav_S2_topright,cav_S2_topleft,cav_S2_bottomright,cav_S2_bottomleft,
#                     cav_S3_topright,cav_S3_topleft,cav_S3_bottomright,cav_S3_bottomleft
#                     ]
# addRigidBodyModes = [0,0,0]

####################################################


# Tolerance
tolModes = 0.001
tolGIE =  0.05

# Optionnal
verbose = True
nbrCPU = 4

packageName = 'test'
addToLib = False

#######################################################################
####################      INITIALIZATION     ##########################
reduceMyModel = ReduceModel(    originalScene,  
                                nodesToReduce,
                                listObjToAnimate,
                                tolModes,tolGIE,
                                outputDir,
                                meshes = meshes,
                                packageName = packageName,
                                addToLib = addToLib,
                                verbose = verbose,
                                addRigidBodyModes = addRigidBodyModes)


#######################################################################
####################       EXECUTION        ###########################

# reduceMyModel.performReduction() # phasesToExecute=list(range(8)),nbrOfModes=18)

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
# reduceMyModel.phase3(phasesToExecute=[len(reduceMyModel.reductionAnimations.phaseNumClass)-1])
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