# -*- coding: utf-8 -*-
import sys
import numpy as np

#   STLIB IMPORT
from splib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.utility import sceneCreation as u
from mor.wrapper import MORreplace

# Our Phase1 Scene IMPORT
import phase1_snapshots

# Scene parameters
phase = []
#for $item in $PHASE
phase.append($item)
#end for
nbrOfModes = $NBROFMODES
periodSaveGIE = $PERIODSAVEGIE
nbTrainingSet = $NBTRAININGSET
paramWrapper = $PARAMWRAPPER

for item in paramWrapper:
    path, param = item
    param['nbrOfModes'] = $NBROFMODES

###############################################################################

def createScene(rootNode):

    # Import Original Scene with the animation added
    # Here we use a wrapper (MORWrapper) that will allow us (with MORreplace)
    # to modify the initial scene and get informations on its structures
    # For more details on the process involved additionnal doc are with :
    #       - mor.wrapper.MORWrapper
    #       - mor.script.sceneCreationUtility

    phase1_snapshots.createScene(Wrapper(rootNode, MORreplace, paramWrapper))

    # Add MOR plugin if not found
    u.addPlugin(rootNode,"ModelOrderReduction")

    # Save connectivity list that will allow us after work only on the necessary elements

    if phase == [0]*len(phase):
        u.saveElements(rootNode,phase,paramWrapper)


    # Modify the scene to perform hyper-reduction according
    # to the informations collected by the wrapper

    u.modifyGraphScene(rootNode,nbrOfModes,paramWrapper)