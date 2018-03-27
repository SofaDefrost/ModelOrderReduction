# -*- coding: utf-8 -*-
import sys
sys.path.append("/home/felix/SOFA/plugin/STLIB/python")
from stlib.scene.wrapper import Wrapper

class MORWrapper(Wrapper):

    def createObject(self, type, **kwargs):
        # print(type) 
        objectArg = self.attachedFunction(self.node,type,self.datacache,kwargs) 
        # objectArg as to contain (newType, **newKwargs, datacache)
        if objectArg == None :
          return self.node.createObject(type, **kwargs)
        else :
          if objectArg[0] == -1 :
            self.datacache = objectArg[2]
            return self.node.createObject(type, **kwargs)
          else: 
            self.datacache = objectArg[2]
            return self.node.createObject(objectArg[0], **objectArg[1])
    
    def createChild(self, name):
        return MORWrapper(self.node.createChild(name), self.attachedFunction ,self.datacache)