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

        self.dataDir = self.outputDir+os.sep+'data'+os.sep
        self.debugDir = self.outputDir+os.sep+'debug'+os.sep
        self.meshDir = self.outputDir+os.sep+'mesh'+os.sep

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
            u.copyFileIntoAnother(os.sep.join([res["directory"],"stateFile.state"]),self.debugDir+stateFileName)

            if velocityFileName is not None:
                u.copyFileIntoAnother(res["directory"]+"/stateFileVelocity.state",self.debugDir+velocityFileName)
            if gie:
                for fileName in gie :
                    u.copyFileIntoAnother(os.sep.join([res["directory"],fileName]),self.debugDir+fileName)


        self.cleanStateFile(periodSaveGIE,stateFileName)

    def finalizePackage(self,result):
        '''
        '''

        shutil.move(os.sep.join([result['directory'],self.packageName+'.py']), 
                    os.sep.join([self.outputDir,self.packageName+'.py']))

        with open(os.sep.join([result['directory'],'meshFiles.txt']), "r") as meshFiles:
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

        u.copy(self.outputDir, pathToReducedModel+self.packageName+os.sep)

        try:
            with open(pathToTemplate+'myInit.txt', "r") as myfile:
                myInit = myfile.read()

                myInit = myInit.replace('MyReducedModel',self.packageName[0].upper()+self.packageName[1:])
                myInit = myInit.replace('myReducedModel',self.packageName)

                with open(pathToReducedModel+os.sep.join([self.packageName,'__init__.py']), "a") as logFile:
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