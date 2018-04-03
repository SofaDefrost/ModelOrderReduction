# -*- coding: utf-8 -*-
import time
import os
import sys 
from sys import argv
import math
from launcher import *
import errno
import shutil
import fileinput

# MOR IMPORT
from morUtilityFunctions import readStateFilesAndComputeModes, readGieFileAndComputeRIDandWeights, convertRIDinActiveNodes

path = os.path.dirname(os.path.abspath(__file__))+'/template/'
pathToReducedModel = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])+'/reducedModel/'
# print('pathToReducedModel : '+pathToReducedModel)

class ReduceModel():

    def __init__(self,
                 originalScene,
                 nodesToReduce,
                 animationParam,
                 tolModes,
                 tolGIE,
                 outputDir,
                 meshDir,
                 packageName = None,
                 verbose = False,
                 addRigidBodyModes = False):

        self.init_time = time.time()
        self.originalScene = originalScene

        self.nodesToReduce = nodesToReduce

        if packageName :
            self.packageName = 'reduced_'+packageName

            if os.path.isdir(pathToReducedModel+self.packageName):
                raise Exception('A Package named %s already exist !\nPlease choose another name for this new package' % packageName)

        # A list of what you want to animate in your scene and with which parameters
        self.toAnimate = animationParam['toAnimate']
        self.increment = animationParam['increment']
        self.breathTime = animationParam['breathTime']
        self.maxPull = animationParam['maxPull']
        self.nbActuator = len(self.toAnimate)
        self.addRigidBodyModes = addRigidBodyModes

        # The different Tolerance & Nbr of Nodes
        self.tolModes = tolModes
        self.tolGIE = tolGIE

        self.verbose = verbose
        self.nbrOfModes = -1

        # Where will be all the different results and with which name
        self.meshDir = meshDir+'/'
        self.outputDir = outputDir
        self.dataDir = self.outputDir+'/data/'
        self.debugDir = self.outputDir+'/debug/'

        self.stateFileName = "stateFile.state"
        self.modesFileName = "test_modes.txt"

        self.gieFilesNames = []
        self.RIDFilesNames = []
        self.weightsFilesNames = [] 
        self.savedElementsFilesNames = []
        self.connectivityFilesNames = []

        ####################   SHAKING VARIABLES  ###########################
        self.nbPossibility = 2**self.nbActuator
        self.phaseNum = [[0] * self.nbActuator for i in range(self.nbPossibility)]
        self.phaseNumClass = []


        self.periodSaveGIE = [x+1 for x in self.breathTime]
        self.nbTrainingSet = (self.maxPull[0]/self.increment[0]) * self.nbPossibility

        ####################        OTHER           #########################        
        self.activesNodesLists = []
        ####################  INIT SCENE SEQUENCES  #########################

        defaultParamForcefield = {
            'prepareECSW' : True,
            'modesPath': self.dataDir+self.modesFileName,
            'periodSaveGIE' : self.periodSaveGIE[0],
            'nbTrainingSet' : self.nbTrainingSet}

        defaultParamMappedMatrixMapping = {
            'template': 'Vec1d,Vec1d',
            'object1': '@./MechanicalObject',
            'object2': '@./MechanicalObject',
            'performECSW': False}

        defaultParamMORMapping = {
            'input': '@../MechanicalObject',
            'modesPath': self.dataDir+self.modesFileName}

        self.paramWrapper = []
        self.subTopoList = []
        for item in self.nodesToReduce :
            if isinstance(item,tuple):
                modelSubTopoName = item[1].split('/')[-1]
                self.subTopoList.append(self.nodesToReduce.index(item))
                self.paramWrapper.append(   (item[0] , 
                                       {'subTopo' : modelSubTopoName,
                                        'paramForcefield': defaultParamForcefield.copy(),
                                        'paramMORMapping': defaultParamMORMapping.copy(),
                                        'paramMappedMatrixMapping': defaultParamMappedMatrixMapping.copy()} ) )

                self.paramWrapper.append(  (item[1] ,{'paramForcefield': defaultParamForcefield.copy()} ) )
            else:
                self.paramWrapper.append(   (item , 
                                       {'paramForcefield': defaultParamForcefield.copy(),
                                        'paramMORMapping': defaultParamMORMapping.copy(),
                                        'paramMappedMatrixMapping': defaultParamMappedMatrixMapping.copy()} ) )

        for path , param in self.paramWrapper :
            nodeName = path.split('/')[-1]
            self.gieFilesNames.append('HyperReducedFEMForceField_'+nodeName+'_Gie.txt')
            self.RIDFilesNames.append('RID_'+nodeName+'.txt')
            self.weightsFilesNames.append('weight_'+nodeName+'.txt')
            self.savedElementsFilesNames.append('elmts_'+nodeName+'.txt')
            self.connectivityFilesNames.append('conectivity_'+nodeName+'.txt')

        self.nbIterations = [0]*self.nbActuator
        for i in range(self.nbActuator):
            self.nbIterations[i] = (self.maxPull[i]/self.increment[i])*self.breathTime[i] + (self.maxPull[i]/self.increment[i]) 

        for i in range(self.nbPossibility):
            binVal = "{0:b}".format(i)
            for j in range(len(binVal)):
                self.phaseNum[i][j + self.nbActuator-len(binVal)] = int(binVal[j])

        for nb in range(self.nbActuator+1):
            for i in range(self.nbPossibility):
                if sum(self.phaseNum[i]) == nb:
                    self.phaseNumClass.append(self.phaseNum[i])

        self.listSofaScene = []
        for i in range(self.nbPossibility):
            self.listSofaScene.append({ "ORIGINALSCENE": self.originalScene,
                                        "TOANIMATE": self.toAnimate,
                                        "PHASE": self.phaseNumClass[i],
                                        "INCREMENT" : self.increment,
                                        "MAXPULL" : self.maxPull,
                                        "BREATHTIME" : self.breathTime,
                                        "PERIODSAVEGIE" : self.periodSaveGIE,
                                        "PARAMWRAPPER" : self.paramWrapper,
                                        "nbIterations":self.nbIterations[0]
                })

        strInfo = 'periodSaveGIE : '+str(self.periodSaveGIE[0])+' | '
        strInfo += 'nbTrainingSet : '+str(self.nbTrainingSet)+' | '
        strInfo += 'nbIterations : '+str(self.nbIterations[0])
        print(strInfo)
        print ('listSofaScene : ')
        for key, value in self.listSofaScene[0].items():
            print('- '+key+' : '+str(value))

    def phase1(self):
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

        if self.verbose :
            print ("List of phase :",self.phaseNumClass)
            print ("Number of Iteration per phase :",self.nbIterations[0])
            print ("##############")

        filenames = ["phase1_snapshots.py","debug_scene.py"]
        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(path+filename).read(), filename) )


        results = startSofa(self.listSofaScene, filesandtemplates, launcher=ParallelLauncher(4))

        if self.verbose:
            for res in results:
                print("Results: ")
                print("    directory: "+res["directory"])
                print("        scene: "+res["scene"])
                print("     duration: "+str(res["duration"])+" sec")  

        if not os.path.exists(os.path.dirname(self.debugDir)):
            try:
                os.makedirs(os.path.dirname(self.debugDir))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        for res in results:
            with open(self.debugDir+self.stateFileName, "a") as stateFile:
                currentStateFile = open(res["directory"]+"/stateFile.state", "r") 
                stateFile.write(currentStateFile.read())
                currentStateFile.close()
            stateFile.close()

        copy(results[0]["directory"]+"/debug_scene.py", self.debugDir)

        counter = 1
        for line in fileinput.input(self.debugDir+self.stateFileName, inplace=True):
            if line.find('T=') != -1:
                line = 'T= '+str(self.periodSaveGIE[0]*counter)+'\n'
                print("%s" % line),
                counter += 1
            else : print(line),

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

        if not os.path.exists(os.path.dirname(self.dataDir)):
            try:
                os.makedirs(os.path.dirname(self.dataDir))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise


        self.nbrOfModes = readStateFilesAndComputeModes(stateFilePath = self.debugDir+self.stateFileName,
                                                        modesFileName = self.dataDir+self.modesFileName,
                                                        tol = self.tolModes,
                                                        addRigidBodyModes = self.addRigidBodyModes)

        if self.nbrOfModes == -1:
            raise ValueError("problem of execution of readStateFilesAndComputeModes")

        print('Number of Modes :'+str(self.nbrOfModes))

        print("PHASE 2 --- %s seconds ---" % (time.time() - start_time))

    def phase3(self):
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

        for i in range(self.nbPossibility):
            self.listSofaScene[i]['NBROFMODES'] = self.nbrOfModes
            self.listSofaScene[i]['NBTRAININGSET'] = self.nbTrainingSet
            # self.listSofaScene[i]["PARAMWRAPPER"] = self.paramWrapper

        filenames = ["phase2_prepareECSW.py","phase1_snapshots.py"]
        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(path+filename).read(), filename) )
             
        results = startSofa(self.listSofaScene, filesandtemplates, launcher=ParallelLauncher(4))

        if self.verbose:
            for res in results:
                print("Results: ")
                print("    directory: "+res["directory"])
                print("        scene: "+res["scene"])
                print("     duration: "+str(res["duration"])+" sec")

        try: 
            for fileName in self.savedElementsFilesNames :
                with open(self.debugDir+fileName, "a") as savedElementsFile:
                    currentStateFile = open(results[-1]["directory"]+'/'+fileName, "r") 
                    savedElementsFile.write(currentStateFile.read())
                    currentStateFile.close()
                savedElementsFile.close() 
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

        for res in results:

            for fileName in self.gieFilesNames :
                with open(self.debugDir+fileName, "a") as gieFile:
                    currentGieFile = open(res["directory"]+'/'+fileName, "r") 
                    gieFile.write(currentGieFile.read())
                    currentGieFile.close()
                gieFile.close()


        print("PHASE 3 --- %s seconds ---" % (time.time() - start_time))

    def phase4(self):
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

        for fileName in self.gieFilesNames :
            index = self.gieFilesNames.index(fileName)
            readGieFileAndComputeRIDandWeights( self.debugDir+fileName,
                                                self.dataDir+self.RIDFilesNames[index],
                                                self.dataDir+self.weightsFilesNames[index],
                                                self.tolGIE)

            self.activesNodesLists.append(  convertRIDinActiveNodes(self.dataDir+self.RIDFilesNames[index],
                                                                    self.debugDir+self.savedElementsFilesNames[index],
                                                                    self.dataDir+self.connectivityFilesNames[index]) )


        print("PHASE 4 --- %s seconds ---\n" % (time.time() - start_time))
        start_time = time.time()

        if self.subTopoList :
            print('there is at least one subTopo : '+str(self.subTopoList))
            for i in range(len(self.subTopoList)) :
                nodeName1 , nodeName2 = self.nodesToReduce[i]
                nodeName1 = nodeName1.split('/')[-1]
                nodeName2 = nodeName2.split('/')[-1]
                # print ('nodeName1 ', nodeName1)
                # print ('nodeName2 ', nodeName2)
                print self.activesNodesLists[i]
                print '###################\n\n'
                print self.activesNodesLists[i+1]
                print '===================\n\n'
                self.activesNodesLists[i] = list(set().union(self.activesNodesLists[i],self.activesNodesLists[i+1]))
                print self.activesNodesLists[i]

                with open(self.dataDir+'conectivity_'+nodeName1+'.txt', "w") as file:
                    for item in self.activesNodesLists[i]:
                      file.write("%i\n" % item)
                file.close()


        filenames = ["phase3_performECSW.py"]

        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(path+filename).read(), filename) )


        self.paramWrapper = []
        dataFolder = '/'+self.dataDir.split('/')[-2]+'/'

        for item in self.nodesToReduce :

            defaultParamMORMapping = {
                'input': '@../MechanicalObject',
                'modesPath': dataFolder+self.modesFileName}

            if isinstance(item,tuple):

                nodeName = item[0].split('/')[-1]
                nodeNameSubTopo = item[1].split('/')[-1]
                tmptParamForcefield = {
                    'performECSW': True,
                    'modesPath': dataFolder+self.modesFileName,
                    'RIDPath': dataFolder+'RID_'+nodeName+'.txt',
                    'weightsPath': dataFolder+'weight_'+nodeName+'.txt'}

                tmptParamForcefieldSubTopo = {
                    'performECSW': True,
                    'modesPath': dataFolder+self.modesFileName,
                    'RIDPath': dataFolder+'RID_'+nodeNameSubTopo+'.txt',
                    'weightsPath': dataFolder+'weight_'+nodeNameSubTopo+'.txt'}

                tmpParamMappedMatrixMapping = {
                    'template': 'Vec1d,Vec1d',
                    'object1': '@./MechanicalObject',
                    'object2': '@./MechanicalObject',
                    'listActiveNodesPath': dataFolder+'conectivity_'+nodeName+'.txt',
                    'performECSW': True}

                self.paramWrapper.append(   (item[0] , 
                                       {'subTopo' : nodeNameSubTopo,
                                        'paramForcefield': tmptParamForcefield.copy(),
                                        'paramMORMapping': defaultParamMORMapping.copy(),
                                        'paramMappedMatrixMapping': tmpParamMappedMatrixMapping.copy()} ) )

                self.paramWrapper.append(  (item[1] ,{'paramForcefield': tmptParamForcefieldSubTopo.copy()} ) )
            else:

                nodeName = item.split('/')[-1]

                tmptParamForcefield = {
                    'performECSW': True,
                    'modesPath': dataFolder+self.modesFileName,
                    'RIDPath': dataFolder+'RID_'+nodeName+'.txt',
                    'weightsPath': dataFolder+'weight_'+nodeName+'.txt'}

                tmpParamMappedMatrixMapping = {
                    'template': 'Vec1d,Vec1d',
                    'object1': '@./MechanicalObject',
                    'object2': '@./MechanicalObject',
                    'listActiveNodesPath': dataFolder+'conectivity_'+nodeName+'.txt',
                    'performECSW': True}

                self.paramWrapper.append(   (item , 
                                       {'paramForcefield': tmptParamForcefield.copy(),
                                        'paramMORMapping': defaultParamMORMapping.copy(),
                                        'paramMappedMatrixMapping': tmpParamMappedMatrixMapping.copy()} ) )

        finalScene = {}
        finalScene["ORIGINALSCENE"] = self.originalScene
        finalScene["PARAMWRAPPER"] = self.paramWrapper
        finalScene['NBROFMODES'] = self.nbrOfModes
        finalScene["nbIterations"] = 1
        finalScene["TOANIMATE"] = self.toAnimate
        finalScene["PACKAGENAME"] = self.packageName

        results = startSofa([finalScene], filesandtemplates, launcher=ParallelLauncher(4))
        # print(results[0]["scene"])
        shutil.move(results[0]['directory']+'/'+self.packageName+'.py', self.outputDir)
        copy(self.meshDir, self.outputDir+'/mesh/')

        createPackage = True
        if createPackage :

            copy(self.outputDir, pathToReducedModel+self.packageName+'/')

            try:
                with open(path+'myInit.txt', "r") as myfile:
                    myInit = myfile.read()

                    myInit = myInit.replace('MyReducedModel',self.packageName[0].upper()+self.packageName[1:])
                    myInit = myInit.replace('myReducedModel',self.packageName)

                    with open(pathToReducedModel+self.packageName+'/__init__.py', "a") as logFile:
                        logFile.write(myInit)
                        logFile.close()

                    myfile.close()
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

        print('The reduction is now finished !')
        print("TOTAL TIME --- %s seconds ---" % (time.time() - self.init_time))

 
def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)