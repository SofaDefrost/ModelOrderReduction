# -*- coding: utf-8 -*-
import sys
import numpy as np

#   STLIB IMPORT
from splib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import MORWrapper
from mor.script.sceneCreationUtility import SceneCreationUtility

# Our Phase1 Scene IMPORT
import phase1_snapshots

# Scene parameters
phase = $PHASE
nbrOfModes = $NBROFMODES
periodSaveGIE = $PERIODSAVEGIE
nbTrainingSet = $NBTRAININGSET
paramWrapper = $PARAMWRAPPER

for item in paramWrapper:
    path, param = item
    param['nbrOfModes'] = $NBROFMODES

# We create our SceneCreationUtility that will ease our scene transformation
u = SceneCreationUtility()

###############################################################################

def createScene(rootNode):

    # Import Original Scene with the animation added
    # Here we use a wrapper (MORWrapper) that will allow us (with MORreplace)
    # to modify the initial scene and get informations on its structures
    # For more details on the process involved additionnal doc are with :
    #       - mor.wrapper.MORWrapper
    #       - mor.script.sceneCreationUtility

    phase1_snapshots.createScene(Wrapper(rootNode, u.MORreplace, paramWrapper))

    # Save connectivity list that will allow us after work only on the necessary elements

    if phase == [0]*len(phase):
        u.saveElements(rootNode,phase,paramWrapper)


    # Modify the scene to perform hyper-reduction according
    # to the informations collected by the wrapper

    u.modifyGraphScene(rootNode,nbrOfModes,paramWrapper)