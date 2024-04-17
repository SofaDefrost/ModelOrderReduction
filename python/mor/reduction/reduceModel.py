# -*- coding: utf-8 -*-
###############################################################################
#            Model Order Reduction plugin for SOFA                            #
#                         version 1.0                                         #
#                       Copyright © Inria                                     #
#                       All rights reserved                                   #
#                       2018                                                  #
#                                                                             #
# This software is under the GNU General Public License v2 (GPLv2)            #
#            https://www.gnu.org/licenses/licenses.en.html                    #
#                                                                             #
#                                                                             #
#                                                                             #
# Authors: Olivier Goury, Felix Vanneste                                      #
#                                                                             #
# Contact information: https://project.inria.fr/modelorderreduction/contact   #
###############################################################################
"""
**Main module to perform reduction**
"""

import os,sys
import time
import datetime
import glob
import platform

try:
    from launcher import ParallelLauncher, startSofa
except:
    raise ImportError("You need to give to PYTHONPATH the path to sofa-launcher in order to use this tool\n"\
                     +"Enter this command in your terminal (for temporary use) or in your .bashrc to resolve this:\n"\
                     +"export PYTHONPATH=/PathToYourSofaSrcFolder/tools/sofa-launcher")

path = os.path.dirname(os.path.abspath(__file__))
pathToTemplate = path+"/template/"
pathToReducedModel = path+"/../../morlib/"
pathToAnimation = path+"/../animation/shakingAnimations.py"
sys.path.insert(0,path+"/../../")

from mor.utility import utility as u
from mor.reduction.container import ReductionAnimations
from mor.reduction.container import PackageBuilder
from mor.reduction.container import ReductionParam
from mor.reduction import script

slash = '/'
if "Windows" in platform.platform():
    slash ='\\'

class ReduceModel():
    """
    **Main class that will perform the reduction**

    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | argument          | type                            | definition                                                                                |
    +===================+=================================+===========================================================================================+
    | originalScene     | str                             | absolute path to original scene                                                           |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | nodeToReduce      | str                             | Paths to models to reduce                                                                 |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | listObjToAnimate  | list(:py:class:`.ObjToAnimate`) | list conaining all the ObjToAnimate that will be use to shake our model                   |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | tolModes          | float                           | tolerance applied to choose the modes                                                     |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | tolGIE            | float                           | tolerance applied to calculated GIE                                                       |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | outputDir         | str                             | absolute path to output directiry in which all results will be stored                     |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | packageName       | str                             | Which name will have the final componant ( & package if the option addToLib is activated) |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | addToLib          | Bool                            | If ``True`` will add in the python library of this plugin the finalized reduced component |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | verbose           | Bool                            | display more or less verbose                                                              |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | addRigidBodyModes | list(int)                       | List of 3 of 0/1 that will allow translation along [x,y,z] axis of our reduced model      |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | nbrCPU            | int                             | Number of CPU we will use to generate/calculate the reduced model                         |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+
    | phaseToSave       | list(int)                       | List of 0/1 indicating during which phase to save the elements/X0                         |
    |                   |                                 | ``by default will save during first phase``                                               |
    +-------------------+---------------------------------+-------------------------------------------------------------------------------------------+

    """
    def __init__(self,
        originalScene,
        nodeToReduce,
        listObjToAnimate,
        tolModes,
        tolGIE,
        outputDir,
        packageName = 'myReducedModel',
        addToLib = False,
        verbose = False,
        addRigidBodyModes = False,
        nbrCPU = 4,
        phaseToSave = None,
        saveVelocitySnapshots = None,
        listPathToAnimation = []):

        self.originalScene = os.path.normpath(originalScene)
        self.nodeToReduce = nodeToReduce

        ### Obj Containing all the argument & function about how the shaking will be done and with which actuators
        self.reductionAnimations = ReductionAnimations(listObjToAnimate,listPathToAnimation)

        ### Obj Containing all the argument & function about how to create the end package and where 
        outputDir = os.path.normpath(outputDir)
        self.packageBuilder = PackageBuilder(outputDir,packageName,addToLib)

        ### Obj Containing all the argument & function about the actual reduction
        self.reductionParam = ReductionParam(tolModes,tolGIE,addRigidBodyModes,self.packageBuilder.dataDir,saveVelocitySnapshots)

        ### With the previous parameters (listObjToAnimate/nbPossibility) we can set our training set number
        self.reductionParam.setNbTrainingSet(   listObjToAnimate[0].params['rangeOfAction'],
                                                listObjToAnimate[0].params['incr'])


        self.reductionParam.addParamWrapper(self.nodeToReduce)

        self.reductionParam.setFilesName()

        # remove: it's done automatically no need to specifiy one, or do we ?
        self.phaseToSave = phaseToSave
        self.phaseToSaveIndex = 0
        ###

        self.nbrCPU = nbrCPU
        self.verbose = verbose

        self.activesNodesLists = []
        self.listSofaScene = []

        if (verbose):
            strInfo = 'periodSaveGIE : '+str(self.reductionParam.periodSaveGIE)+' | '
            strInfo += 'nbTrainingSet : '+str(self.reductionParam.nbTrainingSet)+' | '
            strInfo += 'nbIterations : '+str(self.reductionAnimations.nbIterations)+'\n'
            # strInfo += "List of phase :"+str(self.reductionAnimations.phaseNumClass)+'\n'
            strInfo += "##################################################"
            print(strInfo)

    def setListSofaScene(self,phasesToExecute=None,phase=None):
        """
        **Will generate a list containing dictionnaries, 
        where each dictionnary is a set of argument for the execution of one SOFA scene.**

        +-----------------+-----------+----------------------------------------------------------+
        | argument        | type      | definition                                               |
        +=================+===========+==========================================================+
        | phasesToExecute | list(int) | Allow to choose which phase to execute for the reduction |
        |                 |           |                                                          |
        |                 |           | ``by default will select all the phase``                 |
        +-----------------+-----------+----------------------------------------------------------+

        The number of dictionnaries generated depend upon either the number of action possibility 
        (self.reductionAnimations.nbPossibility) or you can give with *phasesToExecute* specifically 
        which possibility you want to execute.

        **example :**

            You have 2 :py:class:`.ObjToAnimate` (thing that will be animated during the execution). 
            From self.reductionAnimations you will have 2^2 possibilities:
            
            [0,0] | [0,1] | [1,0] | [1,1] --> where 0 mean no animation & 1 animation

            * if you give no argument, phasesToExecute = [0,1,2,3]
                ``it will execute possibilty 0,1,2 & 3``
            * if you give phasesToExecute=[1,3]
                ``it will execute possibility 1 & 3``

        """
        self.listSofaScene = []

        if not phasesToExecute:
            phasesToExecute = list(range(self.reductionAnimations.nbPossibility))

        if not self.phaseToSave:
            self.phaseToSave = self.reductionAnimations.phaseNumClass[phasesToExecute[0]]
            self.phaseToSaveIndex = 0

        if (phase != None):
            self.listSofaScene.append({ "ORIGINALSCENE": self.originalScene,
                                        "LISTOBJTOANIMATE": self.reductionAnimations.listObjToAnimate,
                                        "PHASE": phase,
                                        "PERIODSAVEGIE" : self.reductionParam.periodSaveGIE,
                                        "PARAMWRAPPER" : self.reductionParam.paramWrapper,
                                        "nbIterations":self.reductionAnimations.nbIterations,
                                        "PHASETOSAVE" : self.phaseToSave,
                                        "LISTANIMATIONTOIMPORT": self.reductionAnimations.listPathToAnimation})
        else:
            for i in phasesToExecute:
                if i >= self.reductionAnimations.nbPossibility or i < 0 :
                    raise ValueError("phasesToExecute incorrect, select an non-existent phase : "+phasesToExecute)

                self.listSofaScene.append({ "ORIGINALSCENE": self.originalScene,
                                            "LISTOBJTOANIMATE": self.reductionAnimations.listObjToAnimate,
                                            "PHASE": self.reductionAnimations.phaseNumClass[i],
                                            "PERIODSAVEGIE" : self.reductionParam.periodSaveGIE,
                                            "PARAMWRAPPER" : self.reductionParam.paramWrapper,
                                            "nbIterations":self.reductionAnimations.nbIterations,
                                            "PHASETOSAVE" : self.phaseToSave,
                                            "LISTANIMATIONTOIMPORT": self.reductionAnimations.listPathToAnimation})

    def generateTestScene(self,phase,template="phase1_snapshots.py"):            

        self.setListSofaScene(phase=phase)
        if(template=="phase2_prepareECSW.py"):
            nbrOfModesPossible = self.packageBuilder.checkNodeNbr(self.reductionParam.modesFileName)
            self.listSofaScene[0]['NBROFMODES'] = nbrOfModesPossible

        filesandtemplates = [(open(pathToTemplate+template).read(), template)]

        u.customLauncher(filesandtemplates,self.listSofaScene[0],self.packageBuilder.debugDir)

    def performReduction(self,phasesToExecute=None,nbrOfModes=None):
        """
        **Perform all the steps of the reduction in one function**

        +-----------------+-----------+----------------------------------------------------------+
        | argument        | type      | definition                                               |
        +=================+===========+==========================================================+
        | phasesToExecute | list(int) || Allow to choose which phase to execute for the reduction|
        |                 |           || *more details see* :py:func:`setListSofaScene`          |
        +-----------------+-----------+----------------------------------------------------------+
        | nbrOfModes      | int       || Number of modes you want to keep                        |
        |                 |           || ``by default will keep them all``                       |
        +-----------------+-----------+----------------------------------------------------------+
        
        If you are sure of all the parameters this way is recommended to gain time

        """
        ### This initila time we allow us to give at the end the total time execution
        init_time = time.time()

        self.phase1(phasesToExecute)
        self.phase2()
        self.phase3(phasesToExecute,nbrOfModes)
        self.phase4(nbrOfModes)

        tps = int(round(time.time() - init_time))
        print("TOTAL TIME --- %s ---" % (datetime.timedelta(seconds=tps) ) )

    def phase1(self,phasesToExecute=None):
        """
        **The step will launch in parallel multiple Sofa scene (nbrCPU by nbrCPU number of scene) until
        it has run all the scene in the sequence.** 

        +-----------------+-----------+----------------------------------------------------------+
        | argument        | type      | definition                                               |
        +=================+===========+==========================================================+
        | phasesToExecute | list(int) || Allow to choose which phase to execute for the reduction|
        |                 |           || *more details see* :py:func:`setListSofaScene`          |
        +-----------------+-----------+----------------------------------------------------------+
        
        To run the SOFA scene in parallele we use the ``sofa launcher`` utility

        What does it do to each scene:

            - Add animation to each :py:class:`.ObjToAnimate` we want for our model in the predifined sequence
            - Add a componant to save the shaking resulting states (WriteState)
            - Take all the resulting states files and combines them in one file put in the ``debug`` dir with a debug scene

        """
        start_time = time.time()
        if not phasesToExecute:
            phasesToExecute = list(range(self.reductionAnimations.nbPossibility))

        self.setListSofaScene(phasesToExecute)

        filenames = ["phase1_snapshots.py","debug_scene.py"]
        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(pathToTemplate+filename).read(), filename) )

        results = startSofa(self.listSofaScene, filesandtemplates, launcher=ParallelLauncher(self.nbrCPU))

        if self.verbose:
            for res in results:
                print("Results: ")
                print("    directory: "+res["directory"])
                print("        scene: "+res["scene"])
                print("     duration: "+str(res["duration"])+" sec")  

        self.packageBuilder.copyAndCleanState(results,self.reductionParam.periodSaveGIE,self.reductionParam.stateFileName,self.reductionParam.velocityFileName)
        u.copy(results[self.phaseToSaveIndex]["directory"]+slash+"debug_scene.py", self.packageBuilder.debugDir)

        print("PHASE 1 --- %s seconds ---" % (time.time() - start_time))

    def phase2(self):
        """
        **With the previous result obtain in during :meth:`phase1` we compute the modes**

        See :py:mod:`.ReadStateFilesAndComputeModes` for the way the modes are determined.

        It will set ``nbrOfModes`` to its maximum, but it can be changed has argument to the next step : :meth:`phase3`

        """
        start_time = time.time()

        u.checkExistance(self.packageBuilder.dataDir)
 
        self.reductionParam.nbrOfModes = script.readStateFilesAndComputeModes(stateFilePath = self.packageBuilder.debugDir+self.reductionParam.stateFileName,
                                                        modesFileName = self.packageBuilder.dataDir+self.reductionParam.modesFileName,
                                                        tol = self.reductionParam.tolModes,
                                                        addRigidBodyModes = self.reductionParam.addRigidBodyModes,
                                                        verbose= self.verbose)

        if self.reductionParam.nbrOfModes == -1:
            raise ValueError("problem of execution of readStateFilesAndComputeModes")

        print("PHASE 2 --- %s seconds ---" % (time.time() - start_time))

    def phase3(self,phasesToExecute=None,nbrOfModes=None):
        """
        **This step will launch in parallel multiple Sofa scene (nbrCPU by nbrCPU number of scene) until
        it has run all the scene in the sequence.**

        +-----------------+-----------+----------------------------------------------------------+
        | argument        | type      | definition                                               |
        +=================+===========+==========================================================+
        | phasesToExecute | list(int) || Allow to choose which phase to execute for the reduction|
        |                 |           || *more details see* :meth:`setListSofaScene`             |
        +-----------------+-----------+----------------------------------------------------------+
        | nbrOfModes      | int       || Number of modes you want to keep                        |
        |                 |           || ``by default will keep them all``                       |
        +-----------------+-----------+----------------------------------------------------------+

        To run the SOFA scene in parallele we use the ``sofa launcher`` utility

        What does it do to each scene:

            - Take the previous one and add the model order reduction component:
               - HyperReducedFEMForceField
               - MappedMatrixForceFieldAndMas
               - ModelOrderReductionMapping
            - Produce an Hyper Reduced description of the model
            - Produce files listing the different element to keep
            - Take all the resulting states files and combines them in one file put in the ``debug`` dir with a debug scene


        """
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

        filenames = ["phase2_prepareECSW.py","phase1_snapshots.py","debug_scene.py"]
        filesandtemplates = []
        for filename in filenames:                
            filesandtemplates.append( (open(pathToTemplate+filename).read(), filename) )
        results = startSofa(self.listSofaScene, filesandtemplates, launcher=ParallelLauncher(self.nbrCPU))

        if self.verbose:
            for res in results:
                print("Results: ")
                print("    directory: "+res["directory"])
                print("        scene: "+res["scene"])
                print("     duration: "+str(res["duration"])+" sec")

        files = glob.glob(results[self.phaseToSaveIndex]["directory"]+slash+"*_elmts.txt")
        if files:
            for i,file in enumerate(files):
                file = os.path.normpath(file)
                files[i] = file.split(slash)[-1]
            # print("FILES ----------->",files)
            self.reductionParam.savedElementsFilesNames = files

        for fileName in self.reductionParam.savedElementsFilesNames :
            u.copyFileIntoAnother(results[self.phaseToSaveIndex]["directory"]+slash+fileName,self.packageBuilder.debugDir+fileName)

        files = glob.glob(results[self.phaseToSaveIndex]["directory"]+slash+"*_Gie.txt")
        if files: 
            for i,file in enumerate(files):
                file = os.path.normpath(file)
                files[i] = file.split(slash)[-1]
            # print("FILES ----------->",files)
            self.reductionParam.gieFilesNames = files
        else:
            raise IOError("Missing GIE Files")

        self.packageBuilder.copyAndCleanState(  results,self.reductionParam.periodSaveGIE,
                                                'step2_'+self.reductionParam.stateFileName,
                                                gie=self.reductionParam.gieFilesNames)


        print("PHASE 3 --- %s seconds ---" % (time.time() - start_time))

    def phase4(self,nbrOfModes=None):
        """
        **The final step will gather all the results in 1 folder and build a reusable scene from it**

        +-----------------+-----------+----------------------------------------------------------+
        | argument        | type      | definition                                               |
        +=================+===========+==========================================================+
        | nbrOfModes      | int       || Number of modes you want to keep                        |
        |                 |           || ``by default will keep them all``                       |
        +-----------------+-----------+----------------------------------------------------------+

        Final step :

            - compute the RID and Weigts with :py:mod:`.ReadGieFileAndComputeRIDandWeights`
            - finalize the package
            - add it to the plugin library if option activated

        """
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

        # print(files)
        files = glob.glob(self.packageBuilder.debugDir+"*_elmts.txt")
        if files:
            for i,file in enumerate(files):
                file = os.path.normpath(file)
                files[i] = file.split(slash)[-1]
            # print("FILES ----------->",files)
            self.reductionParam.savedElementsFilesNames = files

        files = glob.glob(self.packageBuilder.debugDir+"*_Gie.txt")
        if files: 
            for i,file in enumerate(files):
                file = os.path.normpath(file)
                files[i] = file.split(slash)[-1]
            # print("FILES ----------->",files)
            self.reductionParam.gieFilesNames = files


        for i , gie in enumerate(self.reductionParam.gieFilesNames):
            tmp = gie.replace('_Gie.txt','')
            for j , elmts in enumerate(self.reductionParam.savedElementsFilesNames):
                if tmp in elmts:
                    tmp = self.reductionParam.savedElementsFilesNames[j]
                    self.reductionParam.savedElementsFilesNames[j] = self.reductionParam.savedElementsFilesNames[i]
                    self.reductionParam.savedElementsFilesNames[i] = tmp

        self.reductionParam.RIDFilesNames = []
        self.reductionParam.weightsFilesNames = []
        for fileName in self.reductionParam.gieFilesNames :
            if not os.path.isfile(self.packageBuilder.debugDir+fileName):
                raise IOError("There is no GIE file at "+self.packageBuilder.debugDir+fileName\
                    +"\nPlease give one at this location or indicate the correct location or re-generate one with phase 3")

            self.reductionParam.RIDFilesNames.append(fileName.replace('_Gie','_RID'))
            self.reductionParam.weightsFilesNames.append(fileName.replace('_Gie','_weight'))


        for i , fileName in enumerate(self.reductionParam.gieFilesNames) :

            script.readGieFileAndComputeRIDandWeights( self.packageBuilder.debugDir+fileName,
                                                self.packageBuilder.dataDir+self.reductionParam.RIDFilesNames[i],
                                                self.packageBuilder.dataDir+self.reductionParam.weightsFilesNames[i],
                                                self.reductionParam.tolGIE,
                                                verbose= self.verbose)

        filename = "phase3_performECSW.py"
        filesandtemplates = [(open(pathToTemplate+filename).read(), filename)]

        self.reductionParam.addParamWrapper(self.nodeToReduce, prepareECSW = False)

        finalScene = {}
        finalScene["ORIGINALSCENE"] = self.originalScene
        finalScene["PARAMWRAPPER"] = self.reductionParam.paramWrapper
        finalScene['NBROFMODES'] = nbrOfModes
        finalScene["nbIterations"] = 1
        finalScene["ANIMATIONPATHS"] = self.reductionAnimations.listOfLocation
        finalScene["PACKAGENAME"] = self.packageBuilder.packageName

        results = startSofa([finalScene], filesandtemplates, launcher=ParallelLauncher(1))
        self.packageBuilder.finalizePackage(results[0])

        print("PHASE 4 --- %s seconds ---\n" % (time.time() - start_time))
        print('The reduction is now finished !')
        # return self.packageBuilder.outputDir+'/'+self.packageBuilder.packageName+'.py'
