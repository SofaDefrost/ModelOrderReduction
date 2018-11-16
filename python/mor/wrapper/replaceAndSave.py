# -*- coding: utf-8 -*-

from collections import OrderedDict

forceFieldImplemented = {   'HexahedronFEMForceField':('HyperReducedHexahedronFEMForceField','hexahedra'),
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
    Here we try to correct wrong link induce by the change later done in the scene
    This step isn't always needed for execution because all the DataLink are made BEFORE we change the scene
    while the links are all correct (noramlly). But this way when we will "save" the scene with all the data value 
    the links will be correct.
    Also for the links to DATA (@myCoponent.myData) or DataLink poorly implemented if the link is false during initialization
    this link (string representing the path) will be lost and won't be tried again during bwdInit.
    To correct that, we need to update after our scene modification, the changed links. We do that with pathToUpdate variable
    '''

    # print(currentPath,type)#,initialParam,newParam)
    for key , value in initialParam.iteritems():
        if isinstance(value, str):
            if '@' in value:
                # print(value)
                for path , item in newParam:
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
                                pathToObj = tmp_value[1:]+'/'+initialParam.get("name",str(type))

                        if '@../' in value and currentPath == path:

                            # print("------------> TO CHANGE 2")
                            tmp_value = value.split('/')
                            tmp_value.insert(1,'..')
                            tmp_value = '/'.join(tmp_value)
                            initialParam[key] = tmp_value
                            pathToUpdate[pathToObj] = (key,tmp_value)

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
                                    initialParam[key] = tmp_value

                                    pathToUpdate[pathToObj] = (key,tmp_value)

                    else:
                        pathToObj = currentPath[1:]+'/'+initialParam.get("name",str(type))


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
                                    initialParam[key] = tmp_value

                                    pathToUpdate[pathToObj] = (key,tmp_value)

def MORreplace(node,type,newParam,initialParam):
    global tmp
    currentPath = node.getPathName()
    # print('NODE : '+node.name)
    # print('TYPE : '+str(type))
    # print('PARAM  :'+str(newParam[0][0]) )
    save = False
    if 'save' in newParam[0][1]:
        save = True

    for item in newParam :
        path , param = item
        # print(currentPath,path)
        if path in currentPath :
            # print('\n')

            #   Change the initial Forcefield by the HyperReduced one with the new argument 
            if str(type) in forceFieldImplemented :
                type , valueType = forceFieldImplemented[type]
                # print str(type)

                name = 'reducedFF_'+ node.name + '_' + str(tmp)
                tmp += 1    
                initialParam['name'] = name
                initialParam['nbModes'] = param['nbrOfModes']
                
                for key in param['paramForcefield']:
                    initialParam[key] = param['paramForcefield'][key]
                
                # We've already put the path to the "data" folder we now have to add the right file
                if param['paramForcefield'].get('performECSW') == True: 
                    initialParam['RIDPath'] += name + '_RID.txt'
                    initialParam['weightsPath'] += name + '_weight.txt'


                if save:
                    # print("------------------> ",currentPath)
                    if currentPath == path:
                        if currentPath not in myModel:
                            myModel[currentPath] = []
                        myModel[currentPath].append((str(type),initialParam))
                    elif currentPath[1:] in newParam[0][1]['toKeep']:
                        if currentPath not in myModel:
                            myModel[currentPath] = []

                        myModel[currentPath].append((str(type),initialParam))
                forcefield.append(currentPath+'/'+initialParam.get("name",str(type)))
                modifyPath(currentPath,type,initialParam,newParam)
                return type , initialParam

            elif currentPath == path and save:
                if type.find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
                    myMORModel.append((str(type),initialParam))
                else:
                    if currentPath not in myModel:
                        myModel[currentPath] = []
                    myModel[currentPath].append((str(type),initialParam))

    if save:
        # this way we will take the path we want "to keep" and all its parents
        if currentPath[1:] in newParam[0][1]['toKeep']:
            if currentPath not in myModel:
                myModel[currentPath] = []

            myModel[currentPath].append((str(type),initialParam))

        # we don't keep all the children of the node we are reducing, the user as to choose them
        # elif path in currentPath: # By default will take all the children of the node we are reducing
        #     if node.name not in myModel:
        #         myModel[currentPath] = []

        #     myModel[currentPath].append((str(type),initialParam))

    modifyPath(currentPath,type,initialParam,newParam)
