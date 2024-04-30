import Sofa

import os

path = os.path.dirname(os.path.abspath(__file__)) + '/mesh/'


# Units: mm, kg, s.     Pressure in kPa = k (kg/(m.s^2)) = k (g/(mm.s^2) =  kg/(mm.s^2)

def createScene(rootNode):
    rootNode.addObject('RequiredPlugin', name='SoftRobots')
    # rootNode.addObject('RequiredPlugin', pluginName='SofaPython3')
    rootNode.addObject('RequiredPlugin', name='ModelOrderReduction')
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.AnimationLoop') # Needed to use components [FreeMotionAnimationLoop]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Collision.Detection.Algorithm') # Needed to use components [BVHNarrowPhase,BruteForceBroadPhase,CollisionPipeline]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Collision.Detection.Intersection') # Needed to use components [LocalMinDistance]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Collision.Geometry') # Needed to use components [LineCollisionModel,PointCollisionModel,TriangleCollisionModel]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Collision.Response.Contact') # Needed to use components [CollisionResponse,RuleBasedContactManager]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Constraint.Lagrangian.Correction') # Needed to use components [GenericConstraintCorrection,UncoupledConstraintCorrection]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Constraint.Lagrangian.Solver') # Needed to use components [GenericConstraintSolver]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Engine.Select') # Needed to use components [BoxROI]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.IO.Mesh') # Needed to use components [MeshOBJLoader,MeshSTLLoader,MeshVTKLoader]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.LinearSolver.Direct') # Needed to use components [SparseLDLSolver]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Mapping.Linear') # Needed to use components [BarycentricMapping]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Mass') # Needed to use components [UniformMass]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.ODESolver.Backward') # Needed to use components [EulerImplicitSolver]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Setting') # Needed to use components [BackgroundSetting]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.SolidMechanics.FEM.Elastic') # Needed to use components [TetrahedronFEMForceField,TriangleFEMForceField]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.StateContainer') # Needed to use components [MechanicalObject]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Topology.Container.Constant') # Needed to use components [MeshTopology]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Topology.Container.Dynamic') # Needed to use components [TetrahedronSetTopologyContainer,TriangleSetTopologyContainer]  
    rootNode.addObject('RequiredPlugin', name='Sofa.Component.Visual') # Needed to use components [VisualStyle]  
    rootNode.addObject('RequiredPlugin', name='Sofa.GL.Component.Rendering3D') # Needed to use components [OglModel,OglSceneFrame]  



    rootNode.gravity = [0, 0, -9810]
    rootNode.addObject('VisualStyle',
                          displayFlags='showVisualModels showBehaviorModels hideCollisionModels hideBoundingCollisionModels showForceFields showInteractionForceFields hideWireframe')

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('EulerImplicitSolver', name='odesolver', firstOrder="false", rayleighStiffness='0.1',
                       rayleighMass='0.1')
    rootNode.addObject('GenericConstraintSolver', printLog='0', tolerance="1e-15", maxIterations="5000")
    rootNode.addObject('CollisionPipeline', verbose="0")
    rootNode.addObject('BruteForceBroadPhase', name="N2")
    rootNode.addObject('BVHNarrowPhase')
    rootNode.addObject('RuleBasedContactManager', name="Response", response="FrictionContactConstraint",
                          responseParams="mu=0.5")
    rootNode.addObject('CollisionResponse', response="FrictionContactConstraint", responseParams="mu=0.7")
    rootNode.addObject('LocalMinDistance', name="Proximity", alarmDistance="2.5", contactDistance="0.5",
                          angleCone="0.01")

    rootNode.addObject('BackgroundSetting', color='0 0.168627 0.211765')
    rootNode.addObject('OglSceneFrame', style="Arrows", alignment="TopRight")

    fineModel = False
    if (fineModel):
        quadrupedMesh = "full_quadriped_fine.vtk"
        centerCavityMesh = "quadriped_Center-cavity_finer.stl"
        rearLeftCavityMesh = "quadriped_Rear-Left-cavity_finer.stl"
        rearRightCavityMesh = "quadriped_Rear-Right-cavity_finer.stl"
        frontLeftCavityMesh = "quadriped_Front-Left-cavity_finer.stl"
        frontRightCavityMesh = "quadriped_Front-Right-cavity_finer.stl"
    else:
        quadrupedMesh = "full_quadriped_SMALL.vtk"
        centerCavityMesh = "quadriped_Center-cavityREMESHEDlighter.stl"
        rearLeftCavityMesh = "quadriped_Rear-Left-cavity_collis.stl"
        rearRightCavityMesh = "quadriped_Rear-Right-cavity_collis.stl"
        frontLeftCavityMesh = "quadriped_Front-Left-cavity_collis.stl"
        frontRightCavityMesh = "quadriped_Front-Right-cavity_collis.stl"
        ##########################################
    # FEM Model
    model = rootNode.addChild('model')
    print(model)

    model.addObject('MeshVTKLoader', name='loader', filename=path + quadrupedMesh)
    model.addObject('TetrahedronSetTopologyContainer', position='@loader.position', tetrahedra='@loader.tetrahedra', name='container')
    model.addObject('MechanicalObject', name='tetras', template='Vec3d', showIndices='false',
                       showIndicesScale='4e-5', rx='0')
    model.addObject('UniformMass', totalMass='0.035')
    model.addObject('SparseLDLSolver', name='preconditioner', template="CompressedRowSparseMatrixMat3x3d")

    model.addObject('TetrahedronFEMForceField', template='Vec3d', name='FEM', method='large', poissonRatio='0.05',
                       youngModulus='70')
    model.addObject('BoxROI', name='boxROISubTopo', box='0 0 0 150 -100 1', drawBoxes='true')
    model.addObject('BoxROI', name='membraneROISubTopo', box='0 0 -0.1 150 -100 0.1', computeTetrahedra="false",
                       drawBoxes='true')
    model.addObject('GenericConstraintCorrection', linearSolver='@preconditioner')
    ##########################################
    # Sub topology
    modelSubTopo = model.addChild('modelSubTopo')

    modelSubTopo.addObject('TriangleSetTopologyContainer', position='@../membraneROISubTopo.pointsInROI',
                              triangles='@../membraneROISubTopo.trianglesInROI', edges='@../membraneROISubTopo.edgesInROI', name='container_modelSubTopo')
    modelSubTopo.addObject('TriangleFEMForceField', template='Vec3d', name='FEM', method='large',
                              poissonRatio='0.49', youngModulus='5000')

    ##########################################
    # Constraint
    centerCavity = model.addChild('centerCavity')
    centerCavity.addObject('MeshSTLLoader', name='loader', filename=path + centerCavityMesh)
    centerCavity.addObject('MeshTopology', src='@loader', name='topo')
    centerCavity.addObject('MechanicalObject', name='centerCavity')
    centerCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                              value="0.00", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                              valueType="volumeGrowth")
    centerCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    rearLeftCavity = model.addChild('rearLeftCavity')
    rearLeftCavity.addObject('MeshSTLLoader', name='loader', filename=path + rearLeftCavityMesh)
    rearLeftCavity.addObject('MeshTopology', src='@loader', name='topo')
    rearLeftCavity.addObject('MechanicalObject', name='rearLeftCavity')
    rearLeftCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                valueType="volumeGrowth", value="0.000", triangles='@topo.triangles', drawPressure='0',
                                drawScale='0.0002')
    rearLeftCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    rearRightCavity = model.addChild('rearRightCavity')
    rearRightCavity.addObject('MeshSTLLoader', name='loader', filename=path + rearRightCavityMesh)
    rearRightCavity.addObject('MeshTopology', src='@loader', name='topo')
    rearRightCavity.addObject('MechanicalObject', name='rearRightCavity')
    rearRightCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                 value="0.00", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                                 valueType="volumeGrowth")
    rearRightCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    frontLeftCavity = model.addChild('frontLeftCavity')
    frontLeftCavity.addObject('MeshSTLLoader', name='loader', filename=path + frontLeftCavityMesh)
    frontLeftCavity.addObject('MeshTopology', src='@loader', name='topo')
    frontLeftCavity.addObject('MechanicalObject', name='frontLeftCavity')
    frontLeftCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                 value="0.000", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                                 valueType="volumeGrowth")
    frontLeftCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    frontRightCavity = model.addChild('frontRightCavity')
    frontRightCavity.addObject('MeshSTLLoader', name='loader', filename=path + frontRightCavityMesh)
    frontRightCavity.addObject('MeshTopology', src='@loader', name='topo')
    frontRightCavity.addObject('MechanicalObject', name='frontRightCavity')
    frontRightCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                  value="0.000", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                                  valueType="volumeGrowth")
    frontRightCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    modelCollis = model.addChild('modelCollis')
    modelCollis.addObject('MeshSTLLoader', name='loader', filename=path + 'quadriped_collision.stl',
                             rotation="0 0 0", translation="0 0 0")
    modelCollis.addObject('TriangleSetTopologyContainer', position='@loader.position', triangles='@loader.triangles', name='container_quadriped')
    modelCollis.addObject('MechanicalObject', name='collisMO', template='Vec3d')
    modelCollis.addObject('TriangleCollisionModel', group="0")
    modelCollis.addObject('LineCollisionModel', group="0")
    modelCollis.addObject('PointCollisionModel', group="0")
    modelCollis.addObject('BarycentricMapping')

    ##########################################
    # Visualization
    modelVisu = model.addChild('visu')
    modelVisu.addObject('MeshSTLLoader', name='loader', filename=path + "quadriped_collision.stl")

    modelVisu.addObject('OglModel',
                           src='@loader',
                           template='Vec3d',
                           color='0.7 0.7 0.7 0.6')

    modelVisu.addObject('BarycentricMapping')

    planeNode = rootNode.addChild('Plane')
    planeNode.addObject('MeshOBJLoader', name='loader', filename="mesh/floorFlat.obj", triangulate="true")
    planeNode.addObject('MeshTopology', src="@loader")
    planeNode.addObject('MechanicalObject', src="@loader", rotation="90 0 0", translation="0 35 -1", scale="15")
    planeNode.addObject('TriangleCollisionModel', simulated="0", moving="0", group="1")
    planeNode.addObject('LineCollisionModel', simulated="0", moving="0", group="1")
    planeNode.addObject('PointCollisionModel', simulated="0", moving="0", group="1")
    planeNode.addObject('OglModel', name="Visual", fileMesh="mesh/floorFlat.obj", color="1 0 0 1", rotation="90 0 0",
                           translation="0 35 -1", scale="15")

    return rootNode
