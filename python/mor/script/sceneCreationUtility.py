# -*- coding: utf-8 -*-
from collections import OrderedDict
from splib.animation import animate

forceFieldImplemented = ['TetrahedronFEMForceField','TriangleFEMForceField']

myModel = OrderedDict() # Ordered dic containing has key Sofa.Node.name & has var a tuple of (Sofa_componant_type , param_solver)
myMORModel = [] # list of tuple (solver_type , param_solver)

class SceneCreationUtility():

    def searchInGraphScene(self,node,toFind):
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

        def search(node,toFind):

            if len(tmp.results) != len(toFind):

                for child in node.getChildren():

                    if child.name in toFind and len(tmp.results) < len(toFind):
                        tmp.results.append(child)

                    if len(tmp.results) < len(toFind):
                        search(child,toFind)

        search(node,toFind)

        if len(toFind) != len(tmp.results):
            raise Exception("ERROR haven't found all object")

        return tmp.results

    def addAnimation(self,phase,timeExe,dt,listObjToAnimate):
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

    def MORreplace(self,node,type,newParam,initialParam):

        currentPath = node.getPathName()
        # print('NODE : '+node.name)
        # print('TYPE : '+str(type))
        # print('PARAM  :'+str(newParam[0][0]) )
        save = False
        if 'save' in newParam[0][1]:
            save = True

        for item in newParam :
            index = newParam.index(item)
            path , param = item
            
            if currentPath == path :
                # print index
                # print(type)

                newType = -1

                #   Find the differents solver to move them in order to have them before the MechanicalMatrixMapperMOR
                if str(type).find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
                    if 'solver' not in param:
                        param['solver'] = [] 

                    if 'name' in initialParam:
                        param['solver'].append(initialParam['name'])
                    else: 
                        param['solver'].append(type)

                    if save:
                        myMORModel.append((str(type),initialParam))

                    return newType, initialParam , newParam


                #   Change the initial Forcefield by the HyperReduced one with the new argument 
                if str(type).find('ForceField') != -1 and str(type) in forceFieldImplemented :
                    # print str(type)
                    name = 'HyperReducedFEMForceField_'+path.split('/')[-1]
                    param['paramForcefield']['name'] = name
                    param['paramForcefield']['nbModes'] = param['nbrOfModes']
                    param['paramForcefield']['poissonRatio'] = initialParam['poissonRatio']
                    param['paramForcefield']['youngModulus'] = initialParam['youngModulus']

                    #Add to the container list  which data it has to save
                    if str(type) == 'TetrahedronFEMForceField':
                        param['loader'] += '/tetrahedra'
                        newType = 'HyperReducedTetrahedronFEMForceField'
                    elif str(type) == 'TriangleFEMForceField':
                        param['loader'] += '/triangles'
                        newType = 'HyperReducedTriangleFEMForceField'

                    if newType == -1 :
                        raise Exception("!! FORCFIELD NOT IMPLEMENTED !!")

                    if save:
                        myModel[node.name].append((newType,param['paramForcefield']))

                    return newType, param['paramForcefield'] , newParam

                elif str(type).find('MechanicalObject') != -1:
                    #Find MechanicalObject name to be able to save to link it to the ModelOrderReductionMapping
                    if save:
                        myModel[node.name].append((str(type),initialParam))

                    if 'name' in initialParam :
                        param['paramMORMapping']['output'] = '@./'+initialParam['name']
                    else:
                        param['paramMORMapping']['output'] = '@./MechanicalObject'
                    return (-1, -1, newParam)

                elif str(type).find('Loader') != -1 or str(type).find('Container') != -1:
                        if 'loader' not in param:
                            param['loader'] = None
                        if not (param['loader']):
                            # print len(containers)
                            if 'name' in initialParam:
                                param['loader'] = initialParam['name']
                            else: 
                                param['loader'] = type
                            # print ('Containers :      '+str(param['loader']))

                if save:
                    if node.name not in myModel:
                        myModel[node.name] = []
                    myModel[node.name].append((str(type),initialParam))

                return newType, initialParam , newParam

        if save:
            if node.name in newParam[0][1]['toKeep']:
                # print(node.name)
                if node.name not in myModel:
                    myModel[node.name] = []
                
                myModel[node.name].append((str(type),initialParam))


        return -1 , -1 , newParam

    def modifyGraphScene(self,nbrOfModes,nodeFound,newParam,save=False):

        modesPositionStr = '0'
        for i in range(1,nbrOfModes):
            modesPositionStr = modesPositionStr + ' 0'
        argMecha = {'template':'Vec1d','position':modesPositionStr}

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
                        modelMOR.createObject('MechanicalObject', **argMecha)
                        modelMOR.moveChild(child)

                        for obj in child.getObjects():
                            # print obj.name
                            # print ('Solver to move :  '+str(param['solver']))
                            if obj.name in param['solver']:
                                # print('To move!')
                                child.removeObject(obj)
                                child.getParents()[0].addObject(obj)

                        # print param['paramMappedMatrixMapping']
                        modelMOR.createObject('MechanicalMatrixMapperMOR', **param['paramMappedMatrixMapping'] )
                        # print 'Create MechanicalMatrixMapperMOR in modelMOR'

                        if save:
                            myMORModel.append(('MechanicalObject',argMecha))
                            myMORModel.append(('MechanicalMatrixMapperMOR',param['paramMappedMatrixMapping']))

                        if 'paramMORMapping' in param:
                            if save:
                                myModel[child.name].append(('ModelOrderReductionMapping',param['paramMORMapping']))

                            child.createObject('ModelOrderReductionMapping', **param['paramMORMapping'])
                            print ("Create ModelOrderReductionMapping in node")
                        # else do error !!

    def saveElements(self,phase,nodeFound,newParam):
        import numpy as np

        def save(node,container,valueType, **param):

            elements = container.findData(valueType).value
            np.savetxt('elmts_'+node.name+'.txt', elements,fmt='%i')
            print('save : '+'elmts_'+node.name+' from '+container.name+' with value Type '+valueType)

        for child in nodeFound :
            path = child.getPathName()
            for item in newParam :
                pathTmp , param = item
                index = newParam.index(item)
                if path == pathTmp:
                    container , valueType = param['loader'].split('/')
                    container = child.getObject(container)
                    dt = container.getContext().getDt()
                    animate(save, {"node" : child ,'container' : container, 'valueType' : valueType, 'startTime' : 0}, dt)