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
'''
**Utility to construct and modify a SOFA scene**


------------------------------------------------------------------
'''
import sys
import yaml

try:
    from splib3.animation import animate
    from splib3.scenegraph import *
except:
    raise ImportError("ModelOrderReduction plugin depend on SPLIB"\
                     +"Please install it : https://github.com/SofaDefrost/STLIB")

from mor.wrapper import replaceAndSave

forceFieldImplemented = {   'HyperReducedTetrahedralCorotationalFEMForceField':'tetrahedra',
                            'HyperReducedTetrahedronHyperelasticityFEMForceField':'tetrahedra',
                            'HyperReducedHexahedronFEMForceField':'hexahedra',
                            'HyperReducedTetrahedronFEMForceField':'tetrahedra',
                            'HyperReducedTriangleFEMForceField':'triangles',
                            'HyperReducedRestShapeSpringsForceField':'points'
                        }


tmp = 0

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
    for obj in node.objects:
        className = obj.getClassName()
        categories = obj.getCategories()
        solverCategories = ["ConstraintSolver","LinearSolver","OdeSolver"]
        if any(x in solverCategories for x in categories):
            solver.append(obj)
    return solver

def getContainer(node):
    container = None
    for obj in node.objects:
        className = obj.getClassName()
        if className.find('TopologyContainer') != -1:
            # print obj.getName()
            container = obj
    print(container)
    return container

def searchObjectClassInGraphScene(node,toFind):
    '''
    **Search in the Graph scene recursively for all the node
    with the same className as toFind**


    +----------+-----------+----------------------------------+
    | argument | type      | definition                       |
    +==========+===========+==================================+
    | node     | Sofa.node | Sofa node in wich we are working |
    +----------+-----------+----------------------------------+
    | toFind   | str       | className we want to find        |
    +----------+-----------+----------------------------------+

    '''
    class Namespace(object):
        pass
    tmp = Namespace()
    tmp.results = []

    if not isinstance(toFind,str):
        raise Exception("toFind is either a string or a list of string")

    def search(node,toFind):

        for obj in node.objects:
            if obj.getClassName() == toFind:
                tmp.results.append(obj)
        for child in node.children:
            search(child,toFind)

    search(node,toFind)
    return tmp.results

def searchPlugin(rootNode,pluginName):
    '''
    **Search if a plugin if used in a SOFA scene**
    '''
    found = False
    plugins = searchObjectClassInGraphScene(rootNode,"RequiredPlugin")
    print(plugins)
    for plugin in plugins:
        for name in plugin.pluginName.value:
            if name == pluginName:
                found = True
    return found

def addPlugin(rootNode,pluginName):

    if not searchPlugin(rootNode,pluginName):
        rootNode.createObject('RequiredPlugin', pluginName=pluginName)

def addAnimation(node,phase,timeExe,dt,listObjToAnimate):
    '''
    **Add/or not animations defined by** :py:class:`.ObjToAnimate` **to the** 
    :py:obj:`splib.animation.AnimationManagerController` **thanks to** :py:func:`splib.animation.animate`
    **of the** `STLIB <https://github.com/SofaDefrost/STLIB>`_ **SOFA plugin**

    +------------------+---------------------------------+----------------------------------------------------------------------------+
    | argument         | type                            | definition                                                                 |
    +==================+=================================+============================================================================+
    | node             | Sofa.node                       | from which node will search & add animation                                |
    +------------------+---------------------------------+----------------------------------------------------------------------------+
    | phase            | list(int)                       || list of 0/1 that according to its index will activate/desactivate         |
    |                  |                                 || a :py:class:`.ObjToAnimate` contained in *listObjToAnimate*               |
    +------------------+---------------------------------+----------------------------------------------------------------------------+
    | timeExe          | sc                              || correspond to the total SOFA execution duration the animation will occure,|
    |                  |                                 || determined with *nbIterations* (of :py:class:`.ReductionAnimations`)      |
    |                  |                                 || multiply by the *dt* of the current scene                                 |
    +------------------+---------------------------------+----------------------------------------------------------------------------+
    | dt               | sc                              | time step of our SOFA scene                                                |
    +------------------+---------------------------------+----------------------------------------------------------------------------+
    | listObjToAnimate | list(:py:class:`.ObjToAnimate`) | list conaining all the ObjToAnimate that will be use to shake our model    |
    +------------------+---------------------------------+----------------------------------------------------------------------------+

    Thanks to the location parameters of an :py:class:`.ObjToAnimate`, we find the component or Sofa.node it will animate.
    *If its a Sofa.node we search something to animate by default CableConstraint/SurfacePressureConstraint.*

    '''

    toAnimate = []
    for obj in listObjToAnimate:
        nodeFound = get(node,obj.location)
        # print(nodeFound.name)
        toAnimate.append(nodeFound)

    if len(toAnimate) != len(listObjToAnimate):
        raise Exception("All Obj/Node to animate haven't been found")

    tmp = 0
    for objToAnimate in listObjToAnimate:
        if phase[tmp] :
            if type(toAnimate[tmp]).__name__ == "Node":
                objToAnimate.item = toAnimate[tmp]
                for obj in objToAnimate.item.objects:
                    # print(obj.getClassName())
                    if obj.getClassName() ==  'CableConstraint' or obj.getClassName() ==  'SurfacePressureConstraint':
                        objToAnimate.item = obj
                        objToAnimate.params["dataToWorkOn"] = 'value'

            else :
                objToAnimate.item = toAnimate[tmp]

            if objToAnimate.item :
                objToAnimate.duration = timeExe

                animate(objToAnimate.animFct, {'objToAnimate':objToAnimate,'dt':dt}, objToAnimate.duration)
                print("Animate "+objToAnimate.location+" of type "+objToAnimate.item.getClassName()+"\nwith parameters :\n"+str(objToAnimate.params))

            else:
                print("Found Nothing to animate in "+str(objToAnimate.location))

        tmp += 1

def modifyGraphScene(node,nbrOfModes,newParam):
    '''
    **Modify the current scene to be able to reduce it**

    +------------+-----------+---------------------------------------------------------------------+
    | argument   | type      | definition                                                          |
    +============+===========+=====================================================================+
    | node       | Sofa.node | from which node will search & modify the graph                      |
    +------------+-----------+---------------------------------------------------------------------+
    | nbrOfModes | int       || Number of modes choosed in :py:meth:`.phase3` or :py:meth:`.phase4`|
    |            |           || where this function will be called                                 |
    +------------+-----------+---------------------------------------------------------------------+
    | newParam   | dic       || Contains numerous argument to modify/replace some component        |
    |            |           || of the SOFA scene. *more details see* :py:class:`.ReductionParam`  |
    +------------+-----------+---------------------------------------------------------------------+

    For more detailed about the modification & why they are made see here

    '''
    modesPositionStr = '0'
    for i in range(1,nbrOfModes):
        modesPositionStr = modesPositionStr + ' 0'
    argMecha = {'template':'Vec1d','position':modesPositionStr}

    save = False
    if 'save' in newParam[1]:
        save = True

    pathTmp , param = newParam
    # print('pathTmp -----------------> '+pathTmp)
    try :
        currentNode = get(node,pathTmp[1:])
        solver = getNodeSolver(currentNode)
        # print("node.getPathName()",currentNode.getPathName())
        if currentNode.getPathName() == pathTmp:
            if 'paramMappedMatrixMapping' in param:
                print('Create new child modelMOR and move node in it')
                myParent = currentNode.getParents()[0]
                modelMOR = myParent.createChild(currentNode.name+'_MOR')
                for parents in currentNode.getParents():
                    parents.removeChild(currentNode)
                modelMOR.addChild(currentNode)
                for obj in solver:
                    # print('To move!')
                    currentNode.removeObject(obj)
                    currentNode.getParents()[0].addObject(obj)
                modelMOR.createObject('MechanicalObject', **argMecha)
                # print param['paramMappedMatrixMapping']
                modelMOR.createObject('MechanicalMatrixMapperMOR', **param['paramMappedMatrixMapping'] )
                # print 'Create MechanicalMatrixMapperMOR in modelMOR'
                if save:
                    replaceAndSave.myMORModel.append(('MechanicalObject',argMecha))
                    replaceAndSave.myMORModel.append(('MechanicalMatrixMapperMOR',param['paramMappedMatrixMapping']))

                if 'paramMORMapping' in param:
                    #Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
                    param['paramMORMapping']['output'] = '@./'+currentNode.getMechanicalState().name
                    if save:
                        replaceAndSave.myModel[pathTmp].append(('ModelOrderReductionMapping',param['paramMORMapping']))

                    currentNode.createObject('ModelOrderReductionMapping', **param['paramMORMapping'])
                    print ("Create ModelOrderReductionMapping in node")
                # else do error !!
    except :
        print("Problem with path : "+pathTmp[1:])

def saveElements(node,dt,forcefield):
    '''
    **Depending on the forcefield will go search for the right kind
    of elements (tetrahedron/triangles...) to save**

    +------------+-----------+-------------------------------------------------------------------------+
    | argument   | type      | definition                                                              |
    +============+===========+=========================================================================+
    | node       | Sofa.node | from which node will search to save elements                            |
    +------------+-----------+-------------------------------------------------------------------------+
    | dt         | sc        | time step of our SOFA scene                                             |
    +------------+-----------+-------------------------------------------------------------------------+
    | forcefield | list(str) || list of path to the forcefield working on the elements we want to save |
    |            |           || see :py:obj:`.forcefield`                                              |
    +------------+-----------+-------------------------------------------------------------------------+

    After determining what to save we will add an animation with a *duration* of 0 that will
    be executed only once when the scene is launched saving the elements.

    To do that we use :py:func:`splib.animation.animate`
    **of the** `STLIB <https://github.com/SofaDefrost/STLIB>`_ **SOFA plugin**
    '''

    import numpy as np
    #print('--------------------->  Gonna Try to Save the Elements')
    def save(node,container,valueType, **param):
        global tmp
        elements = container.findData(valueType).value
        np.savetxt('reducedFF_'+ node.name + '_' + str(tmp)+'_'+valueType+'_elmts.txt', elements,fmt='%i')
        tmp += 1
        print('save : '+'elmts_'+node.name+' from '+container.name+' with value Type '+valueType)

    print('--------------------->  ',forcefield)
    for objPath in forcefield:
        nodePath = '/'.join(objPath.split('/')[:-1])
        #print(nodePath,objPath)
        #print("----------->", type(node))
        obj = get(node,objPath[1:])
        currentNode = get(node,nodePath[1:])

        if obj.getClassName() == 'HyperReducedRestShapeSpringsForceField':
            container = obj
        elif obj.getClassName() == 'HyperReducedHexahedronFEMForceField':
            container = searchObjectClassInGraphScene(currentNode,'RegularGridTopology')[0]
        else:
            container = getContainer(currentNode)
        print("0000, \n \n \n++554++--**//74+-/ \n \n \n")

        # print(container)
        if obj.getClassName() in forceFieldImplemented and container:
            valueType = forceFieldImplemented[obj.getClassName()]

            # print('--------------------->  ',valueType)
            print("1100, \n \n \n++554++--**//74+-/ \n \n \n")
            if valueType:
                animate(save, {"node" : currentNode ,'container' : container, 'valueType' : valueType, 'startTime' : 0}, 0)
                print("2200, \n \n \n++554++--**//74+-/ \n \n \n")

def createDebug(rootNode,pathToNode,stateFile="stateFile.state"):
    '''
    **Will, from our original scene, remove all unnecessary component and add a ReadState component
    in order to see what happen during** :py:meth:`.phase1` or :py:meth:`.phase3`

    +------------+-----------+--------------------------------------------------------------+
    | argument   | type      | definition                                                   |
    +============+===========+==============================================================+
    | rootNode   | Sofa.root | root node of the SOFA scene                                  |
    +------------+-----------+--------------------------------------------------------------+
    | pathToNode | str       | Path to the only node we will keep to create our debug scene |
    +------------+-----------+--------------------------------------------------------------+
    | stateFile  | str       | file that will be read by default by the ReadState component |
    +------------+-----------+--------------------------------------------------------------+

    '''
    print("---------------------------------------------------")
    node = get(rootNode,pathToNode)
    nodeName = node.name

    solver = getNodeSolver(node)
    removeObjects(solver)

    for obj in rootNode.objects:
        rootNode.removeObject(obj)

    rootNode.createObject('VisualStyle', displayFlags='showForceFields')
    rootNode.dt = 1

    for child in rootNode.children:
        rootNode.removeChild(child)

    for child in node.children:
        print(child)
        if not child.name.value in nodeName:
            # print '--------------------------> remove   '+child.name
            node.removeChild(child)

    node.createObject('ReadState', filename=stateFile)
    rootNode.addChild(node)
