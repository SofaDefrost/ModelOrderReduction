# -*- coding: utf-8 -*-
import imp

#	STLIB IMPORT
from splib.animation import AnimationManager , animate
from stlib.scene.wrapper import Wrapper

# MOR IMPORT
from mor import animation
from mor.script import ObjToAnimate


# Our Original Scene IMPORT
originalScene = '$ORIGINALSCENE'
originalScene = imp.load_source(originalScene.split('/')[-1], originalScene)

# Animation parameters
listObjToAnimate = []
#for $obj in $LISTOBJTOANIMATE:
listObjToAnimate.append(ObjToAnimate('$obj.location',$obj.animFct,objName='$obj.objName',duration=$obj.duration,**$obj.params))
#end for
phase = $PHASE
nbIterations = $nbIterations
paramWrapper = $PARAMWRAPPER
# GLOBAL
timeExe = 0.0
dt = 0.0
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
        if child.name in toFind and len(tmp) < len(toFind):
            # print(child.name)
            tmp.append(child)
        if len(tmp) == len(toFind):
            tmp = tmp + [-1]
            return None
        else:
            searchInGraphScene(child,toFind)

def searchChildAndAnimate():
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
    tmpFind = 0
    for objToAnimate in listObjToAnimate:
        if phase[tmpFind] :
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

        tmpFind += 1


def createScene(rootNode):
    global timeExe, dt, tmp

    print ("Scene Phase :"+str(phase))
    originalScene.createScene(rootNode)
    tmp = []

    toAnimate = []
    for obj in listObjToAnimate:
        toAnimate.append(obj.location)

    searchInGraphScene(rootNode,toAnimate)

    nodeFound = tmp[:-1]
    if len(nodeFound) != len(listObjToAnimate):
        raise "ERROR haven't found all node to animate"
    for i in range(len(listObjToAnimate)):
        listObjToAnimate[i].node = nodeFound[i]

    dt = rootNode.dt
    timeExe = nbIterations * dt
    # print "timeExe :",timeExe

    if isinstance(rootNode, Wrapper):
        AnimationManager(rootNode.node)
    else:
        AnimationManager(rootNode)

    searchChildAndAnimate()

    toFind = []
    for item in paramWrapper:
        path, param = item
        toFind.append(path.split('/')[-1])

    tmp = []
    searchInGraphScene(rootNode,toFind)
    if tmp:
        myParent = tmp[0]
        if phase == [0]*len(phase):
            myParent.createObject('WriteState', filename="stateFile.state", period=listObjToAnimate[0].params["incrPeriod"]*dt,writeX="1", writeX0="1", writeV="0")
        else :
            myParent.createObject('WriteState', filename="stateFile.state", period=listObjToAnimate[0].params["incrPeriod"]*dt,writeX="1", writeX0="0", writeV="0")