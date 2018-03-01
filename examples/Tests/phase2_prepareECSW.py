# -*- coding: utf-8 -*-

from pprint import pprint

from stlib.scene.wrapper import Wrapper
    
# Because sofa launcher create a template of our scene, we need to indicate the path to our original scene
import sys
sys.path.insert(0,'/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests')

import phase1_snapshots

####################				PARAM 			  #########################
modesFilePath = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/2_Modes_Options/"
modesFileName = "test_modes.txt"

pathToWeightsAndRIDdir = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/3_Reduced_Model/"
RIDFileName = 'test_RID.txt'
weightsFileName = 'test_weight.txt' 

paramForcefield = {
	'name' : 'myHyperForceField',
	'prepareECSW' : True,
	'modesPath': modesFilePath+modesFileName,
	'poissonRatio': 0.45,
	'youngModulus': 450,
	'nbTrainingSet' : 200}

paramMappedMatrixMapping = {
	'template': 'Vec1d,Vec1d',
	'object1': '@./MechanicalObject',
	'object2': '@./MechanicalObject',
	'mappedForceField':'@./modelNode/myHyperForceField',
	'mappedMass': '@./modelNode/UniformMass',
	'performECSW': False}

paramMORMapping = {
	'input': '@../MechanicalObject',
    'output': '@./MechanicalObject',
    'modesPath': modesFilePath+modesFileName}

paramWrapper = {
	"/modelNode/TetrahedronFEMForceField" : {
						'componentType': 'HyperReducedTetrahedronFEMForceField',
						'paramForcefield': paramForcefield,
						'paramMORMapping': paramMORMapping,
						'paramMappedMatrixMapping': paramMappedMatrixMapping}
	}

modesPositionStr = '0'
nbrOfNode = 34

for i in range(1,nbrOfNode):
    modesPositionStr = modesPositionStr + ' 0'

###############################################################################

def MORNameExistance (name,kwargs):
    if 'name' in kwargs :
        if kwargs['name'] == name : 
        	return True

def MORreplace(node,type,newParam,initialParam):
	solverParam = []
	currentPath = node.getPathName()

	for key in newParam :
		tabReduced = key.split('/')
		path = '/'.join(tabReduced[:-1])
		# print ('tabReduced : ',tabReduced)
		# print ('path : '+path)
		# print ('currenPath : '+currentPath)
		if currentPath == path :
			print type
			if str(type).find('Solver') != -1 :
				# print initialParam['name'],type,'+1'
				solverParam.append(initialParam)
			name = ''.join(tabReduced[-1:])
			# print ('name : '+name)
			if MORNameExistance(name,initialParam) or type == name:
				node = MORInsert(node,key,newParam)
				if 'paramForcefield' in newParam[key]:
					return newParam[key]['componentType'], newParam[key]['paramForcefield']
				else :
					return newParam[key]['componentType'], initialParam

	return None

def MORInsert(node,key,newParam):

	myParent = node.getParents()[0]
	modelMOR = myParent.createChild(node.name+'_MOR')
	modelMOR.createObject('MechanicalObject',template='Vec1d',position=modesPositionStr)
	modelMOR.moveChild(node)
	print 'Create new child modelMOR and move node in it'

	if 'paramMappedMatrixMapping' in newParam[key]:
		modelMOR.createObject('MappedMatrixForceFieldAndMass', **newParam[key]['paramMappedMatrixMapping'] )
		print 'Create MappedMatrixForceFieldAndMass in modelMOR'

	if 'paramMORMapping' in newParam[key]:		
		node.createObject('ModelOrderReductionMapping', **newParam[key]['paramMORMapping'])
		print "Create ModelOrderReductionMapping in node"

	return node

def createScene(rootNode):

	phase1_snapshots.createScene(Wrapper(rootNode, MORreplace, paramWrapper)) 