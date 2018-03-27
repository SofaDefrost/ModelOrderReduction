# -*- coding: utf-8 -*-
import sys
import os
import ntpath
import importlib
import sys
import numpy as np

#   STLIB IMPORT
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import MORWrapper

originalScene = 'quadruped_snapshotGeneration.py'
nbrOfModes = 78
paramWrapper = [('/model', {'paramForcefield': {'performECSW': True, 'RIDPath': 'data/RID_model.txt', 'modesPath': 'data/test_modes.txt', 'weightsPath': 'data/weight_model.txt'}, 'paramMORMapping': {'input': '@../MechanicalObject', 'modesPath': 'data/test_modes.txt'}, 'subTopo': 'modelSubTopo', 'paramMappedMatrixMapping': {'object1': '@./MechanicalObject', 'object2': '@./MechanicalObject', 'listActiveNodesPath': 'data/conectivity_model.txt', 'performECSW': True, 'template': 'Vec1d,Vec1d'}}), ('/model/modelSubTopo', {'paramForcefield': {'performECSW': True, 'RIDPath': 'data/RID_modelSubTopo.txt', 'modesPath': 'data/test_modes.txt', 'weightsPath': 'data/weight_modelSubTopo.txt'}})]

sys.path.insert(0,os.path.dirname(os.path.abspath(originalScene)))
filename, file_extension = os.path.splitext(originalScene)
importScene = str(ntpath.basename(filename))
originalScene = importlib.import_module(importScene)


modesPositionStr = '0'
for i in range(1,nbrOfModes):
    modesPositionStr = modesPositionStr + ' 0'


def MORNameExistance (name,kwargs):
    if 'name' in kwargs :
        if kwargs['name'] == name : 
            return True

solverParam = [[]]*len(paramWrapper)
containers = []
def MORreplace(node,type,newParam,initialParam):
    global solverParam

    currentPath = node.getPathName()

    for item in newParam :
        index = newParam.index(item)
        path , param = item
        
        if currentPath == path :
            # print index
            # print(type)

            # 	Find the differents solver to move them in order to have them before the MappedMatrixForceFieldAndMass
            if str(type).find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
                if 'name' in initialParam:
                    solverParam[index].append(initialParam['name'])
                else: 
                    solverParam[index].append(type)
			
            # 	Find the loader/container to be able to save elements allowing to build the connectivity file
            if str(type).find('Loader') != -1 or str(type).find('Container') != -1:
                if len(containers) != index+1 :
                    # print len(containers)
                    if 'name' in initialParam:
                        containers.append(initialParam['name'])
                    else: 
                        containers.append(type)
			#    Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
            if str(type).find('MechanicalObject') != -1:
                if 'name' in initialParam :
                    param['paramMORMapping']['output'] = '@./'+initialParam['name']
                    return (-1, -1, newParam)
                else:
                    param['paramMORMapping']['output'] = '@./MechanicalObject'
                    return (-1, -1, newParam)

            #   Find UniformMass name to be able to save to link it to the ModelOrderReductionMapping
            if str(type).find('UniformMass') != -1:
                if 'name' in initialParam :
                    param['paramMappedMatrixMapping']['mappedMass'] = '@.'+path+'/'+initialParam['name']
                    return (-1, -1, newParam)
                else:
                    param['paramMappedMatrixMapping']['mappedMass'] = '@.'+path+'/'+'UniformMass'
                    return (-1, -1, newParam)

            #	Change the initial Forcefield by the HyperReduced one with the new argument 
            if str(type).find('ForceField') != -1:
                # print str(type)
                name = 'HyperReducedFEMForceField_'+path.split('/')[-1]
                param['paramForcefield']['name'] = name
                param['paramForcefield']['nbModes'] = nbrOfModes
                param['paramForcefield']['poissonRatio'] = initialParam['poissonRatio']
                param['paramForcefield']['youngModulus'] = initialParam['youngModulus']

                #   Add to the container list  which data it has to save
                if str(type) == 'TetrahedronFEMForceField':
                    containers[-1] += '/tetrahedra'
                    return 'HyperReducedTetrahedronFEMForceField', param['paramForcefield'] , newParam
                elif str(type) == 'TriangleFEMForceField':
                    containers[-1] += '/triangles'
                    return 'HyperReducedTriangleFEMForceField', param['paramForcefield'] , newParam

    return None

tmpFind = 0
modify = []
def searchObjectAndDestroy(node,mySolver,newParam):
    global tmpFind
    global modify

    for child in node.getChildren():
        currentPath = child.getPathName()
        # print ('child Name : ',child.name)
        for item in newParam :
            index = newParam.index(item)
            path , param = item
            # path = '/'.join(tabReduced[:-1])
            # print ('path : '+path)
            # print ('currenPath : '+currentPath)
            if currentPath == path :

                if 'paramMappedMatrixMapping' in param:
                    modify.append((path,param,index,child))

                tmpFind+=1

        if tmpFind == len(paramWrapper):
            # print (modify)
            for item in modify :
                # print 'Create new child modelMOR and move node in it'
                path, param, index, child = item
                myParent = child.getParents()[0]
                modelMOR = myParent.createChild(child.name+'_MOR')
                modelMOR.createObject('MechanicalObject',template='Vec1d',position=modesPositionStr)
                modelMOR.moveChild(child)

                for obj in child.getObjects():
                    # print obj.name 
                    if obj.name in mySolver[index]:
                        # print('To move!')
                        child.removeObject(obj)
                        child.getParents()[0].addObject(obj)

                param['paramMappedMatrixMapping']['mappedForceField'] = '@.'+path+'/'+'HyperReducedFEMForceField_'+path[1:]
                if 'subTopo' in param:
                    nodeName = param['subTopo']
                    pathToLink = '@.'+path+'/'+nodeName+'/'+'HyperReducedFEMForceField_'+nodeName
                    # print pathToLink
                    param['paramMappedMatrixMapping']['mappedForceField2'] = pathToLink
                # print param['paramMappedMatrixMapping']
                modelMOR.createObject('MappedMatrixForceFieldAndMass', **param['paramMappedMatrixMapping'] )
                # print 'Create MappedMatrixForceFieldAndMass in modelMOR'

                if 'paramMORMapping' in param:      
                    child.createObject('ModelOrderReductionMapping', **param['paramMORMapping'])
                    print "Create ModelOrderReductionMapping in node"
                # else do error !!
            tmpFind += 1
            return None

        else:
            searchObjectAndDestroy(child,mySolver,newParam)	


def createScene(rootNode):
    
    originalScene.createScene(MORWrapper(rootNode, MORreplace, paramWrapper)) 
    searchObjectAndDestroy(rootNode,solverParam,paramWrapper)
