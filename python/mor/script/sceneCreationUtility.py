# -*- coding: utf-8 -*-
###############################################################################
#            Model Order Reduction plugin for SOFA                            #
#                         version 1.0                                         #
#                       Copyright © Inria                                     #
#                       All rights reserved                                   #
#                       2018                                                  #
#                                                                             #
# This software is under the GNU General Public License v2 (GPLv2)            #
#            https://www.gnu.org/licenses/licenses.en.html                    #
#                                                                             #
#                                                                             #
#                                                                             #
# Authors: Olivier Goury, Felix Vanneste                                      #
#                                                                             #
# Contact information: https://project.inria.fr/modelorderreduction/contact   #
###############################################################################
from collections import OrderedDict
from splib.animation import animate

forceFieldImplemented = ['TetrahedronFEMForceField','TriangleFEMForceField']

myModel = OrderedDict() # Ordered dic containing has key Sofa.Node.name & has var a tuple of (Sofa_componant_type , param_solver)
myMORModel = [] # list of tuple (solver_type , param_solver)


def searchNodeInGraphScene(node,toFind):
    '''
        Args:
        node (Sofa.node):     Sofa node in wich we are working

        toFind (list[str]):  list of node name we want to find

        Description:

            Search in the Graph scene recursively for all the node
            with name contained in the list toFind
    '''
    class Namespace(object):
        pass
    tmp = Namespace()
    tmp.results = []

    returnString = False
    if isinstance(toFind,str):
        toFind = [toFind]
        returnString = True
    elif isinstance(toFind,list):
        pass
    else:
        raise Exception("toFind is either a string or a list of string")

    def search(node,toFind):

        if len(tmp.results) != len(toFind):

            for child in node.getChildren():

                if child.name in toFind and len(tmp.results) < len(toFind):
                    tmp.results.append(child)

                if len(tmp.results) < len(toFind):
                    search(child,toFind)

    search(node,toFind)

    if len(toFind) != len(tmp.results):
        raise Exception("ERROR haven't found all Node")

    if returnString:
        return tmp.results[0]
    else:
        return tmp.results

def searchObjectInGraphScene(node,toFind):
    '''
        Args:
        node (Sofa.node):     Sofa node in wich we are working

        toFind (list[str]):  list of node name we want to find

        Description:

            Search in the Graph scene recursively for all the node
            with name contained in the list toFind
    '''
    class Namespace(object):
        pass
    tmp = Namespace()
    tmp.results = []

    if isinstance(toFind,str):
        toFind = [toFind]
    elif isinstance(toFind,list):
        pass
    else:
        raise Exception("toFind is either a string or a list of string")

    def search(node,toFind):

        if len(tmp.results) != len(toFind):

            for obj in node.getObjects():
                if obj.getName() in toFind and len(tmp.results) < len(toFind):
                    tmp.results.append(obj)

            if len(tmp.results) < len(toFind):
                for child in node.getChildren():

                    search(child,toFind)

    search(node,toFind)

    if len(toFind) != len(tmp.results):
        raise Exception("ERROR haven't found all Object")

    if len(toFind) == 1:
        return tmp.results[0]
    else:
        return tmp.results

def removeObject(obj):
    obj.getContext().removeObject(obj)

def removeObjects(objects):
    for obj in objects :
        removeObject(obj)

def removeNode(node):
    myParent = node.getParents()[0]
    myParent.removeChild(node)

def removeNodes(nodes):
    for node in nodes:
        removeChild(node)

def getNodeSolver(node):
    solver = []
    for obj in node.getObjects():
        className = obj.getClassName()
        if className.find('Solver') != -1 or className == 'EulerImplicit' or className == 'GenericConstraintCorrection':
            # print obj.getName()
            solver.append(obj)
    return solver

def getContainer(node):
    container = None
    for obj in node.getObjects():
        className = obj.getClassName()
        if className.find('Container') != -1: # className.find('Loader') != -1 or
            # print obj.getName()
            container = obj
    return container

def addAnimation(rootNode,phase,timeExe,dt,listObjToAnimate):
    '''
        FOR all node find to animate animate only the one moving -> phase 1/0

        If DEFAULT :
          - SEARCH here for the obj to animate & its valueToIncrement
        Else :
          - GIVE obj name to work with & its valueToIncrement

        give to animate :
          - the obj to work with & its valueToIncrement
          if DEFAULT :
              - the animation function will be defaultShaking
              - the general param lis(range,period,increment)
          else :
              - give the new animation function
              - param lis(...)
    '''
    # Search node to animate

    toAnimate = []
    for obj in listObjToAnimate:
        toAnimate.append(obj.location)

    nodeFound = searchNodeInGraphScene(rootNode,toAnimate)

    for i in range(len(listObjToAnimate)):
        listObjToAnimate[i].node = nodeFound[i]


    tmp = 0
    for objToAnimate in listObjToAnimate:
        if phase[tmp] :
            # param = listParam.copy()
            for obj in objToAnimate.node.getObjects():
                if objToAnimate.objName == '':
                    if obj.getClassName() ==  'CableConstraint' or obj.getClassName() ==  'SurfacePressureConstraint':
                        objToAnimate.obj = obj
                        objToAnimate.params["dataToWorkOn"] = 'value'

                elif obj.getClassName() == objToAnimate.objName:
                    objToAnimate.obj = obj

            if objToAnimate.obj and objToAnimate.params["dataToWorkOn"]:
                objToAnimate.duration = timeExe

                animate(objToAnimate.animFct, {'objToAnimate':objToAnimate,'dt':dt}, objToAnimate.duration)
                print("Animate "+objToAnimate.obj.getClassName()+" from node "+objToAnimate.node.name+"\nwith parameters :\n"+str(objToAnimate.params))

            else:
                print("Found Nothing to animate in "+str(objToAnimate.node.name))

        tmp += 1

def MORreplace(node,type,newParam,initialParam):

    currentPath = node.getPathName()
    # print('NODE : '+node.name)
    # print('TYPE : '+str(type))
    # print('PARAM  :'+str(newParam[0][0]) )
    save = False
    if 'save' in newParam[0][1]:
        save = True

    for item in newParam :
        path , param = item
        
        if currentPath == path :
            # print(type)

            #   Change the initial Forcefield by the HyperReduced one with the new argument 
            if str(type).find('ForceField') != -1 and str(type) in forceFieldImplemented :
                # print str(type)
                import random
                name = 'HyperReducedFEMForceField_'+ node.name #str(random.randint(0, 20))
                initialParam['name'] = name
                initialParam['nbModes'] = param['nbrOfModes']
                for key in param['paramForcefield']:
                    initialParam[key] = param['paramForcefield'][key]

                #Add to the container list  which data it has to save
                if str(type) == 'TetrahedronFEMForceField':
                    type = 'HyperReducedTetrahedronFEMForceField'
                elif str(type) == 'TriangleFEMForceField':
                    type = 'HyperReducedTriangleFEMForceField'
                elif str(type) == 'RestShapeSpringsForceField':
                    type = 'HyperReducedRestShapeSpringsForceField'
                else:
                    raise Exception("!! FORCFIELD NOT IMPLEMENTED !!")

                if save:
                    myModel[node.name].append((str(type),initialParam))

                return type , initialParam

            elif save:
                if type.find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
                    myMORModel.append((str(type),initialParam))
                else:
                    if node.name not in myModel:
                        myModel[node.name] = []
                    myModel[node.name].append((str(type),initialParam))

    if save:
        if node.name in newParam[0][1]['toKeep']:
            # print(node.name)
            if node.name not in myModel:
                myModel[node.name] = []

            myModel[node.name].append((str(type),initialParam))

def modifyGraphScene(rootNode,nbrOfModes,newParam,save=False):

    modesPositionStr = '0'
    for i in range(1,nbrOfModes):
        modesPositionStr = modesPositionStr + ' 0'
    argMecha = {'template':'Vec1d','position':modesPositionStr}

    for item in newParam :
        pathTmp , param = item
        node = searchNodeInGraphScene(rootNode,pathTmp.split('/')[-1])
        solver = getNodeSolver(node)

        if node.getPathName() == pathTmp:
            if 'paramMappedMatrixMapping' in param:
                # print 'Create new child modelMOR and move node in it'

                myParent = node.getParents()[0]
                modelMOR = myParent.createChild(node.name+'_MOR')
                modelMOR.createObject('MechanicalObject', **argMecha)
                modelMOR.moveChild(node)

                for obj in solver:
                    # print('To move!')
                    node.removeObject(obj)
                    node.getParents()[0].addObject(obj)

                # print param['paramMappedMatrixMapping']
                modelMOR.createObject('MechanicalMatrixMapperMOR', **param['paramMappedMatrixMapping'] )
                # print 'Create MechanicalMatrixMapperMOR in modelMOR'

                if save:
                    myMORModel.append(('MechanicalObject',argMecha))
                    myMORModel.append(('MechanicalMatrixMapperMOR',param['paramMappedMatrixMapping']))

                if 'paramMORMapping' in param:
                    #Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
                    param['paramMORMapping']['output'] = '@./'+node.getMechanicalState().name
                    if save:
                        myModel[node.name].append(('ModelOrderReductionMapping',param['paramMORMapping']))

                    node.createObject('ModelOrderReductionMapping', **param['paramMORMapping'])
                    print ("Create ModelOrderReductionMapping in node")
                # else do error !!

def saveElements(rootNode,phase,newParam):
    import numpy as np

    def save(node,container,valueType, **param):

        elements = container.findData(valueType).value
        np.savetxt('elmts_'+node.name+'.txt', elements,fmt='%i')
        print('save : '+'elmts_'+node.name+' from '+container.name+' with value Type '+valueType)

    for item in newParam :
        pathTmp , param = item
        index = newParam.index(item)
        node = searchNodeInGraphScene(rootNode,pathTmp.split('/')[-1])

        if node.getPathName() == pathTmp:
            
            forcefield = []
            tmp = node.getForceField(0)
            i = 0
            while tmp != None:
                forcefield.append(tmp)
                i += 1
                tmp = node.getForceField(i)


            container = getContainer(node)
            dt = container.getContext().getDt()

            # print('--------------------->  ',forcefield)

            for obj in forcefield:
                # print('--------------------->  '+obj.getName())
                className = obj.getClassName()
                if className == 'HyperReducedTetrahedronFEMForceField':
                    valueType = 'tetrahedra'
                elif className == 'HyperReducedTriangleFEMForceField':
                    valueType = 'triangles'
                elif className == 'HyperReducedRestShapeSpringsForceField':
                    valueType = 'points'
                else:
                    valueType = None

                # print('--------------------->  ',valueType)

                if valueType:
                    animate(save, {"node" : node ,'container' : container, 'valueType' : valueType, 'startTime' : 0}, dt)

def createDebug(rootNode,paramWrapper,stateFile="stateFile.state"):

    nodeName = []
    nodes = []
    for item in paramWrapper :
        path , param = item
        node = searchNodeInGraphScene(rootNode,path.split('/')[-1])
        # print node.name
        solver = getNodeSolver(node)
        removeObjects(solver)

        nodeName.append(node.name)
        nodes.append(node)


    for obj in rootNode.getObjects():
        rootNode.removeObject(obj)

    rootNode.createObject('VisualStyle', displayFlags='showForceFields')
    rootNode.dt = 1

    for child in rootNode.getChildren():
        rootNode.removeChild(child)

    for node in nodes:
        for child in node.getChildren():
            if not (child.name in nodeName):
                # print '--------------------------> remove   '+child.name
                node.removeChild(child)

    nodes[0].createObject('ReadState', filename=stateFile)
    rootNode.addChild(nodes[0])