# -*- coding: utf-8 -*-

#   STLIB IMPORT
from stlib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import MORWrapper

# Because sofa launcher create a template of our scene, we need to indicate the path to our original scene
import sys
import numpy as np

import phase1_snapshots

####################				PARAM 			  #########################

#### Run manually diamond
# modesFilePath = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/2_Modes_Options/"
# modesFileName = "test_modes.txt"
# phase = [1,1,1,1]
# nbrOfModes = 28
# periodSaveGIE = [11, 11, 11, 11]
# nbTrainingSet = 128
# myModelToMOR = "/modelNode"
##################

#### Run manually strafish
# modesFilePath = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/2_Modes_Options/"
# modesFileName = "test_modes.txt"
# phase = [1,1,1,1,1]
# nbrOfModes = 41
# periodSaveGIE = [3, 3, 3, 3, 3]
# nbTrainingSet = 50
# myModelToMOR = "/model"
##################

#### with launcher
phase = $PHASE
nbrOfModes = $NBROFMODES
periodSaveGIE = $PERIODSAVEGIE
nbTrainingSet = $NBTRAININGSET
paramWrapper = $PARAMWRAPPER
##################

# nodesToReduce =['/model','/model/modelSubTopo']

# defaultParamForcefield = {
#     'prepareECSW' : True,
#     'modesPath': modesFilePath+modesFileName,
#     'periodSaveGIE' : periodSaveGIE[0],
#     'nbModes' : nbrOfModes,
#     'nbTrainingSet' : nbTrainingSet}

# defaultParamMappedMatrixMapping = {
#     'template': 'Vec1d,Vec1d',
#     'object1': '@./MechanicalObject',
#     'object2': '@./MechanicalObject',
#     'performECSW': False}

# defaultParamMORMapping = {
#     'input': '@../MechanicalObject',
#     'modesPath': modesFilePath+modesFileName}

# paramWrapper = []
# paramWrapper.append(   (nodesToReduce[0] , 
#                        {'subTopo' : 'modelSubTopo',
#                         'paramForcefield': defaultParamForcefield.copy(),
#                         'paramMORMapping': defaultParamMORMapping.copy(),
#                         'paramMappedMatrixMapping': defaultParamMappedMatrixMapping.copy()} ) )

# paramWrapper.append(  (nodesToReduce[1] ,{'paramForcefield': defaultParamForcefield.copy()} ) )

modesPositionStr = '0'
for i in range(1,nbrOfModes):
    modesPositionStr = modesPositionStr + ' 0'

###############################################################################

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

                if phase == [1]*len(phase):
                    containerName , valueType = containers[index].split('/')
                    containerName = child.getObject(containerName)
                    dt = containerName.getContext().getDt()
                    animate(saveElements, {"node" : child ,'containerName' : containerName, 'valueType' : valueType, 'startTime' : 0}, dt)

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

def saveElements(node,containerName,valueType, **param):

    elements = containerName.findData(valueType).value
    np.savetxt('elmts_'+node.name+'.txt', elements,fmt='%i')
    print('save : '+'elmts_'+node.name+' from '+containerName.name+' with value Type '+valueType)


def createScene(rootNode):
    phase1_snapshots.createScene(MORWrapper(rootNode, MORreplace, paramWrapper)) 
    
    # print ('Solver to move : 	'+str(solverParam))
    # print ('Containers : 		'+str(containers))
    # print ('ComponentType : 	'+str(componentType))
    searchObjectAndDestroy(rootNode,solverParam,paramWrapper)