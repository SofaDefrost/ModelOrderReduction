# -*- coding: utf-8 -*-

import platform

slash = '/'
if "Windows" in platform.platform():
    slash ='\\'


class ReductionParam():
    """
    **Contain all the parameters related to the reduction**

    """

    def __init__(self,tolModes,tolGIE,addRigidBodyModes,dataDir,saveVelocitySnapshots):

        self.tolModes = tolModes
        self.tolGIE = tolGIE

        self.addRigidBodyModes = addRigidBodyModes
        self.dataDir = dataDir
        self.dataFolder = slash+dataDir.split(slash)[-2]+slash

        self.stateFileName = "stateFile.state"
        self.modesFileName = "modes.txt"

        self.gieFilesNames = []
        self.RIDFilesNames = []
        self.weightsFilesNames = [] 
        self.savedElementsFilesNames = []

        self.nbrOfModes = -1
        self.periodSaveGIE = 6 #10
        self.nbTrainingSet = -1

        self.paramWrapper = None

        if not saveVelocitySnapshots:
            self.velocityFileName = None
        else:
            self.velocityFileName = "velocityStateFile.state"

    def setNbTrainingSet(self,rangeOfAction,incr):
        '''
        '''

        self.nbTrainingSet = int(rangeOfAction/incr)

    def addParamWrapper(self ,nodeToReduce ,prepareECSW = True, paramForcefield = None ,paramMORMapping = None):
        '''
        '''
        nodeToReduce = "".join(nodeToReduce)
        ndtSplit = nodeToReduce.split(slash)
        nodeToParse = '@./' + ndtSplit[-1]

        defaultParamPrepare = {
                'paramForcefield' : {
                    'prepareECSW' : True,
                    'modesPath': self.dataDir+self.modesFileName,
                    'periodSaveGIE' : self.periodSaveGIE,
                    'nbTrainingSet' : self.nbTrainingSet},

                'paramMORMapping' : {
                    'input': '@../MechanicalObject',
                    'modesPath': self.dataDir+self.modesFileName},
                }

        defaultParamPerform = {
                'paramForcefield' : {
                    'performECSW': True,
                    'modesPath': self.dataFolder+self.modesFileName,
                    'RIDPath': self.dataFolder,
                    'weightsPath': self.dataFolder},

                'paramMORMapping' : {
                    'input': '@../MechanicalObject',
                    'modesPath': self.dataFolder+self.modesFileName},
                }

        if paramForcefield and paramMORMapping :
            pass
        else:
            if prepareECSW:
                self.paramWrapper = (   (nodeToReduce ,
                                       {'paramForcefield': defaultParamPrepare['paramForcefield'].copy(),
                                        'paramMORMapping': defaultParamPrepare['paramMORMapping'].copy()} ) )

            else :
                self.paramWrapper = (   (nodeToReduce ,
                                       {'paramForcefield': defaultParamPerform['paramForcefield'].copy(),
                                        'paramMORMapping': defaultParamPerform['paramMORMapping'].copy()} ) )

        return self.paramWrapper

    def setFilesName(self):
        '''
        '''

        path , param = self.paramWrapper
        nodeName = path.split(slash)[-1]
        self.gieFilesNames.append('HyperReducedFEMForceField_'+nodeName+'_Gie.txt')
        self.RIDFilesNames.append('RID_'+nodeName+'.txt')
        self.weightsFilesNames.append('weight_'+nodeName+'.txt')
        self.savedElementsFilesNames.append('elmts_'+nodeName+'.txt')
