# -*- coding: utf-8 -*-
import os
import sys
import imp
from collections import OrderedDict

#   STLIB IMPORT
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor.wrapper import MORWrapper
from mor.wrapper import writeScene

# Our Original Scene IMPORT
originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

# Scene parameters
nbrOfModes = $NBROFMODES
paramWrapper = $PARAMWRAPPER
toKeep = $TOKEEP
packageName = '$PACKAGENAME'



modesPositionStr = '0'
for i in range(1,nbrOfModes):
    modesPositionStr = modesPositionStr + ' 0'


myModel = OrderedDict()
myMORModel = []

def MORNameExistance (name,kwargs):
    if 'name' in kwargs :
        if kwargs['name'] == name : 
            return True

solverParam = [[]]*len(paramWrapper)
containers = []
def MORreplace(node,type,newParam,initialParam):

    currentPath = node.getPathName()

    for item in newParam :
        index = newParam.index(item)
        path , param = item
        
        if currentPath == path :
            # print index
            # print(type)

            if node.name not in myModel:
                myModel[node.name] = []

            if str(type).find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
                #Find the differents solver to move them in order to have them before the MappedMatrixForceFieldAndMassMOR
                if 'name' in initialParam:
                    solverParam[index].append(initialParam['name'])
                else: 
                    solverParam[index].append(type)
                myMORModel.append((str(type),initialParam))
            
            elif str(type).find('ForceField') != -1:
                    #Change the initial Forcefield by the HyperReduced one with the new argument 
                    # print str(type)
                    name = 'HyperReducedFEMForceField_'+path.split('/')[-1]
                    param['paramForcefield']['name'] = name
                    param['paramForcefield']['nbModes'] = nbrOfModes
                    param['paramForcefield']['poissonRatio'] = initialParam['poissonRatio']
                    param['paramForcefield']['youngModulus'] = initialParam['youngModulus']

                    #Add to the container list  which data it has to save
                    newType =''
                    if str(type) == 'TetrahedronFEMForceField':
                        containers[-1] += '/tetrahedra'
                        newType = 'HyperReducedTetrahedronFEMForceField'
                    elif str(type) == 'TriangleFEMForceField':
                        containers[-1] += '/triangles'
                        newType = 'HyperReducedTriangleFEMForceField'

                    if not newType :
                        print('!! FORCFIELD NOT IMPLEMENTED !!')
                        return -1, -1 , newParam

                    myModel[node.name].append((newType,param['paramForcefield']))
                    return newType, param['paramForcefield'] , newParam

            elif str(type).find('MechanicalObject') != -1:
                #Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
                myModel[node.name].append((str(type),initialParam))
                if 'name' in initialParam :
                    param['paramMORMapping']['output'] = '@./'+initialParam['name']
                else:
                    param['paramMORMapping']['output'] = '@./MechanicalObject'
                return (-1, -1, newParam)

            elif str(type).find('UniformMass') != -1:
                #Find UniformMass name to be able to save to link it to the ModelOrderReductionMapping
                myModel[node.name].append((str(type),initialParam))
                if 'name' in initialParam :
                    param['paramMappedMatrixMapping']['mappedMass'] = '@.'+path+'/'+initialParam['name']
                else:
                    param['paramMappedMatrixMapping']['mappedMass'] = '@.'+path+'/'+'UniformMass'
                return (-1, -1, newParam)

            else:
                if str(type).find('Loader') != -1 or str(type).find('Container') != -1:
                    #   Find the loader/container to be able to save elements allowing to build the connectivity file
                    if len(containers) != index+1 :
                        # print len(containers)
                        if 'name' in initialParam:
                            containers.append(initialParam['name'])
                        else: 
                            containers.append(type)

                myModel[node.name].append((str(type),initialParam))

    if node.name in toKeep:
        # print(node.name)
        if node.name not in myModel:
            myModel[node.name] = []
        
        myModel[node.name].append((str(type),initialParam))

    return None

tmpFind = 0
modify = []
def searchObjectAndDestroy(node,mySolver,newParam):
    global tmpFind
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
                argMecha = {'template':'Vec1d','position':modesPositionStr}
                myMORModel.append(('MechanicalObject',argMecha))
                modelMOR.createObject('MechanicalObject', **argMecha)
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
                myMORModel.append(('MappedMatrixForceFieldAndMassMOR',param['paramMappedMatrixMapping']))
                modelMOR.createObject('MappedMatrixForceFieldAndMassMOR', **param['paramMappedMatrixMapping'] )
                # print 'Create MappedMatrixForceFieldAndMassMOR in modelMOR'

                if 'paramMORMapping' in param:
                    myModel[child.name].append(('ModelOrderReductionMapping',param['paramMORMapping']))  
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
    # print('myMORModel : '+str(myMORModel)+'\n\n')
    # print('myModel : '+str(myModel)+'\n\n')

    if packageName:
        nodeName = paramWrapper[0][0].split('/')[-1]

        writeScene.writeHeader(packageName)
        modelTransform = writeScene.writeGraphScene(packageName,nodeName,myMORModel,myModel)
        writeScene.writeFooter(packageName,nodeName,modelTransform)