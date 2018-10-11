# -*- coding: utf-8 -*-

from collections import OrderedDict

forceFieldImplemented = {
                            'TetrahedronFEMForceField':('HyperReducedTetrahedronFEMForceField','tetrahedra'),
                            'TriangleFEMForceField':('HyperReducedTriangleFEMForceField','triangles'),
                            'RestShapeSpringsForceField':('HyperReducedRestShapeSpringsForceField','points')
                        }

myModel = OrderedDict() # Ordered dic containing has key Sofa.Node.name & has var a tuple of (Sofa_componant_type , param_solver)
myMORModel = [] # list of tuple (solver_type , param_solver)


tmp = 0

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
        
        if currentPath == path :
            # print(type)

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