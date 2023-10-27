# -*- coding: utf-8 -*-

import os, sys
import platform
import fileinput
import shutil

path = os.path.dirname(os.path.abspath(__file__))
pathToTemplate = path+'/../template/'
pathToReducedModel = path+'/../../../morlib/'
sys.path.insert(0,path+'/../../../')

from mor.utility import utility as u

slash = '/'
if "Windows" in platform.platform():
    slash ='\\'


class PackageBuilder():
    """
    **Contain all the parameters & functions related to building the package**
    """
    def __init__(self,outputDir,packageName = None ,addToLib = False):

        self.outputDir = outputDir
        self.meshes = []

        self.addToLibBool = addToLib

        if packageName :
            self.packageName = 'reduced_'+packageName

            if os.path.isdir(pathToReducedModel+self.packageName) and addToLib:
                raise Exception('A Package named %s already exist in the MOR lib !\nPlease choose another name for this new package' % packageName)

        self.dataDir = self.outputDir+slash+'data'+slash
        self.debugDir = self.outputDir+slash+'debug'+slash
        self.meshDir = self.outputDir+slash+'mesh'+slash

    def checkNodeNbr(self,modeFileName):
        '''
        '''

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
        '''
        '''

        counter = 1
        for line in fileinput.input(self.debugDir+stateFileName, inplace=True):
            if line.find('T=') != -1:
                line = 'T= '+str(periodSaveGIE*counter)+'\n'
                print("%s" % line, end="")
                counter += 1
            else : print(line, end="")

    def copyAndCleanState(self,results,periodSaveGIE,stateFileName,velocityFileName=None,gie=None):
        '''
        '''

        u.checkExistance(self.debugDir)

        if os.path.exists(self.debugDir+stateFileName):
            os.remove(self.debugDir+stateFileName)
        if velocityFileName and os.path.exists(self.debugDir+velocityFileName):
            os.remove(self.debugDir+velocityFileName)
        if gie:
            for fileName in gie :
                if os.path.exists(self.debugDir+fileName):
                    os.remove(self.debugDir+fileName)


        for res in results:
            u.copyFileIntoAnother(res["directory"]+slash+"stateFile.state",self.debugDir+stateFileName)

            if velocityFileName is not None:
                u.copyFileIntoAnother(res["directory"]+"/stateFileVelocity.state",self.debugDir+velocityFileName)
            if gie:
                for fileName in gie :
                    u.copyFileIntoAnother(res["directory"]+slash+fileName,self.debugDir+fileName)


        self.cleanStateFile(periodSaveGIE,stateFileName)

    def finalizePackage(self,result):
        '''
        '''

        shutil.move(result['directory']+slash+self.packageName+'.py', self.outputDir+slash+self.packageName+'.py')

        with open(result['directory']+slash+'meshFiles.txt', "r") as meshFiles:
            self.meshes = meshFiles.read().splitlines()

        u.checkExistance(self.meshDir)

        if self.meshes:
            for mesh in self.meshes:
                u.copy(mesh, self.meshDir)

        if self.addToLibBool :

            self.addToLib()

    def addToLib(self):
        '''
        '''

        u.copy(self.outputDir, pathToReducedModel+self.packageName+slash)

        try:
            with open(pathToTemplate+'myInit.txt', "r") as myfile:
                myInit = myfile.read()

                myInit = myInit.replace('MyReducedModel',self.packageName[0].upper()+self.packageName[1:])
                myInit = myInit.replace('myReducedModel',self.packageName)

                with open(pathToReducedModel+self.packageName+slash+'__init__.py', "a") as logFile:
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
            print ("Unexpected error:", sys.exc_info()[0])
            raise