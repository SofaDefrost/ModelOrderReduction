# -*- coding: utf-8 -*-

from collections import OrderedDict

forceFieldImplemented = ['TetrahedronFEMForceField','TriangleFEMForceField']

myModel = OrderedDict() # Ordered dic containing has key Sofa.Node.name & has var a tuple of (Sofa_componant_type , param_solver)
myMORModel = [] # list of tuple (solver_type , param_solver)


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