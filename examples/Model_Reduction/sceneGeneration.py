import yaml

def planeNode(rootNode):

	planeNode = rootNode.createChild('Plane')
	planeNode.createObject('MeshObjLoader', name='loader', filename="mesh/floorFlat.obj", triangulate="true")
	planeNode.createObject('Mesh', src="@loader")
	planeNode.createObject('MechanicalObject', src="@loader", rotation="90 0 0", translation="0 35 -1", scale="15")
	planeNode.createObject('Triangle',simulated="0", moving="0",group="1")
	planeNode.createObject('Line',simulated="0", moving="0",group="1")
	planeNode.createObject('Point',simulated="0", moving="0",group="1")
	planeNode.createObject('OglModel',name="Visual", fileMesh="mesh/floorFlat.obj", color="1 0 0 1",rotation="90 0 0", translation="0 35 -1", scale="15")
	planeNode.createObject('UncoupledConstraintCorrection')

	return rootNode

def instantiateActuators(model,actuatorConfigFile):

	with open(actuatorConfigFile, 'r') as ymlfile:
		cfg_Actuator = yaml.load(ymlfile)

	mappingType = 'BarycentricMapping'
	actuatorType = 'CableConstraint'

	for i in range(len(cfg_Actuator['modelActuator'])) :

		actuator = model.createChild('Actuator_'+str(i)+'_'+cfg_Actuator['modelActuator'][i]['name'])

		#MeshLoader
		if "meshLoader" in  cfg_Actuator['modelActuator'][i]:
			actuator.createObject('MeshSTLLoader',
				name='loader',
				filename=cfg_Actuator['modelActuator'][i]['meshLoader'])
			actuator.createObject('Mesh', src='@loader', name='topo')

		#Mesh
		if "mesh" in cfg_Actuator['modelActuator'][i]:
			actuator.createObject('Mesh')
			instanciateArg(actuator,"Mesh",cfg_Actuator['modelActuator'][i]['mesh'])

		#MechanicalObject
		actuator.createObject('MechanicalObject', name="actuatorMecha")
		if "mechanicalObject" in cfg_Actuator['modelActuator'][i]:
			instanciateArg(actuator,"actuatorMecha",cfg_Actuator['modelActuator'][i]['mechanicalObject'])

		#Actuator
		if "actuatorType" in  cfg_Actuator['modelActuator'][i]:
			actuatorType = cfg_Actuator['modelActuator'][i]['actuatorType']
		elif  "actuatorType" in  cfg_Actuator:
			actuatorType = cfg_Actuator['actuatorType']

		actuator.createObject(actuatorType, name="actuatorType")

		if "actuator" in  cfg_Actuator['modelActuator'][i] and ("actuatorType" in  cfg_Actuator['modelActuator'][i] or "actuatorType" in  cfg_Actuator):
			instanciateArg(actuator,"actuatorType",cfg_Actuator['modelActuator'][i]['actuator'])

		#Mapping
		if "mappingType" in  cfg_Actuator['modelActuator'][i]:
			mappingType = cfg_Actuator['modelActuator'][i]['mappingType']
		elif "mappingType" in  cfg_Actuator:
			mappingType = cfg_Actuator['mappingType']

		actuator.createObject(mappingType, name="actuatorMapping",mapForces="false",mapMasses="false")

		if "mapping" in  cfg_Actuator['modelActuator'][i] and ("mappingType" in  cfg_Actuator['modelActuator'][i] or "mappingType" in  cfg_Actuator):
			instanciateArg(actuator,"actuatorMapping",cfg_Actuator['modelActuator'][i]['mapping'])

		if "other" in  cfg_Actuator['modelActuator'][i]:
			instanciateObjAndArg(actuator,cfg_Actuator['modelActuator'][i]['other'])

	return model

def instanciatePythonScriptController(model,modelCfg):
 
	for i in range(len(modelCfg['modelNode']['pythonControllers'])):
		model.createObject('PythonScriptController',
			classname=modelCfg['modelNode']['pythonControllers'][i]['classname'],
			filename=modelCfg['modelNode']['pythonControllers'][i]['filename'])

	return model

def instantiateVisu(model,modelCfg):

	modelVisu = model.createChild('Visu')           
	modelVisu.createObject('OglModel', 
		filename=modelCfg['modelNode']['pathTodir']+modelCfg['modelNode']['nameModelVisu'],
		template='ExtVec3f',
		color='0.7 0.7 0.7 0.6')
	if 'rotation' in modelCfg['modelNode']:
		modelVisu.getObject('OglModel').findData('rotation').value = modelCfg['modelNode']['rotation']
	if 'translation' in modelCfg['modelNode']:
		modelVisu.getObject('OglModel').findData('translation').value = modelCfg['modelNode']['translation']
	
	modelVisu.createObject('BarycentricMapping')

	return model

def instanciateArg(node,nameSofaObj,cfgFile):

	for arg in cfgFile:
		node.getObject(nameSofaObj).findData(arg).value = cfgFile[arg]

	return node

# TO TEST
def instanciateObjAndArg(node,cfgFile):

	for arg1 in cfgFile:
		node.createObject(arg1)
		node = instanciateArg(node,arg1,cfgFile[arg1])

	return node

def instanciateAll(node,cfgFile):

	for arg1 in cfgFile:
		node.createObject(arg1)
		for arg2 in cfgFile[arg1]:
			node.getObject(arg1).findData(arg2).value = cfgFile[arg1][arg2]

	return node

def instanciateCollisionModel(model,modelCfg):
		
	modelCollis = model.createChild('modelCollis')
	modelCollis.createObject('MeshSTLLoader',
		name='loader',
		filename=modelCfg['modelNode']['pathTodir']+modelCfg['modelNode']['nameModelCol'],
		rotation="0 0 0",
		translation="0 0 0")
	modelCollis.createObject('TriangleSetTopologyContainer', src='@loader', name='container')
	modelCollis.createObject('MechanicalObject', name='collisMO', template='Vec3d')
	modelCollis.createObject('Triangle',group="0")
	modelCollis.createObject('Line',group="0")
	modelCollis.createObject('Point',group="0")
	modelCollis.createObject('BarycentricMapping')

	return model

def instanciateForceField(model,modelCfg):

	return instanciateAll(model,modelCfg['modelNode']['ForceField'])

def instanciateBoxROI(model,modelCfg,subTopo=None):

	model.createObject('BoxROI', box=modelCfg['modelNode']['BoxROIpts'])
	if subTopo is None :

		return instanciateAll(model,modelCfg['modelNode']['BoxROI'])
	else :	
		subTopo = model.createChild(subTopo)
		instanciateAll(subTopo,modelCfg['modelNode']['BoxROI'])
		return model

def instanciateSolver(rootNode,modelCfg):

	#Solver
		solverNode = rootNode.createChild('solverNode')

		solverNode.createObject('EulerImplicitSolver', rayleighStiffness='0.1', rayleighMass='0.1')
		solverNode.createObject('SparseLDLSolver')

		if 'solverNode' in modelCfg:
			return instanciateAll(solverNode,modelCfg['solverNode'])

		else: return solverNode

def instantiateRootNode(rootNode,rootNodeCfg):

	#RequiredPlugin
		if 'requiredPlugin' in rootNodeCfg['rootNode']:
			for arg in rootNodeCfg['rootNode']['requiredPlugin']:
				rootNode.createObject('RequiredPlugin', name=arg, pluginName=arg)

	#Scene Paramters
		if 'sceneParam' in rootNodeCfg['rootNode']:
			for arg in rootNodeCfg['rootNode']['sceneParam']:
				rootNode.findData(arg).value = rootNodeCfg['rootNode']['sceneParam'][arg]
		if 'visualStyle' in rootNodeCfg['rootNode']: 
			rootNode.createObject('VisualStyle', displayFlags=rootNodeCfg['rootNode']['visualStyle'])

	#Solver
		rootNode.createObject('FreeMotionMasterSolver')
		rootNode.createObject('GenericConstraintSolver', printLog='0', tolerance="1e-15", maxIterations="5000")

	#Collision
		if 'collision' in rootNodeCfg['rootNode']:
			rootNode.createObject('CollisionPipeline', verbose="0")
			rootNode.createObject('BruteForceDetection', name="N2")
			rootNode.createObject('LocalMinDistance',
				name="Proximity",
				alarmDistance="2.5",
				contactDistance="0.5",
				angleCone="0.01") ### alarm / contact
			if 'friction' in rootNodeCfg['rootNode']['collision']:
				rootNode.createObject('CollisionResponse',
				response="FrictionContact",
				responseParams=rootNodeCfg['rootNode']['collision']['friction']) 
			else :
				rootNode.createObject('CollisionResponse')

		return rootNode

def instantiateModelLight(solverNode,modelCfg):

	#Model
		model = solverNode.createChild('model')

	#ModelMesh
		if ('nameModelMesh' in modelCfg['modelNode']) and ('pathTodir' in modelCfg['modelNode']):
			model.createObject('MeshVTKLoader', name="loader", filename=modelCfg['modelNode']['pathTodir']+modelCfg['modelNode']['nameModelMesh']) 
			model.createObject('Mesh', src='@loader', name='topo')  
	
    #MechanicalObject
		model.createObject('MechanicalObject')
		if 'mechanicalParam' in modelCfg['modelNode']:
		    for arg in modelCfg['modelNode']['mechanicalParam'] :
		        model.getObject('MechanicalObject').findData(arg).value = modelCfg['modelNode']['mechanicalParam'][arg]
		
		if 'rotation' in modelCfg['modelNode']:
			model.getObject('MechanicalObject').findData('rotation').value = modelCfg['modelNode']['rotation']
		
		if 'translation' in modelCfg['modelNode']:
			model.getObject('MechanicalObject').findData('translation').value = modelCfg['modelNode']['translation']

		model.createObject('UniformMass')
		if 'totalmass' in modelCfg['modelNode']:
			model.getObject('UniformMass').findData('totalmass').value = modelCfg['modelNode']['totalmass']

		return model

def instantiateModel(solverNode,modelCfg):

	#Model
		model = instantiateModelLight(solverNode,modelCfg)
		
    #Forcefield
		if 'ForceField' in modelCfg['modelNode']:
			model = instanciateForceField(model,modelCfg)

    #BoxROI
		if 'BoxROI' in modelCfg['modelNode']:
			model = instanciateBoxROI(model,modelCfg)

	#Solver
		if 'linearSolver' in modelCfg['modelNode']:
			model.createObject('LinearSolverConstraintCorrection', solverName=modelCfg['modelNode']['linearSolver']) #have to be after forcefield

	#PythonScriptController
		if 'pythonControllers' in modelCfg['modelNode']:
			model = instanciatePythonScriptController(model,modelCfg)

	#CollisionModel
		if 'collision' in modelCfg['rootNode']:
			model = instanciateCollisionModel(model,modelCfg)

	#Visualization 
		if 'nameModelVisu' in modelCfg['modelNode']: 
			model = instantiateVisu(model,modelCfg)
			
	#Actuator
		if 'actuatorConfigFile' in modelCfg['modelNode']: 
			model = instantiateActuators(model,modelCfg['modelNode']['actuatorConfigFile'])

		return model