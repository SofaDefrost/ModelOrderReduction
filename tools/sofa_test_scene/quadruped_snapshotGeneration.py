import Sofa

import os
path = os.path.dirname(os.path.abspath(__file__))+'/mesh/'

# Units: mm, kg, s.     Pressure in kPa = k (kg/(m.s^2)) = k (g/(mm.s^2) =  kg/(mm.s^2)

def createScene(rootNode):
                rootNode.createObject('RequiredPlugin', pluginName='SofaPardisoSolver')
                rootNode.createObject('RequiredPlugin', pluginName='SoftRobots')
                rootNode.createObject('RequiredPlugin', pluginName='SofaPython')
                rootNode.createObject('RequiredPlugin', pluginName='ModelOrderReduction')
                #rootNode.createObject('RequiredPlugin', pluginName='SofaMJEDFEM')
                rootNode.findData('gravity').value='0 0 -9810';
                #rootNode.findData('gravity').value='0 0 0';
                rootNode.createObject('VisualStyle', displayFlags='showVisualModels showBehaviorModels hideCollisionModels hideBoundingCollisionModels showForceFields showInteractionForceFields hideWireframe')

                rootNode.createObject('FreeMotionAnimationLoop')
                rootNode.createObject('GenericConstraintSolver', printLog='0', tolerance="1e-15", maxIterations="5000")
                rootNode.createObject('CollisionPipeline', verbose="0")
		rootNode.createObject('BruteForceDetection', name="N2")
		#rootNode.createObject('RuleBasedContactManager', name="Response", response="FrictionContact", rules="0 * FrictionContact?mu=0.01" )
		rootNode.createObject('CollisionResponse', response="FrictionContact", responseParams="mu=0.7")
		rootNode.createObject('LocalMinDistance', name="Proximity", alarmDistance="2.5", contactDistance="0.5", angleCone="0.01")

		rootNode.createObject('BackgroundSetting', color='0 0.168627 0.211765')
                rootNode.createObject('OglSceneFrame', style="Arrows", alignment="TopRight")
 #               rootNode.createObject('ClipPlane', normal="0 -1 0")
                
		##########################################
                # FEM Model                              
                model = rootNode.createChild('model')
                model.createObject('EulerImplicit', name='odesolver',firstOrder="false", rayleighStiffness='0.1', rayleighMass='0.1')
                model.createObject('SparseLDLSolver', name='preconditioner', template="CompressedRowSparseMatrix3d")
                # model.createObject('SparsePARDISOSolver', name="preconditioner", symmetric="1")
                # model.createObject('MeshVTKLoader', name='loader', filename=path+'full_quadriped_fine.vtk', edges='')
                model.createObject('MeshVTKLoader', name='loader', filename=path+'full_quadriped_SMALL.vtk')
                model.createObject('TetrahedronSetTopologyContainer', src='@loader', name='container',position="@loader.position",  edges='', tetrahedra="@loader.tetrahedra")
                model.createObject('TetrahedronSetTopologyModifier')
                model.createObject('TetrahedronSetTopologyAlgorithms', template='Vec3d')
                model.createObject('TetrahedronSetGeometryAlgorithms', template='Vec3d')
                
#                model.createObject('MechanicalObject', name='tetras', template='Vec3d', showIndices='false', showIndicesScale='4e-5', rx='0', translation='-80 55 0')
                model.createObject('MechanicalObject', name='tetras', template='Vec3d', showIndices='false', showIndicesScale='4e-5', rx='0')
                #model.createObject('UniformMass', totalmass='0.035')
                model.createObject('UniformMass', totalMass='0.200')
                model.createObject('TetrahedronFEMForceField', template='Vec3d', name='FEM', method='large', poissonRatio='0.05',  youngModulus='70', drawAsEdges="1")
		  
		model.createObject('BoxROI', name='boxROISubTopo', box='0 0 0 150 -100 1', drawBoxes='true') 
		model.createObject('BoxROI', name='membraneROISubTopo', box='0 0 -0.1 150 -100 0.1',computeTetrahedra="false", drawBoxes='true') 
		
                model.createObject('GenericConstraintCorrection', solverName='preconditioner')



                ##########################################
                # Sub topology                           
                modelSubTopo = model.createChild('modelSubTopo')
                
                modelSubTopo.createObject('TriangleSetTopologyContainer', position='@loader.position', triangles="@membraneROISubTopo.trianglesInROI", name='container')
                modelSubTopo.createObject('TriangleFEMForceField', template='Vec3d', name='FEM', method='large', poissonRatio='0.49',  youngModulus='5000')


		##########################################
                # Constraint                             
                centerCavity = model.createChild('centerCavity')
                # centerCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Center-cavity_finer.stl')
                centerCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Center-cavityREMESHEDlighter.stl')
                centerCavity.createObject('Mesh', src='@loader', name='topo')
                #centerCavity.createObject('MechanicalObject', name='centerCavity', translation='-80 55 0')
                centerCavity.createObject('MechanicalObject', name='centerCavity')
                centerCavity.createObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d', value="0.00", triangles='@topo.triangles', visualization='0', showVisuScale='0.0002', valueType="volumeGrowth")
                #centerCavity.createObject('PythonScriptController', filename="PneuNetsController.py", classname="controller")
                centerCavity.createObject('BarycentricMapping', name='mapping',  mapForces='false', mapMasses='false')
                                
                rearLeftCavity = model.createChild('rearLeftCavity')
                # rearLeftCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Rear-Left-cavity_finer.stl')
                rearLeftCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Rear-Left-cavity_collis.stl')
                rearLeftCavity.createObject('Mesh', src='@loader', name='topo')
                #rearLeftCavity.createObject('MechanicalObject', name='rearLeftCavity', translation='-80 55 0')
                rearLeftCavity.createObject('MechanicalObject', name='rearLeftCavity')
                rearLeftCavity.createObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d', valueType="volumeGrowth", value="0.000", triangles='@topo.triangles', visualization='0', showVisuScale='0.0002')
#                rearLeftCavity.createObject('PythonScriptController', filename="PneuNetsController.py", classname="controller")
                rearLeftCavity.createObject('BarycentricMapping', name='mapping',  mapForces='false', mapMasses='false')
                
                rearRightCavity = model.createChild('rearRightCavity')
                # rearRightCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Rear-Right-cavity_finer.stl')
                rearRightCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Rear-Right-cavity_collis.stl')
                rearRightCavity.createObject('Mesh', src='@loader', name='topo')
                #rearRightCavity.createObject('MechanicalObject', name='rearRightCavity', translation='-80 55 0')
                rearRightCavity.createObject('MechanicalObject', name='rearRightCavity')
                rearRightCavity.createObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d', value="0.00", triangles='@topo.triangles', visualization='0', showVisuScale='0.0002', valueType="volumeGrowth")
                #rearRightCavity.createObject('PythonScriptController', filename="PneuNetsController.py", classname="controller")
                rearRightCavity.createObject('BarycentricMapping', name='mapping',  mapForces='false', mapMasses='false')
                
                
                frontLeftCavity = model.createChild('frontLeftCavity')
                # frontLeftCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Front-Left-cavity_finer.stl')
                frontLeftCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Front-Left-cavity_collis.stl')
                frontLeftCavity.createObject('Mesh', src='@loader', name='topo')
                #frontLeftCavity.createObject('MechanicalObject', name='frontLeftCavity', translation='-80 55 0')
                frontLeftCavity.createObject('MechanicalObject', name='frontLeftCavity')
                frontLeftCavity.createObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d', value="0.000", triangles='@topo.triangles', visualization='0', showVisuScale='0.0002', valueType="volumeGrowth")
                #frontLeftCavity.createObject('PythonScriptController', filename="PneuNetsController.py", classname="controller")
                frontLeftCavity.createObject('BarycentricMapping', name='mapping',  mapForces='false', mapMasses='false')
                		
                
                frontRightCavity = model.createChild('frontRightCavity')
                # frontRightCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Front-Right-cavity_finer.stl')
                frontRightCavity.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_Front-Right-cavity_collis.stl')
                frontRightCavity.createObject('Mesh', src='@loader', name='topo')
                #frontRightCavity.createObject('MechanicalObject', name='frontRightCavity', translation='-80 55 0')
                frontRightCavity.createObject('MechanicalObject', name='frontRightCavity')
                frontRightCavity.createObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d', value="0.000", triangles='@topo.triangles', visualization='0', showVisuScale='0.0002', valueType="volumeGrowth")
                #frontRightCavity.createObject('PythonScriptController', filename="PneuNetsController.py", classname="controller")
                frontRightCavity.createObject('BarycentricMapping', name='mapping',  mapForces='false', mapMasses='false')
                                
                modelCollis = model.createChild('modelCollis')
		modelCollis.createObject('MeshSTLLoader', name='loader', filename=path+'quadriped_collision.stl', rotation="0 0 0", translation="0 0 0")
		modelCollis.createObject('TriangleSetTopologyContainer', src='@loader', name='container')
		modelCollis.createObject('MechanicalObject', name='collisMO', template='Vec3d')
		modelCollis.createObject('Triangle',group="0")
		modelCollis.createObject('Line',group="0")
		modelCollis.createObject('Point',group="0")
		modelCollis.createObject('BarycentricMapping')
                
                
		##########################################
                # Visualization  
                modelVisu = model.createChild('visu')
                modelVisu.createObject(  'MeshSTLLoader', name= 'loader', filename=path+"quadriped_collision.stl")

                modelVisu.createObject(  'OglModel',
                                    src='@loader',
                                    template='ExtVec3f',
                                    color='0.7 0.7 0.7 0.6')

                modelVisu.createObject('BarycentricMapping')

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
