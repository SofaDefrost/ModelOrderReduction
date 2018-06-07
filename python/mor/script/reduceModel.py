# -*- coding: utf-8 -*-
"""
Set of class simplifying and allowing to perform ModelReduction 
"""
import time
import os
import sys 
import math
from launcher import *
import errno
import fileinput
import datetime

# MOR IMPORT
from morUtilityFunctions import readStateFilesAndComputeModes, readGieFileAndComputeRIDandWeights, convertRIDinActiveNodes

path = os.path.dirname(os.path.abspath(__file__))+'/template/'
pathToReducedModel = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])+'/reducedModel/'
print('pathToReducedModel : '+pathToReducedModel)

class ObjToAnimate():
    '''
    ObjToAnimate is a class allowing us to store in 1 object all the information about a specific animation

    **Args**
        
    +----------+-----------+---------------------------------------------------------------------------------------+
    | argument | type      | definition                                                                            |
    +==========+===========+=======================================================================================+
    | location | Str       | Name of the Sofa Node where our obj to animate is                                     |
    +----------+-----------+---------------------------------------------------------------------------------------+
    | animFct  | Str       || Name of our function we want to use to animate.                                      |
    |          |           || During execution of the Sofa Scene, it will import the module                        |
    |          |           || mor.animation in which your animation function has to be located in order to be used |
    +----------+-----------+---------------------------------------------------------------------------------------+
    | objName  | Str       | Name of our Sofa obj                                                                  |
    +----------+-----------+---------------------------------------------------------------------------------------+
    | node     | Sofa.Node | pointer to Sofa node in which we are working on (will be set during execution)        |
    +----------+-----------+---------------------------------------------------------------------------------------+
    | obj      | Sofa.Obj  | pointer to Sofa obj working on (will be set during execution)                         |
    +----------+-----------+---------------------------------------------------------------------------------------+
    | duration | sc        || Total time in second of the animation (put by default to -1                          |
    |          |           || & will be calculated & set later in the execution)                                   |
    +----------+-----------+---------------------------------------------------------------------------------------+
    | **params | undefined || You can put in addation whatever parameters you will need                            |
    |          |           || for your specific animation function                                                 |
    +----------+-----------+---------------------------------------------------------------------------------------+

    Example :

        ObjToAnimate("nord","defaultShaking", incr=5,incrPeriod=10,rangeOfAction=40)

    '''

    def __init__(self,location, animFct=None, objName=None, node=None, obj=None, duration=-1, **params):
        self.location = location
        if animFct == None:
            self.animFct = 'animation.defaultShaking'
        elif isinstance(animFct, str):
            self.animFct = 'animation.shakingAnimations.'+animFct
        else:
            self.animFct = animFct
        self.objName =objName
        self.node = node
        self.obj = obj
        self.duration = duration
        self.params = params # name, dataToWorkOn, incr, incrPeriod, rangeOfAction ...

class ReductionAnimations():
    """
    TODO
    """
    def __init__(self,listObjToAnimate):

        # A list of what you want to animate in your scene and with which parameters
        self.listObjToAnimate = listObjToAnimate

        self.nbActuator = len(self.listObjToAnimate)
        self.nbPossibility = 2**self.nbActuator


        self.nbIterations = 0
        self.setNbIteration()

        self.phaseNumClass = None
        self.generateListOfPhase(self.nbPossibility,self.nbActuator)

    def setNbIteration(self,nbIterations=None):

        if nbIterations :
            self.nbIterations = int(math.ceil(nbIterations))
        else :
            for obj in self.listObjToAnimate:
                tmp = 0
                if all (k in obj.params for k in ("incr","incrPeriod")):
                    tmp = ((obj.params['rangeOfAction']/obj.params['incr'])-1)*obj.params['incrPeriod'] + obj.params['incrPeriod']
                if tmp > self.nbIterations:
                    self.nbIterations = int(math.ceil(tmp))

    def generateListOfPhase(self,nbPossibility,nbActuator):

        phaseNum = [[0] * nbActuator for i in range(nbPossibility)]
        phaseNumClass = []
        for i in range(nbPossibility):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                phaseNum[i][j + nbActuator-len(binVal)] = int(binVal[j])

        for nb in range(nbActuator+1):
            for i in range(nbPossibility):
                if sum(phaseNum[i]) == nb:
                    phaseNumClass.append(phaseNum[i])

        self.phaseNumClass = phaseNumClass

class PackageBuilder():
    """
    TODO
    """
    def __init__(self,outputDir,meshDir,toKeep,packageName = None ,addToLib = False):

        self.outputDir = outputDir
        self.meshDir = meshDir+'/'

        self.toKeep = toKeep
        self.addToLibBool = addToLib

        if packageName :
            self.packageName = 'reduced_'+packageName

            if os.path.isdir(pathToReducedModel+self.packageName) and addToLib:
                raise Exception('A Package named %s already exist in the MOR lib !\nPlease choose another name for this new package' % packageName)

        self.dataDir = self.outputDir+'/data/'
        self.debugDir = self.outputDir+'/debug/'

    def copy(self, src, dest):

        try:
            shutil.copytree(src, dest)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                print('Directory not copied. Error: %s' % e)

    def checkExistance(self,dir):

        if not os.path.exists(os.path.dirname(dir)):
            try:
                os.makedirs(os.path.dirname(dir))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def checkNodeNbr(self,modeFileName):

        nbrOfModes = -1 
        try:

            with open(self.dataDir+modeFileName, "r") as myFile:
                lineSplit = myFile.readline().strip().split();
                nbrOfModes = lineSplit[1]

        except IOError:
            print("IOError : there is no "+self.dataDir+modeFileName)

        except:
            raise

        return int(nbrOfModes)

    def cleanStateFile(self,periodSaveGIE,stateFileName):

        counter = 1
        for line in fileinput.input(self.debugDir+stateFileName, inplace=True):
            if line.find('T=') != -1:
                line = 'T= '+str(periodSaveGIE*counter)+'\n'
                print("%s" % line),
                counter += 1
            else : print(line),

    def copyFileIntoAnother(self,fileToCopy,fileToPasteInto):

        try:

            with open(fileToPasteInto, "a") as myFile:
                currentFile = open(fileToCopy, "r")
                myFile.write(currentFile.read())
                currentFile.close()

        except IOError:
            print("IOError : there is no "+fileToCopy+" , check the template log to find why.\nHere some clue for its probable origin :"\
                            +"    - Your animation arguments are incorrect and it hasn't find anything to animate")

        except:
            raise

    def copyAndCleanState(self,results,periodSaveGIE,stateFileName,gie=None):

        self.checkExistance(self.debugDir)

        for res in results:
            self.copyFileIntoAnother(res["directory"]+"/stateFile.state",self.debugDir+stateFileName)

            if gie:
                for fileName in gie :
                    self.copyFileIntoAnother(res["directory"]+'/'+fileName,self.debugDir+fileName)


        self.cleanStateFile(periodSaveGIE,stateFileName)

    def finalizePackage(self,result):

        shutil.move(result['directory']+'/'+self.packageName+'.py', self.outputDir)

        self.copy(self.meshDir, self.outputDir+'/mesh/')

        if self.addToLibBool :

            self.addToLib()

    def addToLib(self):

        self.copy(self.outputDir, pathToReducedModel+self.packageName+'/')

        try:
            with open(path+'myInit.txt', "r") as myfile:
                myInit = myfile.read()

                myInit = myInit.replace('MyReducedModel',self.packageName[0].upper()+self.packageName[1:])
                myInit = myInit.replace('myReducedModel',self.packageName)

                with open(pathToReducedModel+self.packageName+'/__init__.py', "a") as logFile:
                    logFile.write(myInit)

                # print(myInit)

            for line in fileinput.input(pathToReducedModel+'__init__.py', inplace=True):
                if line.find('__all__') != -1:
                    if line.find('[]') != -1:
                        line = line[:-2]+"'"+self.packageName+"']"'\n'

                    else:
                        line = line[:-2]+",'"+self.packageName+"']"'\n'
                    print("%s" % line),

                else : print(line),

        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

class ReductionParam():
    """
    TODO
    """
    def __init__(self,tolModes,tolGIE,addRigidBodyModes,dataDir):

        self.tolModes = tolModes
        self.tolGIE = tolGIE

        self.addRigidBodyModes = addRigidBodyModes
        self.dataDir = dataDir
        self.dataFolder = '/'+dataDir.split('/')[-2]+'/'

        self.stateFileName = "stateFile.state"
        self.modesFileName = "modes.txt"

        self.gieFilesNames = []
        self.RIDFilesNames = []
        self.weightsFilesNames = [] 
        self.savedElementsFilesNames = []
        self.connectivityFilesNames = []

        self.nbrOfModes = -1
        self.periodSaveGIE = 3 #10
        self.nbTrainingSet = -1

        self.paramWrapper = []

    def setNbTrainingSet(self,rangeOfAction,incr,nbPossibility):

        self.nbTrainingSet = (rangeOfAction/incr) * nbPossibility

    def addParamWrapper(self ,nodeToReduce ,prepareECSW = True ,subTopo = None ,paramForcefield = None ,paramMappedMatrixMapping = None ,paramMORMapping = None):

        nodeName = nodeToReduce.split('/')[-1]

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
                    'template': 'Vec1d,Vec1d',
                    'object1': '@./MechanicalObject',
                    'object2': '@./MechanicalObject',
                    'performECSW': False}
                }

        defaultParamPerform = {
                'paramForcefield' : {
                    'performECSW': True,
                    'modesPath': self.dataFolder+self.modesFileName,
                    'RIDPath': self.dataFolder+'RID_'+nodeName+'.txt',
                    'weightsPath': self.dataFolder+'weight_'+nodeName+'.txt'},

                'paramMORMapping' : {
                    'input': '@../MechanicalObject',
                    'modesPath': self.dataFolder+self.modesFileName},

                'paramMappedMatrixMapping' : {
                    'template': 'Vec1d,Vec1d',
                    'object1': '@./MechanicalObject',
                    'object2': '@./MechanicalObject',
                    'listActiveNodesPath' : self.dataFolder+'conectivity_'+nodeName+'.txt',
                    'performECSW': True}
                }

        if subTopo:
            subTopoName = subTopo.split('/')[-1]
            paramsubTopo = {
                'paramForcefield' : {
                    'performECSW': True,
                    'modesPath': self.dataFolder+self.modesFileName,
                    'RIDPath': self.dataFolder+'RID_'+subTopoName+'.txt',
                    'weightsPath': self.dataFolder+'weight_'+subTopoName+'.txt'}
            }

        if paramForcefield and paramMappedMatrixMapping and paramMORMapping :
            print('plop')
        else:
            if prepareECSW:
                if subTopo:
                    self.paramWrapper.append(   (nodeToReduce ,
                                           {'subTopo' : subTopoName,
                                            'paramForcefield': defaultParamPrepare['paramForcefield'].copy(),
                                            'paramMORMapping': defaultParamPrepare['paramMORMapping'].copy(),
                                            'paramMappedMatrixMapping': defaultParamPrepare['paramMappedMatrixMapping'].copy()} ) )

                    self.paramWrapper.append(  (subTopo ,{'paramForcefield': defaultParamPrepare['paramForcefield'].copy()} ) )
                else:
                    self.paramWrapper.append(   (nodeToReduce ,
                                           {'paramForcefield': defaultParamPrepare['paramForcefield'].copy(),
                                            'paramMORMapping': defaultParamPrepare['paramMORMapping'].copy(),
                                            'paramMappedMatrixMapping': defaultParamPrepare['paramMappedMatrixMapping'].copy()} ) )

            else :
                if subTopo:
                    self.paramWrapper.append(   (nodeToReduce ,
                                           {'subTopo' : subTopoName,
                                            'paramForcefield': defaultParamPerform['paramForcefield'].copy(),
                                            'paramMORMapping': defaultParamPerform['paramMORMapping'].copy(),
                                            'paramMappedMatrixMapping': defaultParamPerform['paramMappedMatrixMapping'].copy()} ) )

                    self.paramWrapper.append(  (subTopo ,{'paramForcefield': paramsubTopo['paramForcefield'].copy()} ) )
                else:
                    self.paramWrapper.append(   (nodeToReduce ,
                                           {'paramForcefield': defaultParamPerform['paramForcefield'].copy(),
                                            'paramMORMapping': defaultParamPerform['paramMORMapping'].copy(),
                                            'paramMappedMatrixMapping': defaultParamPerform['paramMappedMatrixMapping'].copy()} ) )


        return self.paramWrapper

    def setFilesName(self):

        for path , param in self.paramWrapper :
            nodeName = path.split('/')[-1]
            self.gieFilesNames.append('HyperReducedFEMForceField_'+nodeName+'_Gie.txt')
            self.RIDFilesNames.append('RID_'+nodeName+'.txt')
            self.weightsFilesNames.append('weight_'+nodeName+'.txt')
            self.savedElementsFilesNames.append('elmts_'+nodeName+'.txt')
            self.connectivityFilesNames.append('conectivity_'+nodeName+'.txt')

class ReduceModel():
    """
    TODO
    """
    def __init__(self,
                 originalScene,
                 nodesToReduce,
                 listObjToAnimate,
                 tolModes,
                 tolGIE,
                 outputDir,
                 meshDir,
                 packageName = None,
                 toKeep = None,
                 addToLib = False,
                 verbose = False,
                 addRigidBodyModes = False,
                 nbrCPU = 4):

        self.originalScene = originalScene
        self.nodesToReducePath = nodesToReduce


        ### Obj Containing all the argument & function about how the shaking will be done and with which actuators
        self.reductionAnimations = ReductionAnimations(listObjToAnimate)

        ### If nothing is indicated to keep in the future package, by default we add all the actuators used to create the reduced model
        if not toKeep:
            toKeep = []
            for obj in listObjToAnimate:
                toKeep.append(obj.location)

        ### Obj Containing all the argument & function about how to create the end package and where 
        self.packageBuilder = PackageBuilder(outputDir,meshDir,toKeep,packageName,addToLib)

        ### Obj Containing all the argument & function about the actual reduction
        self.reductionParam = ReductionParam(tolModes,tolGIE,addRigidBodyModes,self.packageBuilder.dataDir)

        ### With the previous parameters (listObjToAnimate/nbPossibility) we can set our training set number
        self.reductionParam.setNbTrainingSet(   listObjToAnimate[0].params['rangeOfAction'],
                                                listObjToAnimate[0].params['incr'],
                                                self.reductionAnimations.nbPossibility)


        self.nodeToReduceNames = []
        self.subTopoList = []
        for nodePath in self.nodesToReducePath :
            if isinstance(nodePath,tuple):
                nodeName = nodePath[0].split('/')[-1]
                modelSubTopoName = nodePath[1].split('/')[-1]
                self.nodeToReduceNames.append((nodeName,modelSubTopoName))
                self.subTopoList.append(self.nodesToReducePath.index(nodePath))
                self.reductionParam.addParamWrapper(nodePath[0], subTopo = nodePath[1])

            else :
                nodeName = nodePath.split('/')[-1]
                self.nodeToReduceNames.append(nodeName)

                self.reductionParam.addParamWrapper(nodePath)

        self.reductionParam.setFilesName()


        self.nbrCPU = nbrCPU
        self.verbose = verbose

        self.activesNodesLists = []
        self.listSofaScene = []

        strInfo = 'periodSaveGIE : '+str(self.reductionParam.periodSaveGIE)+' | '
        strInfo += 'nbTrainingSet : '+str(self.reductionParam.nbTrainingSet)+' | '
        strInfo += 'nbIterations : '+str(self.reductionAnimations.nbIterations)+'\n'
        strInfo += "List of phase :"+str(self.reductionAnimations.phaseNumClass)+'\n'
        strInfo += "##################################################"
        print(strInfo)

    def setListSofaScene(self,phasesToExecute=None):

        self.listSofaScene = []

        if not phasesToExecute:
            phasesToExecute = list(range(self.reductionAnimations.nbPossibility))

        for i in phasesToExecute:
            if i >= self.reductionAnimations.nbPossibility or i < 0 :
                raise ValueError("phasesToExecute incorrect, select an non-existent phase : "+phasesToExecute)
            self.listSofaScene.append({ "ORIGINALSCENE": self.originalScene,
                                        "LISTOBJTOANIMATE": self.reductionAnimations.listObjToAnimate,
                                        "PHASE": self.reductionAnimations.phaseNumClass[i],
                                        "PERIODSAVEGIE" : self.reductionParam.periodSaveGIE,
                                        "PARAMWRAPPER" : self.reductionParam.paramWrapper,
                                        "nbIterations":self.reductionAnimations.nbIterations})

    def performReduction(self,phasesToExecute=None,nbrOfModes=None):

        ### This initila time we allow us to give at the end the total time execution
        init_time = time.time()

        self.phase1(phasesToExecute)
        self.phase2()
        self.phase3(phasesToExecute,nbrOfModes)
        self.phase4(nbrOfModes)

        tps = int(round(time.time() - init_time))
        print("TOTAL TIME --- %s ---" % (datetime.timedelta(seconds=tps) ) )

    def phase1(self,phasesToExecute=None):
        ####################    SOFA LAUNCHER       ##########################
        #                                                                    #
        #                           PHASE 1                                  #
        #                                                                    #
        #      We modify the original scene to do the first step of MOR :    #
        #   we add animation to each actuators we want for our model         #
        #   add a writeState componant to save the shaking resulting states  #
        #                                                                    #
        ######################################################################
        start_time = time.time()

        if not phasesToExecute:
            phasesToExecute = list(range(self.reductionAnimations.nbPossibility))

        self.setListSofaScene(phasesToExecute)

        filenames = ["phase1_snapshots.py","debug_scene.py"]
        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(path+filename).read(), filename) )


        results = startSofa(self.listSofaScene, filesandtemplates, launcher=ParallelLauncher(self.nbrCPU))

        if self.verbose:
            for res in results:
                print("Results: ")
                print("    directory: "+res["directory"])
                print("        scene: "+res["scene"])
                print("     duration: "+str(res["duration"])+" sec")  

        self.packageBuilder.copyAndCleanState(results,self.reductionParam.periodSaveGIE,self.reductionParam.stateFileName)
        self.packageBuilder.copy(results[0]["directory"]+"/debug_scene.py", self.packageBuilder.debugDir)

        print("PHASE 1 --- %s seconds ---" % (time.time() - start_time))

    def phase2(self):
        ####################    PYTHON SCRIPT       ##########################
        #                                                                    #
        #                           PHASE 2                                  #
        #                                                                    #
        #      With the previous result we combine all the generated         #
        #       state files into one to be able to extract from it           #
        #                       the different mode                           #
        #                                                                    #
        ######################################################################
        start_time = time.time()

        self.packageBuilder.checkExistance(self.packageBuilder.dataDir)
 
        self.reductionParam.nbrOfModes = readStateFilesAndComputeModes(stateFilePath = self.packageBuilder.debugDir+self.reductionParam.stateFileName,
                                                        modesFileName = self.packageBuilder.dataDir+self.reductionParam.modesFileName,
                                                        tol = self.reductionParam.tolModes,
                                                        addRigidBodyModes = self.reductionParam.addRigidBodyModes,
                                                        verbose= self.verbose)

        if self.reductionParam.nbrOfModes == -1:
            raise ValueError("problem of execution of readStateFilesAndComputeModes")

        print("PHASE 2 --- %s seconds ---" % (time.time() - start_time))

    def phase3(self,phasesToExecute=None,nbrOfModes=None):
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
        start_time = time.time()

        if not phasesToExecute:
            phasesToExecute = list(range(self.reductionAnimations.nbPossibility))
        if not nbrOfModes:
            nbrOfModes = self.reductionParam.nbrOfModes

        if not os.path.isfile(self.packageBuilder.dataDir+self.reductionParam.modesFileName):
            raise IOError("There is no mode file at "+self.packageBuilder.dataDir+self.reductionParam.modesFileName\
                +"\nPlease give one at this location or indicate the correct location or re-generate one with phase 1 & 2")

        nbrOfModesPossible = self.packageBuilder.checkNodeNbr(self.reductionParam.modesFileName)

        if not nbrOfModes:
            nbrOfModes = self.reductionParam.nbrOfModes
        if nbrOfModes == -1 :
            nbrOfModes = self.reductionParam.nbrOfModes = nbrOfModesPossible

        if (nbrOfModes <= 0) or (nbrOfModes > nbrOfModesPossible):
            raise ValueError("nbrOfModes incorrect\n"\
                +"  nbrOfModes given :"+str(nbrOfModes)+" | nbrOfModes max possible : "+str(nbrOfModesPossible))

        self.setListSofaScene(phasesToExecute)

        for i in range(len(phasesToExecute)):
            self.listSofaScene[i]['NBROFMODES'] = nbrOfModes
            self.listSofaScene[i]['NBTRAININGSET'] = self.reductionParam.nbTrainingSet
            # self.listSofaScene[i]["PARAMWRAPPER"] = self.paramWrapper

        filenames = ["phase2_prepareECSW.py","phase1_snapshots.py"]
        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(path+filename).read(), filename) )
             
        results = startSofa(self.listSofaScene, filesandtemplates, launcher=ParallelLauncher(self.nbrCPU))

        if self.verbose:
            for res in results:
                print("Results: ")
                print("    directory: "+res["directory"])
                print("        scene: "+res["scene"])
                print("     duration: "+str(res["duration"])+" sec")

        for fileName in self.reductionParam.savedElementsFilesNames :
            self.packageBuilder.copyFileIntoAnother(results[0]["directory"]+'/'+fileName,self.packageBuilder.debugDir+fileName)


        self.packageBuilder.copyAndCleanState(  results,self.reductionParam.periodSaveGIE,
                                                'step2_'+self.reductionParam.stateFileName,
                                                gie=self.reductionParam.gieFilesNames)


        print("PHASE 3 --- %s seconds ---" % (time.time() - start_time))

    def phase4(self,nbrOfModes=None):
        ####################    PYTHON SCRIPT       ##########################
        #                                                                    #
        #                           PHASE 4                                  #
        #                                                                    #
        #      Final step : we gather again all the results of the           #
        #      previous scenes into one and then compute the RID and Weigts  #
        #      with it. Additionnally we also compute the Active Nodes       #
        #                                                                    #
        ######################################################################
        start_time = time.time()

        if not os.path.isfile(self.packageBuilder.dataDir+self.reductionParam.modesFileName):
            raise IOError("There is no mode file at "+self.packageBuilder.dataDir+self.reductionParam.modesFileName\
                +"\nPlease give one at this location or indicate the correct location or re-generate one with phase 1 & 2")

        nbrOfModesPossible = self.packageBuilder.checkNodeNbr(self.reductionParam.modesFileName)

        if not nbrOfModes:
            nbrOfModes = self.reductionParam.nbrOfModes
        if nbrOfModes == -1 :
            nbrOfModes = self.reductionParam.nbrOfModes = nbrOfModesPossible

        if (nbrOfModes <= 0) or (nbrOfModes > nbrOfModesPossible):
            raise ValueError("nbrOfModes incorrect\n"\
                +"  nbrOfModes given :"+str(nbrOfModes)+" | nbrOfModes max possible : "+str(nbrOfModesPossible))

        for fileName in self.reductionParam.gieFilesNames :
            if not os.path.isfile(self.packageBuilder.debugDir+fileName):
                raise IOError("There is no GIE file at "+self.packageBuilder.debugDir+fileName\
                    +"\nPlease give one at this location or indicate the correct location or re-generate one with phase 3")

            index = self.reductionParam.gieFilesNames.index(fileName)
            readGieFileAndComputeRIDandWeights( self.packageBuilder.debugDir+fileName,
                                                self.packageBuilder.dataDir+self.reductionParam.RIDFilesNames[index],
                                                self.packageBuilder.dataDir+self.reductionParam.weightsFilesNames[index],
                                                self.reductionParam.tolGIE,
                                                verbose= self.verbose)

            self.activesNodesLists.append(  convertRIDinActiveNodes(self.packageBuilder.dataDir+self.reductionParam.RIDFilesNames[index],
                                                                    self.packageBuilder.debugDir+self.reductionParam.savedElementsFilesNames[index],
                                                                    self.packageBuilder.dataDir+self.reductionParam.connectivityFilesNames[index],
                                                                    verbose= self.verbose))


        if self.subTopoList :
            print('there is at least one subTopo : '+str(self.subTopoList))
            for i in range(len(self.subTopoList)) :
                nodeName1 , nodeName2 = self.nodeToReduceNames[i]
                print ('nodeName1 ', nodeName1)
                print ('nodeName2 ', nodeName2)
                print (self.activesNodesLists[i])
                print ('###################\n\n')
                print (self.activesNodesLists[i+1])
                print ('===================\n\n')
                self.activesNodesLists[i] = list(set().union(self.activesNodesLists[i],self.activesNodesLists[i+1]))
                print (self.activesNodesLists[i])

                with open(self.packageBuilder.dataDir+'conectivity_'+nodeName1+'.txt', "w") as file:
                    for item in self.activesNodesLists[i]:
                      file.write("%i\n" % item)
                file.close()


        filename = "phase3_performECSW.py"
        filesandtemplates = [(open(path+filename).read(), filename)]

        self.reductionParam.paramWrapper = []
        for nodePath in self.nodesToReducePath :
            if isinstance(nodePath,tuple):
                self.reductionParam.addParamWrapper(nodePath[0], subTopo = nodePath[1], prepareECSW = False)
            else :
                self.reductionParam.addParamWrapper(nodePath, prepareECSW = False)

        finalScene = {}
        finalScene["ORIGINALSCENE"] = self.originalScene
        finalScene["PARAMWRAPPER"] = self.reductionParam.paramWrapper
        finalScene['NBROFMODES'] = nbrOfModes
        finalScene["nbIterations"] = 1
        finalScene["TOKEEP"] = self.packageBuilder.toKeep
        finalScene["PACKAGENAME"] = self.packageBuilder.packageName

        results = startSofa([finalScene], filesandtemplates, launcher=ParallelLauncher(1))

        self.packageBuilder.finalizePackage(results[0])

        print("PHASE 4 --- %s seconds ---\n" % (time.time() - start_time))
        print('The reduction is now finished !')
        return self.packageBuilder.outputDir+'/'+self.packageBuilder.packageName+'.py'