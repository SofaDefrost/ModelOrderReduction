# -*- coding: utf-8 -*-

from stlib.scene.wrapper import Wrapper
    
# Because sofa launcher create a template of our scene, we need to indicate the path to our original scene
import sys
import numpy as np

import originalScene 

####################				PARAM 			  #########################

#### Run manually
modesFilePath = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/2_Modes_Options/"
modesFileName = "test_modes.txt"
pathToWeightsAndRIDdir = "/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/3_Reduced_Model/"
RIDFileName = 'test_RID.txt'
weightsFileName = 'test_weight.txt' 
connectivityFileName = 'conectivity.txt'
nbrOfNode = 28
##################

#### with launcher
# modesFilePath = "$MODESFILEPATH"
# modesFileName = "$MODESFILENAME"
# nbrOfNode = $NBROFNODE
##################
print 'modesFilePath',modesFilePath
print 'modesFileName',modesFileName

paramForcefield = {
	'name' : 'myHyperForceField',
	'prepareECSW' : True,
	'modesPath': modesFilePath+modesFileName,
	'poissonRatio': 0.45,
	'youngModulus': 450,
	'nbTrainingSet' : 200,
	'performECSW': True,
	'RIDPath': pathToWeightsAndRIDdir+RIDFileName,
	'weightsPath': pathToWeightsAndRIDdir+weightsFileName}

paramMappedMatrixMapping = {
	'template': 'Vec1d,Vec1d',
	'object1': '@./MechanicalObject',
	'object2': '@./MechanicalObject',
	'mappedForceField':'@./modelNode/myHyperForceField',
	'mappedMass': '@./modelNode/UniformMass',
	'performECSW': True,
	'listActiveNodesPath': pathToWeightsAndRIDdir+connectivityFileName}

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
for i in range(1,nbrOfNode):
    modesPositionStr = modesPositionStr + ' 0'

###############################################################################

def MORNameExistance (name,kwargs):
    if 'name' in kwargs :
        if kwargs['name'] == name : 
        	return True

solverParam = [[]]*len(paramWrapper)
def MORreplace(node,type,newParam,initialParam):
	global solverParam
	
	currentPath = node.getPathName()
	counter = 0
	for key in newParam :
		tabReduced = key.split('/')
		path = '/'.join(tabReduced[:-1])
		# print ('tabReduced : ',tabReduced)
		# print ('path : '+path)
		# print ('currenPath : '+currentPath)
		if currentPath == path :
			# print type
			if str(type).find('Solver') != -1 or type == 'EulerImplicit' or type == 'GenericConstraintCorrection':
				# print initialParam['name'],type,'+1'
				if 'name' in initialParam:
					solverParam[counter].append(initialParam['name'])
				else: 
					solverParam[counter].append(type)
			name = ''.join(tabReduced[-1:])
			# print ('name : '+name)
			if MORNameExistance(name,initialParam) or type == name:
				# node = MORInsert(node,key,newParam)
				if 'paramForcefield' in newParam[key]:
					return newParam[key]['componentType'], newParam[key]['paramForcefield']
				else :
					return newParam[key]['componentType'], initialParam
		counter+=1

	return None

tmpFind = 0
def searchObjectAndDestroy(node,mySolver,newParam):
	global tmpFind

	for child in node.getChildren():
		currentPath = child.getPathName()
		counter = 0
		# print ('child Name : ',child.name)
		for key in newParam :
			tabReduced = key.split('/')
			path = '/'.join(tabReduced[:-1])
			# print ('path : '+path)
			# print ('currenPath : '+currentPath)
			if currentPath == path :
			
				myParent = child.getParents()[0]
				modelMOR = myParent.createChild(child.name+'_MOR')
				modelMOR.createObject('MechanicalObject',template='Vec1d',position=modesPositionStr)
				modelMOR.moveChild(child)

				for obj in child.getObjects():
					# print obj.name 
					if obj.name in mySolver[counter]:
						# print('To move!')
						child.removeObject(obj)
						child.getParents()[0].addObject(obj)

				print 'Create new child modelMOR and move node in it'

				if 'paramMappedMatrixMapping' in newParam[key]:
					modelMOR.createObject('MappedMatrixForceFieldAndMass', **newParam[key]['paramMappedMatrixMapping'] )
					print 'Create MappedMatrixForceFieldAndMass in modelMOR'

				if 'paramMORMapping' in newParam[key]:		
					child.createObject('ModelOrderReductionMapping', **newParam[key]['paramMORMapping'])
					print "Create ModelOrderReductionMapping in node"
				
				tmpFind+=1

			counter+=1	

		if tmpFind >= len(paramWrapper):
			# print ('yolo')
			return None

		else:
			searchObjectAndDestroy(child,mySolver,newParam)	

def createScene(rootNode):

	originalScene.createScene(Wrapper(rootNode, MORreplace, paramWrapper)) 
	searchObjectAndDestroy(rootNode,solverParam,paramWrapper)