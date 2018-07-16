# -*- coding: utf-8 -*-
import sys
import numpy as np

#   STLIB IMPORT
from splib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import MORWrapper

# Our Phase1 Scene IMPORT
import phase1_snapshots

# Scene parameters
phase = $PHASE
nbrOfModes = $NBROFMODES
periodSaveGIE = $PERIODSAVEGIE
nbTrainingSet = $NBTRAININGSET
paramWrapper = $PARAMWRAPPER


forceFieldImplemented = ['TetrahedronFEMForceField','TriangleFEMForceField']

modesPositionStr = '0'
for i in range(1,nbrOfModes):
    modesPositionStr = modesPositionStr + ' 0'

###############################################################################
tmp = []
def searchInGraphScene(node,toFind):
    '''
        Args:
        node (Sofa.node):     Sofa node in wich we are working

        toFind (list[str]):  list of node name we want to find

        Description:

            Search in the Graph scene recursively for all the node
            with name contained in the list toFind
    '''
    global tmp
    for child in node.getChildren():
        # print(child.name)
        if child.getPathName() in toFind and len(tmp) < len(toFind):
            # print(child.name)
            tmp.append(child)
        if len(tmp) == len(toFind):
            tmp = tmp + [-1]
            return None
        else:
            searchInGraphScene(child,toFind)


def MORNameExistance (name,kwargs):
    if 'name' in kwargs :
        if kwargs['name'] == name : 
            return True

solverParam = [[]]*len(paramWrapper)
containers = []
def MORreplace(node,type,newParam,initialParam):
    global solverParam

    currentPath = node.getPathName()
    # print('NODE : '+node.name)
    # print('TYPE : '+str(type))
    # print('PARAM  :'+str(newParam[0][0]) )

    for item in newParam :
        index = newParam.index(item)
        path , param = item
        
        if currentPath == path :
            # print index
            # print(type)

            # 	Find the differents solver to move them in order to have them before the MappedMatrixForceFieldAndMassMOR
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

            #	Change the initial Forcefield by the HyperReduced one with the new argument 
            if str(type).find('ForceField') != -1 and str(type) in forceFieldImplemented :
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


def modifyGraphScene(nodeFound,mySolver,newParam):

    if phase == [0]*len(phase):
        for child in nodeFound :
            path = child.getPathName()
            for item in newParam :
                pathTmp , param = item
                index = newParam.index(item)
                if path == pathTmp:
                    containerName , valueType = containers[index].split('/')
                    containerName = child.getObject(containerName)
                    dt = containerName.getContext().getDt()
                    animate(saveElements, {"node" : child ,'containerName' : containerName, 'valueType' : valueType, 'startTime' : 0}, dt)

    for child in nodeFound :
        path = child.getPathName()

        for item in newParam :
            pathTmp , param = item
            index = newParam.index(item)
            if path == pathTmp:
                if 'paramMappedMatrixMapping' in param:
                    # print 'Create new child modelMOR and move node in it'

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

                    # print param['paramMappedMatrixMapping']
                    modelMOR.createObject('MappedMatrixForceFieldAndMassMOR', **param['paramMappedMatrixMapping'] )
                    # print 'Create MappedMatrixForceFieldAndMassMOR in modelMOR'

                    if 'paramMORMapping' in param:
                        child.createObject('ModelOrderReductionMapping', **param['paramMORMapping'])
                        print "Create ModelOrderReductionMapping in node"
                    # else do error !!


def saveElements(node,containerName,valueType, **param):

    elements = containerName.findData(valueType).value
    np.savetxt('elmts_'+node.name+'.txt', elements,fmt='%i')
    print('save : '+'elmts_'+node.name+' from '+containerName.name+' with value Type '+valueType)


def createScene(rootNode):
    phase1_snapshots.createScene(MORWrapper(rootNode, MORreplace, paramWrapper)) 
    
    # print ('Solver to move : 	'+str(solverParam))
    # print ('Containers : 		'+str(containers))
    # print ('ComponentType : 	'+str(componentType))
    toFind = []
    for item in paramWrapper:
        path, param = item
        toFind.append(path)

    searchInGraphScene(rootNode,toFind)

    nodeFound = tmp[:-1]

    modifyGraphScene(nodeFound,solverParam,paramWrapper)