import Sofa
import Sofa.Core
import os
pathSceneFile = os.path.dirname(os.path.abspath(__file__))
pathMesh = os.path.dirname(os.path.abspath(__file__))+'/'
# Units: mm, kg, s.     Pressure in kPa = k (kg/(m.s^2)) = k (g/(mm.s^2) =  kg/(mm.s^2)

def createScene(rootNode):
                rootNode.addObject('VisualStyle', displayFlags='showVisualModels hideBehaviorModels showCollisionModels hideBoundingCollisionModels showForceFields showInteractionForceFields hideWireframe')
                rootNode.gravity=[0,-9810, 0]
                rootNode.dt = 0.0001
                rootNode.addObject('FreeMotionAnimationLoop')
                rootNode.addObject('GenericConstraintSolver', name='GSSolver', maxIterations='10000', tolerance='1e-15')
                rootNode.addObject('CollisionPipeline', verbose="0")
                rootNode.addObject('BruteForceBroadPhase', name="N2")
                rootNode.addObject('BVHNarrowPhase')
                rootNode.addObject('CollisionResponse', response="FrictionContactConstraint", responseParams="mu=0.0")
                rootNode.addObject('LocalMinDistance', name="Proximity", alarmDistance="8.0", contactDistance="0.5", angleCone="0.01")

                solverNode = rootNode.addChild('solverNode')
                solverNode.addObject('EulerImplicitSolver', name='odesolver',firstOrder="false", rayleighStiffness='0.0', rayleighMass='0.0')
                solverNode.addObject('SparseLDLSolver', name="preconditioner", template="CompressedRowSparseMatrixd")
                solverNode.addObject('GenericConstraintCorrection', linearSolver='@preconditioner',printLog=True, name='ResReso')

                ##########################################
                # FEM Model                              #
                ##########################################
                
                sphereTranslation = [0,10,0]
                model = solverNode.addChild('model')
                model.addObject('MeshVTKLoader', name='loader', filename=pathMesh+'sphere.vtk', translation=sphereTranslation)
                model.addObject('Mesh',src = '@loader')
                model.addObject('MechanicalObject', name='tetras', template='Vec3d', showIndices='false', showIndicesScale='4e-5', rx='0',printLog="0")
                model.addObject('UniformMass', totalMass='0.2', printLog='0')
                model.addObject('TetrahedronFEMForceField', template='Vec3d',youngModulus=1.0e3)
                
                dummyActuator = rootNode.addChild('dummyActuator')
                dummyActuator.addObject('MechanicalObject', name = 'actuatorState', position = [0,0,0], template = 'Vec3d')
                
                modelCollis = model.addChild('modelCollis')
                modelCollis.addObject('MeshSTLLoader', name='loader', filename=pathMesh+'sphere.stl', rotation="0 0 0", translation=sphereTranslation)
                #modelCollis.addObject('MeshSTLLoader', name='loader', filename=pathMesh+'sphereFine.stl', rotation="0 0 0", translation=sphereTranslation)
                modelCollis.addObject('TriangleSetTopologyContainer', src='@loader', name='container')
                modelCollis.addObject('MechanicalObject', name='collisMO', template='Vec3d')
                modelCollis.addObject('TriangleCollisionModel',group="0")
                modelCollis.addObject('LineCollisionModel',group="0")
                modelCollis.addObject('PointCollisionModel',group="0")
                modelCollis.addObject('BarycentricMapping')

                rotation=[0,0,0]
                #rotation=[30,0,0]
                planeNode = rootNode.addChild('Plane')
                planeNode.addObject('MeshObjLoader', name='loader', filename="mesh/floorFlat.obj", triangulate="true",rotation=rotation)
                planeNode.addObject('Mesh', src="@loader")
                planeNode.addObject('MechanicalObject', src="@loader", rotation="0 0 0", translation="0 0 0", scale="1")
                planeNode.addObject('TriangleCollisionModel',simulated="0", moving="0",group="1",name='TriPlane')
                planeNode.addObject('LineCollisionModel',simulated="0", moving="0",group="1")
                planeNode.addObject('PointCollisionModel',simulated="0", moving="0",group="1")
                planeNode.addObject('OglModel',name="Visual", fileMesh="mesh/floorFlat.obj", color="1 0 0 1",rotation=rotation, translation="0 0 0", scale="1")
                planeNode.addObject('UncoupledConstraintCorrection')

                return rootNode
