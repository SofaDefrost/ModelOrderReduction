# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("/home/felix/SOFA/plugin/STLIB/python")
from stlib.scene.wrapper import Wrapper

class MORWrapper(Wrapper):
    def __init__(self, node, attachedFunction, datacache, log = None):

        super(MORWrapper, self).__init__(node, attachedFunction, datacache)

        self.log = log
        if self.log:

            self.functionName = 'Reduced_'+self.datacache['originalScene']

            self.writeCreateChild(self.node)


    def createObject(self, type, **kwargs):
        # print(type) 
        objectArg = self.attachedFunction(self.node,type,self.datacache,kwargs) 
        # objectArg as to contain (newType, **newKwargs, datacache)
        if objectArg == None :

            if self.log:
                self.writeCreateObject(self.node,type,kwargs)
            return self.node.createObject(type, **kwargs)

    
    def createChild(self, name):
        return MORWrapper(self.node.createChild(name), self.attachedFunction ,self.datacache ,self.log)


    def writeCreateChild(self,node):
        if node.name in self.datacache['toKeep']:
            with open(self.log, "a") as myfile:
                myfile.write("\n\n")
                
                if node.name.find('_MOR') != -1:
                    myfile.write("    "+node.name+" = attachedTo.createChild(name)\n")
                    # found += 1
                else:
                    myfile.write("    "+node.name+' = '+node.getParents()[0].name+".createChild('"+node.name+"')\n")
                    # found += 1

                myfile.close()


    def writeCreateObject(self,node,type,kwargs):
        if node.getPathName().find(self.datacache['nodesToReduce']) != -1:
            # print('In '+node.name+' with object : '+str(type))
            if node.name in self.datacache['toKeep']:
                # print ('node.name toKeep : '+node.name)
                tmpList = ['MeshGmshLoader','MeshVTKLoader','MeshSTLLoader']
                if type in tmpList:
                    kwargs['rotation'] = 'rotation'
                    kwargs['translation'] = 'translation'
                    kwargs['filename'] = 'mesh/'+kwargs['filename'].split('/')[-1]
                    myArgs = ', '.join("{} = '{}' ".format(key, val) for key, val in kwargs.items())
                    myArgs = myArgs.replace("'rotation'","rotation").replace("'translation'","translation")
                    # print(myArgs)
                elif type == 'BoxROI':
                    tmp = [float(x) for x in kwargs['box'].split(' ')]
                    myArgs = "name= '"+kwargs['name']+"' , box=translate(translation,rotate(rotation,"+str(tmp)+") )"
                    # print('BOXROI ARG: ',myArgs)
                else:
                    if str(type).find('ForceField'):
                        kwargs.pop('initialPoints', None)
                        
                    if str(type).find('SetTopologyContainer'):
                        kwargs.pop('nbPoints', None)
                        kwargs.pop('points', None)

                    if type == 'MeshTopology':
                        kwargs.pop('edges', None)

                    if type == 'MechanicalObject':
                        kwargs.pop('force', None)
                        kwargs.pop('rest_position', None)
                        kwargs.pop('reset_position', None)
                        kwargs.pop('velocity', None)
                        kwargs.pop('derivX', None)
                        kwargs.pop('externalForce', None)
                        kwargs.pop('size', None)
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