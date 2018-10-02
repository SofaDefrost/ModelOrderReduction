# -*- coding: utf-8 -*-

import os
import yaml
from launcher import *

def getGraphScene(node,getObj=False):
    class Namespace(object):
        pass
    tmp = Namespace()
    tmp.results = {}
    tmp.results["tree"] = {}
    tmp.results["obj"] = {}
    # tmp.results = None

    def buildTree(node,dic):
        if node.name != "root":
            if getObj:
                dic[node] = {}
            else:
                dic[node.name] = {}
                # dic = AnyNode(node.name = )

        for child in node.getChildren():
            if node.name != "root":
                if getObj:
                    buildTree(child,dic[node])
                else:
                    buildTree(child,dic[node.name])
            else:
                buildTree(child,dic)
    def objTree(node,dic):

        if getObj:
            dic[node] = {}
        else:
            dic[node.name] = {}

        for obj in node.getObjects():
            # print('root '+str(type(obj).__name__)+' '+obj.getName())

            if getObj:
                dic[node][obj] = obj.getClassName()
            else:
                dic[node.name][obj.getName()] = obj.getClassName()

        for child in node.getChildren():
            if getObj:
                objTree(child,dic)
            else:
                objTree(child,dic)

    buildTree(node,tmp.results["tree"])
    # print(tmp.results["tree"])
    objTree(node,tmp.results["obj"])
    # print(tmp.results["obj"])

    # for key in tmp.results:
    #     print(str(key)+' : '+str(tmp.results[key])+'\n')

    return tmp.results

def dumpGraphScene(node,fileName='graphScene.yml'):

    data = getGraphScene(node)
    with open(fileName, 'w') as ymlfile:
        yaml.dump(data,ymlfile, default_flow_style=False)

def importScene(filePath):
    numiterations = 1
    filename = "importScene.py"
    path = os.path.dirname(os.path.abspath(__file__))+'/template/'
    filesandtemplates = [ (open(path+filename).read(), filename)]

    listSofaScene = [
                        {"ORIGINALSCENE": filePath,
                         "nbIterations":numiterations}
                    ]

    results = startSofa(listSofaScene, filesandtemplates, launcher=SerialLauncher())

    with open(results[0]["directory"]+'/graphScene.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    return cfg