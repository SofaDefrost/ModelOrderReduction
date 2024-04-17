# -*- coding: utf-8 -*-
'''
**Functions that will be use during wrapping**

**Global Variable**

.. py:attribute:: forceFieldImplemented

    List of ForceField implemented and there associated HyperReduced one
    This will be use to *swap* forcefield during scene creation with :py:func:`.MORreplace`

.. py:attribute:: myModel

    OrderedDict that will contain:
        - has key Sofa.node.name
        - has items list of tuple (type,argument) each one coresponding to a component

.. py:attribute:: myMORModel

list of tuple (type,argument) each one coresponding to a component

.. py:attribute:: pathToUpdate


.. py:attribute:: forcefield

----------------------------------------------

**Methods**

'''
from collections import OrderedDict


forceFieldImplemented = {   'TetrahedralCorotationalFEMForceField':('HyperReducedTetrahedralCorotationalFEMForceField','tetrahedra'),
                            'TetrahedronHyperelasticityFEMForceField':('HyperReducedTetrahedronHyperelasticityFEMForceField','tetrahedra'),
                            'HexahedronFEMForceField':('HyperReducedHexahedronFEMForceField','hexahedra'),
                            'TetrahedronFEMForceField':('HyperReducedTetrahedronFEMForceField','tetrahedra'),
                            'TriangleFEMForceField':('HyperReducedTriangleFEMForceField','triangles'),
                            'RestShapeSpringsForceField':('HyperReducedRestShapeSpringsForceField','points')

                        }

myModel = OrderedDict() # Ordered dic containing has key Sofa.Node.name & has var a tuple of (Sofa_componant_type , param_solver)

myMORModel = [] # list of tuple (solver_type , param_solver)

pathToUpdate = {}

forcefield = []

tmp = 0

def modifyPath(currentPath,type,initialParam,newParam):
    '''
    **Correct wrong link induce by the change later done in the scene**

    This step isn't always needed for execution because all the DataLink are made BEFORE we change the scene with :py:func:`.modifyGraphScene`
    while the links are all correct (normally). But this way when we will "save" the scene with all the data value 
    the links will be correct.

    Also for the links to DATA (@myCoponent.myData) or DataLink poorly implemented if the link is false during initialization
    this link (string representing the path) will be lost and won't be tried again during bwdInit.
    
    To correct that, we need to update after our scene modification, the changed links. 
    We do that with :py:obj:`.pathToUpdate` 
    
    '''
    return_bool = False
    initialParam_copy = initialParam.copy()
    # print(currentPath,type)#,initialParam,newParam)
    for key , value in initialParam_copy.items():
        if isinstance(value, str):
            if '@' in value:
                # print(value)
                path , param = newParam
                # print(path)
                # print(currentPath)
                pathToObj = ''
                if path+'/' in currentPath+'/':
                    for i,nodeName in enumerate(currentPath.split('/')):
                        # print(nodeName)
                        if nodeName == path.split('/')[-1]:
                            # print('here')
                            tmp_value = currentPath.split('/')
                            tmp_value.insert(i,nodeName+'_MOR')
                            tmp_value = '/'.join(tmp_value)
                            pathToObj = tmp_value[1:]+'/'+initialParam_copy.get("name",str(type))

                    if '@../' in value and currentPath == path:

                        # print("------------> TO CHANGE 2")
                        tmp_value = value.split('/')
                        tmp_value.insert(1,'..')
                        tmp_value = '/'.join(tmp_value)
                        initialParam_copy[key] = tmp_value
                        pathToUpdate[pathToObj] = (key,tmp_value)
                        return_bool = True

                    elif value.find(path+'/') != -1 or value.find(path+'.') != -1:
                        # here if linked to node in reduction we need to add the new node we created "nodeName_MOR"
                        # only needed when trying to write a proper new scene

                        # print("------------> TO CHANGE 1")
                        for i,nodeName in enumerate(value.split('/')):
                            # print(nodeName)
                            if nodeName == path.split('/')[-1]:
                                # print('here')
                                tmp_value = value.split('/')
                                tmp_value.insert(i,nodeName+'_MOR')
                                tmp_value = '/'.join(tmp_value)
                                initialParam_copy[key] = tmp_value

                                pathToUpdate[pathToObj] = (key,tmp_value)
                                return_bool = True


                else:
                    pathToObj = currentPath[1:]+'/'+initialParam_copy.get("name",str(type))


                    if value.find(path+'/') != -1 or value.find(path+'.') != -1:
                        # here if linked to node in reduction we need to add the new node we created "nodeName_MOR"
                        # only needed when trying to write a proper new scene

                        # print("------------> TO CHANGE 1")
                        for i,nodeName in enumerate(value.split('/')):
                            # print(nodeName)
                            if nodeName == path.split('/')[-1]:
                                # print('here')
                                tmp_value = value.split('/')
                                tmp_value.insert(i,nodeName+'_MOR')
                                tmp_value = '/'.join(tmp_value)
                                initialParam_copy[key] = tmp_value

                                pathToUpdate[pathToObj] = (key,tmp_value)

                                return_bool = True

    if return_bool:
        return initialParam_copy

def MORreplace(node,type,newParam,initialParam):
    '''
    **Will replace classical ForceField by HyperReduced one**

    +--------------+-----------+--------------------------------------------------------------------------------+
    | argument     | type      | definition                                                                     |
    +==============+===========+================================================================================+
    | node         | Sofa.node | On which node the current object will be set                                   |
    +--------------+-----------+--------------------------------------------------------------------------------+
    | type         | undefined | Type of the Sofa.object                                                        |
    +--------------+-----------+--------------------------------------------------------------------------------+
    | newParam     | dic       || Contains numerous argument to modify/replace some component of the SOFA scene.|
    |              |           || *more details see* :py:class:`.ReductionParam`                                |
    +--------------+-----------+--------------------------------------------------------------------------------+
    | initialParam | dic       | Contains all the initial argument of the SOFA component being instanciated     |
    +--------------+-----------+--------------------------------------------------------------------------------+

    This function work thanks to the :py:class:`stlib.scene.Wrapper` of the
    `STLIB <https://github.com/SofaDefrost/STLIB>`_ SOFA plugin that will call this function BEFORE creating any 
    SOFA component enabling us to replace/modify the SOFA component before its creation

    This function will also, if there is *save* in the *newParam* key, save the initial component type & argument
    into 2 global variable :py:obj:`.myModel` & :py:obj:`.myMORModel` that will be used later by :py:func:`.writeGraphScene` to create a reusable component.

    We *save* our scene here with all the complications it will produce, wrong links (corrected by :py:func:`modifyPath`),
    need to differentiate components from *myModel* that will be moved in *myMORModel*, ect... 
    Because this way the component parameters are not polluted by all unnecessary *dataFields* that are initialized during creation.

    '''
    global tmp
    from  SofaRuntime import  getCategories
    currentPath = node.getPathName()
    # print('NODE : '+node.name.value)
    # print('TYPE : '+str(type))
    # print('PARAM  :'+str(newParam[0][0]) )
    save = False
    if 'save' in newParam[1]:
        save = True

    path , param = newParam
    lastNode = path.split('/')[-1]
    if path == currentPath or lastNode+'/' in currentPath :
        # print('\n')
        #   Change the initial Forcefield by the HyperReduced one with the new argument
        if "ForceField" in getCategories(type):
            # print('NODE : ' + node.name.value)
            # print('TYPE : ' + str(type))
            # print(getCategories(type))
            if type in forceFieldImplemented :
                type , valueType = forceFieldImplemented[type]
                name = 'reducedFF_'+ node.name.value + '_' + str(tmp)
                tmp += 1
                initialParam['name'] = name
                initialParam['nbModes'] = param['nbrOfModes']

                for key in param['paramForcefield']:
                    initialParam[key] = param['paramForcefield'][key]

                # We've already put the path to the "data" folder we now have to add the right file
                if param['paramForcefield'].get('performECSW') == True:
                    initialParam['RIDPath'] += name + '_RID.txt'
                    initialParam['weightsPath'] += name + '_weight.txt'


                saveParam = modifyPath(currentPath,type,initialParam,newParam)
                if save:
                    if currentPath not in myModel:
                            myModel[currentPath] = []
                    if saveParam:
                        myModel[currentPath].append((str(type),saveParam))
                    else:
                        myModel[currentPath].append((str(type),initialParam))

                forcefield.append(currentPath+'/'+initialParam.get("name",str(type)))
                # print(type, initialParam)
                return type , initialParam
            else:
                print("[WARNING]        No HyperReducedForceField exist for "+type)

        saveParam = modifyPath(currentPath,type,initialParam,newParam)

        if save:
            if currentPath == path :
                if type.find('Solver') != -1 or type == 'EulerImplicitSolver' or type == 'GenericConstraintCorrection':
                    myMORModel.append((str(type),initialParam))
                else:
                    if currentPath not in myModel:
                        myModel[currentPath] = []
                    if saveParam:
                        myModel[currentPath].append((str(type),saveParam))
                    else:
                        myModel[currentPath].append((str(type),initialParam))

            else:
                if currentPath not in myModel:
                    myModel[currentPath] = []

                if saveParam:
                    myModel[currentPath].append((str(type),saveParam))
                else:
                    myModel[currentPath].append((str(type),initialParam))
    elif save:
        saveParam = modifyPath(currentPath,type,initialParam,newParam)

        # this way we will take the path we want "to keep" and all its parents
        if newParam[1]['animationPaths']:
            for path in newParam[1]['animationPaths']:
                # If the animationPaths contain the name of the obj
                currentObjPath = currentPath + '/' + initialParam.get("name",str(type))
                if currentPath.find(path) != -1 or currentObjPath.find(path) != -1:
                    if currentPath not in myModel:
                        myModel[currentPath] = []

                    if saveParam:
                        myModel[currentPath].append((str(type),saveParam))
                    else:
                        myModel[currentPath].append((str(type),initialParam))

    modifyPath(currentPath,type,initialParam,newParam)
