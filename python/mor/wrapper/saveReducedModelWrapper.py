# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("/home/felix/SOFA/plugin/STLIB/python")
from stlib.scene.wrapper import Wrapper

path = os.path.dirname(os.path.abspath(__file__))+'/template/'

logBool = True
footer = False

# found = 0
# counter = 0

class MORWrapper(Wrapper):
    def __init__(self, node, attachedFunction, datacache, log = None):

        super(MORWrapper, self).__init__(node, attachedFunction, datacache)

        self.log = log
        if self.log:

            self.functionName = 'Reduced_'+self.datacache['originalScene']
            self.myHeader = ""
            self.myFooter = ""
            self.visu = None

            self.nodeName  = self.datacache['nodesToReduce'].split('/')[-1]

            if logBool :
                self.writeHeader()
            else :
                self.writeCreateChild(self.node)


    def createObject(self, type, **kwargs):
        # print(type) 
        objectArg = self.attachedFunction(self.node,type,self.datacache,kwargs) 
        # objectArg as to contain (newType, **newKwargs, datacache)
        if objectArg == None :

            self.writeCreateObject(self.node,type,kwargs)
            return self.node.createObject(type, **kwargs)
        # else :
        #   if objectArg[0] == -1 :
        #     self.datacache = objectArg[2]

        #     if self.log:
        #         writeCreateObject(type,self.log,self.node,myArgs)

        #     return self.node.createObject(type, **kwargs)
        #   else: 
        #     self.datacache = objectArg[2]

        #     if self.log:
        #         writeCreateObject(type,self.log,self.node,myArgs)

        #     return self.node.createObject(objectArg[0], **objectArg[1])
    
    def createChild(self, name):
        return MORWrapper(self.node.createChild(name), self.attachedFunction ,self.datacache ,self.log)


    def writeCreateChild(self,node):
        # global found

            with open(self.log, "a") as myfile:
                myfile.write("\n\n")
                if node.name in self.datacache['toKeep']:
                    if node.name.find('_MOR') != -1:
                        myfile.write("    "+node.name+" = attachedTo.createChild(name)\n")
                        # found += 1
                    else:
                        myfile.write("    "+node.name+' = '+node.getParents()[0].name+".createChild('"+node.name+"')\n")
                        # found += 1

                myfile.close()


    def writeCreateObject(self,node,type,kwargs):
        # global counter

        if self.log:
            if node.getPathName().find(self.datacache['nodesToReduce']) != -1:
                print('In '+node.name+' with object : '+str(type))
                if node.name in self.datacache['toKeep']:
                    print (node.name)
                    tmpList = ['MeshGmshLoader','MeshVTKLoader','MeshSTLLoader']
                    if type in tmpList:
                        kwargs['rotation'] = 'rotation'
                        kwargs['translation'] = 'translation'
                        kwargs['filename'] = 'mesh/'+kwargs['filename'].split('/')[-1]
                        myArgs = ', '.join("{} = '{}' ".format(key, val) for key, val in kwargs.items())
                        myArgs = myArgs.replace("'rotation'","rotation").replace("'translation'","translation")
                        # print(myArgs)
                    elif type == 'BoxROI':
                        myArgs = ''
                    else:
                        if str(type).find('ForceField'):
                            kwargs.pop('initialPoints', None)
                            
                        # if str(type).find('SetTopologyContainer'):
                        #     kwargs.pop('nbPoints', None)
                        #     kwargs.pop('points', None)

                        if type == 'MeshTopology':
                            kwargs.pop('edges', None)

                        if type == 'MechanicalObject':
                            kwargs.pop('force', None)
                            kwargs.pop('rest_position', None)
                            kwargs.pop('reset_position', None)
                            kwargs.pop('velocity', None)
                            kwargs.pop('derivX', None)
                            kwargs.pop('externalForce', None)
                            if node.name.find('_MOR') == -1:
                                kwargs.pop('position', None)
                            
                        if type == 'UniformMass':
                            kwargs.pop('indices', None)
                        if type == 'HyperReducedTetrahedronFEMForceField':
                            kwargs.pop('initialPoints', None)    
                        myArgs = ', '.join("{} = '{}' ".format(key, val) for key, val in kwargs.items())

                    # print(myArgs)
                    if myArgs:
                        with open(self.log, "a") as myfile:
                            myfile.write("    "+node.name+".createObject('" + type +"' , "+myArgs+")\n")
                            myfile.close()

                elif node.name in self.datacache['toKeep']:
                    print (node.name)

                elif type == 'OglModel':
                    self.visu = kwargs['fileMesh']
                    
            # if found == len(self.datacache['toKeep']):
            #     counter += 1
            #     print('counter : '+str(counter)+' out of '+str(len(node.getObjects())))
            #     if len(node.getObjects()) == counter:

            #         visuArg = { 'color': 'surfaceColor',
            #                     'rotation' : 'rotation',
            #                     'translation' : 'translation'}

            #         if self.visu:
            #             visuArg['fileMesh'] = kwargs['fileMesh']


            #         myArgs = ' , '.join("{} = '{}' ".format(key, val) for key, val in visuArg.items())
            #         myArgs = myArgs.replace("'rotation'","rotation").replace("'translation'","translation").replace("'surfaceColor'","surfaceColor")
            #         visu = "'OglModel' , "+myArgs

            #         self.writeFooter(visu)


    def writeHeader(self):
        global logBool
        with open(path+'myHeader.txt', "r") as myfile:
            self.myHeader = myfile.read()

            self.myHeader = self.myHeader.replace('MyReducedModel',self.functionName)

            with open(self.log, "a") as logFile:
                logFile.write(self.myHeader)
                logFile.close()

            myfile.close()

        # print(self.myHeader)
        logBool = False

    def writeFooter(self,visu):
        global footer

        if not footer:
            with open(path+'myFooter.txt', "r") as myfile:
                self.myFooter = myfile.read()

                self.myFooter = self.myFooter.replace('MyReducedModel',self.functionName)
                self.myFooter = self.myFooter.replace('myReducedModel',self.nodeName)
                self.myFooter = self.myFooter.replace('arg',visu)

                with open(self.log, "a") as logFile:
                    logFile.write(self.myFooter)
                    logFile.close()

                myfile.close()


            # print(self.myFooter)
            footer = True