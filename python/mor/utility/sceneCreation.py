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
from splib.animation import animate
from splib.scenegraph import *

from mor.wrapper import replaceAndSave

import yaml

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
        node = get(rootNode,obj.location)
        print(node.name)
        toAnimate.append(node)

    if len(toAnimate) != len(listObjToAnimate):
        raise Exception("All Obj/Node to animate haven't benn found")

    tmp = 0
    for objToAnimate in listObjToAnimate:
        if phase[tmp] :
            if type(toAnimate[tmp]).__name__ == "Node":
                objToAnimate.item = toAnimate[tmp]
                for obj in objToAnimate.item.getObjects():
                    # print(obj.getClassName())
                    if obj.getClassName() ==  'CableConstraint' or obj.getClassName() ==  'SurfacePressureConstraint':
                        objToAnimate.item = obj
                        objToAnimate.params["dataToWorkOn"] = 'value'

            elif type(toAnimate[tmp]).__name__ == "BaseObject":
                objToAnimate.item = toAnimate[tmp]

            if objToAnimate.item and objToAnimate.params["dataToWorkOn"]:
                objToAnimate.duration = timeExe

                animate(objToAnimate.animFct, {'objToAnimate':objToAnimate,'dt':dt}, objToAnimate.duration)
                print("Animate "+objToAnimate.location+" of type "+objToAnimate.item.getClassName()+"\nwith parameters :\n"+str(objToAnimate.params))

            else:
                print("Found Nothing to animate in "+str(objToAnimate.location))

        tmp += 1

def modifyGraphScene(rootNode,nbrOfModes,newParam,save=False):

    modesPositionStr = '0'
    for i in range(1,nbrOfModes):
        modesPositionStr = modesPositionStr + ' 0'
    argMecha = {'template':'Vec1d','position':modesPositionStr}

    for item in newParam :
        pathTmp , param = item
        node = get(rootNode,pathTmp[1:])
        solver = getNodeSolver(node)
        print("node.getPathName()",node.getPathName())
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
                    replaceAndSave.myMORModel.append(('MechanicalObject',argMecha))
                    replaceAndSave.myMORModel.append(('MechanicalMatrixMapperMOR',param['paramMappedMatrixMapping']))

                if 'paramMORMapping' in param:
                    #Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
                    param['paramMORMapping']['output'] = '@./'+node.getMechanicalState().name
                    if save:
                        replaceAndSave.myModel[node.name].append(('ModelOrderReductionMapping',param['paramMORMapping']))

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
        node = get(rootNode,pathTmp[1:])
        print(pathTmp,node)
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
        node = get(rootNode,path[1:])
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