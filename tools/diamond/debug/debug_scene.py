# -*- coding: utf-8 -*-

#	STLIB IMPORT
from stlib.scene.wrapper import Wrapper

import sys
import os
import ntpath
import importlib

originalScene = '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/originalScene.py'

sys.path.insert(0,os.path.dirname(os.path.abspath(originalScene)))
filename, file_extension = os.path.splitext(originalScene)
importScene = str(ntpath.basename(filename))
originalScene = importlib.import_module(importScene)

# paramWrapper = [('/modelNode', {'paramForcefield': {'performECSW': True, 'RIDPath': 'data/RID_modelNode.txt', 'modesPath': 'data/test_modes.txt', 'weightsPath': 'data/weight_modelNode.txt'}, 'paramMORMapping': {'input': '@../MechanicalObject', 'modesPath': 'data/test_modes.txt'}, 'paramMappedMatrixMapping': {'object1': '@./MechanicalObject', 'object2': '@./MechanicalObject', 'listActiveNodesPath': 'data/conectivity_modelNode.txt', 'performECSW': True, 'template': 'Vec1d,Vec1d'}})]
paramWrapper = [('/modelNode', {'paramForcefield': {'periodSaveGIE': 11, 'prepareECSW': True, 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/diamond/data/test_modes.txt', 'nbTrainingSet': 128}, 'paramMORMapping': {'input': '@../MechanicalObject', 'modesPath': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/diamond/data/test_modes.txt'}, 'paramMappedMatrixMapping': {'object1': '@./MechanicalObject', 'object2': '@./MechanicalObject', 'performECSW': False, 'template': 'Vec1d,Vec1d'}})]

solverToDelete = {}
nodeToKeep = []
def findSolver(node,type,newParam,initialParam):
    global solverToDelete , nodeToKeep

    currentPath = node.getPathName()

    for item in newParam :
        index = newParam.index(item)
        path , param = item
        # print(path)
        if currentPath == path :
            if node.name in solverToDelete:
                pass
            else:
                solverToDelete[node.name] = []
            #   Find the differents solver to move them in order to have them before the MappedMatrixForceFieldAndMass
            # print(type)
            if str(type).find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
                if 'name' in initialParam:
                    solverToDelete[node.name].append(initialParam['name'])
                else: 
                    solverToDelete[node.name].append(str(type))

            if node.name not in nodeToKeep :
                nodeToKeep.append(node.name)

    return None


tmpFind = 0
def searchObjectAndDestroy(node):
    global tmpFind,nodeToKeep

    for child in node.getChildren():
        for item in paramWrapper:
            # print(item[0]+' in '+child.getPathName()+' ?')
            if child.getPathName().find(item[0]) != -1 or item[0].find(child.getPathName()) != -1 and child.getPathName() != '':
                # print('keep : '+child.name)
                if child.getPathName() ==  item[0]:

                    objects = child.getObjects()
                    for obj in objects:
                        if obj.name in solverToDelete[child.name]:
                            child.removeObject(obj)

                    if solverToDelete[child.name]:
                        child.createObject('ReadState', filename="stateFile.state") 
                    
                    childs = child.getChildren()
                    for node in childs:
                        # print(node.name)
                        subTopo = False
                        for item in paramWrapper:
                            if item[0] == child.getPathName():
                                if 'subTopo' in item[1] :
                                    if node.name == item[1]['subTopo']:
                                        subTopo = True
                        if subTopo:
                            pass
                        else:
                            child.removeChild(node)
                    tmpFind+=1

                else:
                    searchObjectAndDestroy(child) 
            elif child.getPathName() != '': 
                # print('remove : '+child.name)
                myParent = child.getParents()[0]
                myParent.removeChild(child)

    if tmpFind == len(nodeToKeep):
        print 'find all'
    # else:
    #     print 'not yet'

    return None

def createScene(rootNode):

    originalScene.createScene(Wrapper(rootNode, findSolver, paramWrapper))

    for obj in rootNode.getObjects():
        rootNode.removeObject(obj)

    # print('nodeToKeep ',nodeToKeep)
    # print('solverToDelete :',solverToDelete)
    searchObjectAndDestroy(rootNode)
    



