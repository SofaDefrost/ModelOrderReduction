# -*- coding: utf-8 -*-
'''
**Class Containing all the parameters related to the reduction**
'''
import platform

slash = '/'
if "Windows" in platform.platform():
    slash ='\\'


class ReductionParam():
    """
    **Contain all the parameters related to the reduction**

    """

    def __init__(self,tolModes,tolGIE,addRigidBodyModes,dataDir):

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
        self.listActiveNodesFilesNames = []
        self.massName = ''


        self.nbrOfModes = -1
        self.periodSaveGIE = 6 #10
        self.nbTrainingSet = -1

        self.paramWrapper = None

    def setNbTrainingSet(self,rangeOfAction,incr):
        '''
        '''

        self.nbTrainingSet = int(rangeOfAction/incr)

    def addParamWrapper(self ,nodeToReduce ,prepareECSW = True, paramForcefield = None ,paramMappedMatrixMapping = None ,paramMORMapping = None):
        '''
        '''
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

                'paramMappedMatrixMapping' : {
                    'nodeToParse': nodeToParse,
                    'template': 'Vec1d,Vec1d',
                    'object1': '@./MechanicalObject',
                    'object2': '@./MechanicalObject',
                    'timeInvariantMapping1': True,
                    'timeInvariantMapping2': True,
                    'performECSW': False}
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

                'paramMappedMatrixMapping' : {
                    'nodeToParse': nodeToParse,
                    'template': 'Vec1d,Vec1d',
                    'object1': '@./MechanicalObject',
                    'object2': '@./MechanicalObject',
                    'timeInvariantMapping1': True,
                    'timeInvariantMapping2': True,
                    'listActiveNodesPath' : self.dataFolder+'listActiveNodes.txt',
                    'performECSW': True,
                    'usePrecomputedMass': True,
                    'precomputedMassPath': self.dataFolder+self.massName}
                }

        if paramForcefield and paramMappedMatrixMapping and paramMORMapping :
            pass
        else:
            if prepareECSW:
                self.paramWrapper = (   (nodeToReduce ,
                                       {'paramForcefield': defaultParamPrepare['paramForcefield'].copy(),
                                        'paramMORMapping': defaultParamPrepare['paramMORMapping'].copy(),
                                        'paramMappedMatrixMapping': defaultParamPrepare['paramMappedMatrixMapping'].copy()} ) )

            else :
                self.paramWrapper = (   (nodeToReduce ,
                                       {'paramForcefield': defaultParamPerform['paramForcefield'].copy(),
                                        'paramMORMapping': defaultParamPerform['paramMORMapping'].copy(),
                                        'paramMappedMatrixMapping': defaultParamPerform['paramMappedMatrixMapping'].copy()} ) )

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
        self.listActiveNodesFilesNames.append('listActiveNodes_'+nodeName+'.txt')