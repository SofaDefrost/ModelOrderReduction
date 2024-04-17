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
"""
**Utility to construct and modify a SOFA scene**

"""

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

import Sofa
import numpy as np

tmp = 0


def removeObject(obj):
    '''
    From a :class:`sofaPy3:Sofa.Core.Object` get :class:`sofaPy3:Sofa.Core.BaseContext` and remove itself :meth:`sofaPy3:Sofa.Core.Node.removeObject`

    +----------+-----------------------------------+--------------------------------------------------------------+
    | argument | type                              | definition                                                   |
    +==========+===================================+==============================================================+
    | obj      | :class:`sofaPy3:Sofa.Core.Object` | Base class for components which can be added in a simulation |
    +----------+-----------------------------------+--------------------------------------------------------------+

    :return: None
    '''
    obj.getContext().removeObject(obj)

def removeObjects(objects):
    '''
    Iterate over list of :class:`sofaPy3:Sofa.Core.Object` and remove them with :func:`removeObject`

    +----------+-----------------------------------------+--------------------------------------------------------------+
    | argument | type                                    | definition                                                   |
    +==========+=========================================+==============================================================+
    | objects  | list(:class:`sofaPy3:Sofa.Core.Object`) | Base class for components which can be added in a simulation |
    +----------+-----------------------------------------+--------------------------------------------------------------+

    :return: None
    '''
    for obj in objects :
        removeObject(obj)

def removeNode(node):
    '''
    From a :class:`sofaPy3:Sofa.Core.Node` get its first parent and remove :meth:`sofaPy3:Sofa.Core.Node.removeChild`

    +----------+-----------------------------------+--------------------------------------------------------------+
    | argument | type                              | definition                                                   |
    +==========+===================================+==============================================================+
    | node     | :class:`sofaPy3:Sofa.Core.Node`   | A Node stores other nodes and components                     |
    +----------+-----------------------------------+--------------------------------------------------------------+

    :return: None
    '''
    myParent = node.getParents()[0]
    myParent.removeChild(node)

def removeNodes(nodes):
    '''
    Iterate over list of :class:`sofaPy3:Sofa.Core.Node` and remove them with :func:`removeNode`

    +----------+-----------------------------------------+--------------------------------------------------------------+
    | argument | type                                    | definition                                                   |
    +==========+=========================================+==============================================================+
    | nodes    | list(:class:`sofaPy3:Sofa.Core.Node`)   | A Node stores other nodes and components                     |
    +----------+-----------------------------------------+--------------------------------------------------------------+

    :return: None
    '''
    for node in nodes:
        removeChild(node)

def getNodeSolver(node):
    '''
    Get specific Solver if contained in :class:`sofaPy3:Sofa.Core.Node`.

    +----------+-----------------------------------+--------------------------------------------------------------+
    | argument | type                              | definition                                                   |
    +==========+===================================+==============================================================+
    | node     | :class:`sofaPy3:Sofa.Core.Node`   | A Node stores other nodes and components                     |
    +----------+-----------------------------------+--------------------------------------------------------------+

    searching for ConstraintSolver, LinearSolver and OdeSolver solvers

    :return: list of solvers found
    '''
    solver = []
    for obj in node.objects:
        className = obj.getClassName()
        if(className !="MeshTopology"):
            categories = obj.getCategories()

            solverCategories = ["ConstraintSolver","LinearSolver","OdeSolver"]
            if any(x in solverCategories for x in categories):
                solver.append(obj)

    return solver

def getContainer(node):
    '''
    Search for **TopologyContainer** and return it

    +----------+-----------------------------------+--------------------------------------------------------------+
    | argument | type                              | definition                                                   |
    +==========+===================================+==============================================================+
    | node     | :class:`sofaPy3:Sofa.Core.Node`   | A Node stores other nodes and components                     |
    +----------+-----------------------------------+--------------------------------------------------------------+

    :return: TopologyContainer object
    '''
    container = None
    for obj in node.objects:
        className = obj.getClassName()
        if className.find('TopologyContainer') != -1:
            return obj
        if className.find('MeshTopology') != -1:
            return obj
        if className.find('RegularGridTopology') != -1:
            return obj

def searchObjectClassInGraphScene(node,toFind):
    '''
    **Search in the Graph scene recursively for all the node
    with the same className as toFind**


    +----------+----------------------------------+----------------------------------+
    | argument | type                             | definition                       |
    +==========+==================================+==================================+
    | node     | :class:`sofaPy3:Sofa.Core.Node`  | Sofa node in wich we are working |
    +----------+----------------------------------+----------------------------------+
    | toFind   | str                              | className we want to find        |
    +----------+----------------------------------+----------------------------------+

    :return: results of search in tab
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

    +------------+---------------------------------+------------------------+
    | argument   | type                            | definition             |
    +============+=================================+========================+
    | rootNode   | :class:`sofaPy3:Sofa.Core.Node` | root of scene          |
    +------------+---------------------------------+------------------------+
    | pluginName | str                             | literal name of plugin |
    +------------+---------------------------------+------------------------+

    :return: found boolean
    '''
    found = False
    plugins = searchObjectClassInGraphScene(rootNode,"RequiredPlugin")
    for plugin in plugins:
        for name in plugin.pluginName.value:
            if name == pluginName:
                found = True
    return found

def addPlugin(rootNode,pluginName):
    '''
    **Add plugin if not present in Sofa scene**

    +------------+---------------------------------+------------------------+
    | argument   | type                            | definition             |
    +============+=================================+========================+
    | rootNode   | :class:`sofaPy3:Sofa.Core.Node` | root of scene          |
    +------------+---------------------------------+------------------------+
    | pluginName | str                             | literal name of plugin |
    +------------+---------------------------------+------------------------+

    Search for it with :func:`searchPlugin` and depending if returned boolean add it or not to current scene

    :return: found boolean
    '''
    if not searchPlugin(rootNode,pluginName):
        rootNode.addObject('RequiredPlugin', pluginName=pluginName)

def addAnimation(node,phase,timeExe,dt,listObjToAnimate):
    '''
    **Add/or not animations defined by** :py:class:`.ObjToAnimate` **to the**
    :obj:`stlib:splib.animation.AnimationManagerController` **thanks to** :func:`stlib:splib.animation.animate`

    +------------------+-----------------------------------------------------+----------------------------------------------------------------------------+
    | argument         | type                                                | definition                                                                 |
    +==================+=====================================================+============================================================================+
    | node             | :class:`sofaPy3:Sofa.Core.Node`                     | from which node will search & add animation                                |
    +------------------+-----------------------------------------------------+----------------------------------------------------------------------------+
    | phase            | list(int)                                           || list of 0/1 that according to its index will activate/desactivate         |
    |                  |                                                     || a :py:class:`.ObjToAnimate` contained in *listObjToAnimate*               |
    +------------------+-----------------------------------------------------+----------------------------------------------------------------------------+
    | timeExe          | sc                                                  || correspond to the total SOFA execution duration the animation will occure,|
    |                  |                                                     || determined with *nbIterations* (of :py:class:`.ReductionAnimations`)      |
    |                  |                                                     || multiply by the *dt* of the current scene                                 |
    +------------------+-----------------------------------------------------+----------------------------------------------------------------------------+
    | dt               | sc                                                  | time step of our SOFA scene                                                |
    +------------------+-----------------------------------------------------+----------------------------------------------------------------------------+
    | listObjToAnimate | list(:class:`mor.reduction.container.objToAnimate`) | list conaining all the ObjToAnimate that will be use to shake our model    |
    +------------------+-----------------------------------------------------+----------------------------------------------------------------------------+

    Thanks to the location parameters of an :py:class:`.ObjToAnimate`, we find the component or Sofa.node it will animate.
    *If its a Sofa.node we search something to animate by default CableConstraint/SurfacePressureConstraint.*

    :return: None
    '''

    toAnimate = []
    for obj in listObjToAnimate:
        nodeFound = get(node,obj.location)
        toAnimate.append(nodeFound)

    if len(toAnimate) != len(listObjToAnimate):
        raise Exception("All Obj/Node to animate haven't been found")

    tmp = 0
    for objToAnimate in listObjToAnimate:
        if phase[tmp] :
            if type(toAnimate[tmp]).__name__ == "Node":
                objToAnimate.item = toAnimate[tmp]
                for obj in objToAnimate.item.objects:
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

    +------------+---------------------------------+---------------------------------------------------------------------------------+
    | argument   | type                            | definition                                                                      |
    +============+=================================+=================================================================================+
    | node       | :class:`sofaPy3:Sofa.Core.Node` | from which node will search & modify the graph                                  |
    +------------+---------------------------------+---------------------------------------------------------------------------------+
    | nbrOfModes | int                             || Number of modes choosed in :meth:`mor.reduction.reduceModel.ReduceModel.phase3`|
    |            |                                 || or :meth:`mor.reduction.reduceModel.ReduceModel.phase4`                        |
    |            |                                 || where this function will be called                                             |
    +------------+---------------------------------+---------------------------------------------------------------------------------+
    | newParam   | dic                             || Contains numerous argument to modify/replace some component                    |
    |            |                                 || of the SOFA scene. *more details see* :py:class:`.ReductionParam`              |
    +------------+---------------------------------+---------------------------------------------------------------------------------+

    For more detailed about the modification & why they are made see here

    :return: None
    :raises:
        Exception: cannot modify scene from path
    '''
    modesPositionStr = '0'
    for i in range(1,nbrOfModes):
        modesPositionStr = modesPositionStr + ' 0'
    argMecha = {'template':'Vec1d','position':modesPositionStr}

    save = False
    if 'save' in newParam[1]:
        save = True

    pathTmp , param = newParam

    try :
        currentNode = get(node,pathTmp[1:])
        solver = getNodeSolver(currentNode)
        print("SOLVER",solver)
        if currentNode.getPathName() == pathTmp:
            if 'prepareECSW' in param['paramForcefield'] or 'performECSW' in param['paramForcefield'] :
                print('Create new child modelMOR and move node in it')
                myParents = list(currentNode.parents)
                modelMOR = Sofa.Core.Node(currentNode.name.value+'_MOR')
                for parent in myParents:
                    parent.removeChild(currentNode)
                    parent.addChild(modelMOR)

                modelMOR.addChild(currentNode)

                if len(solver)>0:
                    for obj in solver:
                        currentNode.removeObject(obj)
                        modelMOR.addObject(obj)

                modelMOR.addObject('MechanicalObject', **argMecha)

                if save:
                    replaceAndSave.myMORModel.append(('MechanicalObject',argMecha))

                if 'paramMORMapping' in param:
                    #Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
                    param['paramMORMapping']['output'] = '@./'+currentNode.getMechanicalState().name.value
                    if save:
                        replaceAndSave.myModel[pathTmp].append(('ModelOrderReductionMapping',param['paramMORMapping']))

                    currentNode.addObject('ModelOrderReductionMapping', **param['paramMORMapping'])
                    print ("Create ModelOrderReductionMapping in node")
                # else do error !!
    except :
        print("[ERROR]    In modifyGraphScene , cannot modify scene from path : "+pathTmp[1:])

def createDebug(rootNode,pathToNode,stateFile="stateFile.state"):
    '''
    **Will, from our original scene, remove all unnecessary component and add a ReadState component
    in order to see what happen during** :py:meth:`.phase1` or :py:meth:`.phase3`

    +------------+---------------------------------+--------------------------------------------------------------+
    | argument   | type                            | definition                                                   |
    +============+=================================+==============================================================+
    | rootNode   | :class:`sofaPy3:Sofa.Core.Node` | root node of the SOFA scene                                  |
    +------------+---------------------------------+--------------------------------------------------------------+
    | pathToNode | str                             | Path to the only node we will keep to create our debug scene |
    +------------+---------------------------------+--------------------------------------------------------------+
    | stateFile  | str                             | file that will be read by default by the ReadState component |
    +------------+---------------------------------+--------------------------------------------------------------+

    :return: None
    '''
    node = get(rootNode,pathToNode)
    nodeName = node.name

    solver = getNodeSolver(node)
    removeObjects(solver)

    for obj in rootNode.objects:
        rootNode.removeObject(obj)

    rootNode.addObject('VisualStyle', displayFlags='showForceFields')
    rootNode.dt = 1

    for child in rootNode.children:
        rootNode.removeChild(child)

    for child in node.children:
        if not child.name.value in nodeName:
            node.removeChild(child)

    node.addObject('ReadState', filename=stateFile)
    rootNode.addChild(node)
