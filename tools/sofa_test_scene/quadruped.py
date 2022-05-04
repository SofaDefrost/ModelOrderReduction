import Sofa

import os

path = os.path.dirname(os.path.abspath(__file__)) + '/mesh/'


# Units: mm, kg, s.     Pressure in kPa = k (kg/(m.s^2)) = k (g/(mm.s^2) =  kg/(mm.s^2)

def createScene(rootNode):
    rootNode.addObject('RequiredPlugin', pluginName='SoftRobots')
    # rootNode.addObject('RequiredPlugin', pluginName='SofaPython3')
    rootNode.addObject('RequiredPlugin', pluginName='ModelOrderReduction')
    rootNode.gravity = [0, 0, -9810]
    rootNode.addObject('VisualStyle',
                          displayFlags='showVisualModels showBehaviorModels hideCollisionModels hideBoundingCollisionModels showForceFields showInteractionForceFields hideWireframe')

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('EulerImplicit', name='odesolver', firstOrder="false", rayleighStiffness='0.1',
                       rayleighMass='0.1')
    rootNode.addObject('GenericConstraintSolver', printLog='0', tolerance="1e-15", maxIterations="5000")
    rootNode.addObject('CollisionPipeline', verbose="0")
    rootNode.addObject('BruteForceBroadPhase', name="N2")
    rootNode.addObject('BVHNarrowPhase')
    rootNode.addObject('RuleBasedContactManager', name="Response", response="FrictionContact",
                          responseParams="mu=0.5")
    rootNode.addObject('CollisionResponse', response="FrictionContact", responseParams="mu=0.7")
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
    model.addObject('TetrahedronSetTopologyContainer', src='@loader', name='container')
    model.addObject('MechanicalObject', name='tetras', template='Vec3d', showIndices='false',
                       showIndicesScale='4e-5', rx='0')
    model.addObject('UniformMass', totalMass='0.035')
    model.addObject('SparseLDLSolver', name='preconditioner', template="CompressedRowSparseMatrixMat3x3d")

    model.addObject('TetrahedronFEMForceField', template='Vec3d', name='FEM', method='large', poissonRatio='0.05',
                       youngModulus='70')
    model.addObject('BoxROI', name='boxROISubTopo', box='0 0 0 150 -100 1', drawBoxes='true')
    model.addObject('BoxROI', name='membraneROISubTopo', box='0 0 -0.1 150 -100 0.1', computeTetrahedra="false",
                       drawBoxes='true')
    model.addObject('GenericConstraintCorrection', solverName='preconditioner')
    ##########################################
    # Sub topology
    modelSubTopo = model.addChild('modelSubTopo')

    modelSubTopo.addObject('TriangleSetTopologyContainer', position='@../membraneROISubTopo.pointsInROI',
                              triangles='@../membraneROISubTopo.trianglesInROI', name='container')
    modelSubTopo.addObject('TriangleFEMForceField', template='Vec3d', name='FEM', method='large',
                              poissonRatio='0.49', youngModulus='5000')

    ##########################################
    # Constraint
    centerCavity = model.addChild('centerCavity')
    centerCavity.addObject('MeshSTLLoader', name='loader', filename=path + centerCavityMesh)
    centerCavity.addObject('Mesh', src='@loader', name='topo')
    centerCavity.addObject('MechanicalObject', name='centerCavity')
    centerCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                              value="0.00", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                              valueType="volumeGrowth")
    centerCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    rearLeftCavity = model.addChild('rearLeftCavity')
    rearLeftCavity.addObject('MeshSTLLoader', name='loader', filename=path + rearLeftCavityMesh)
    rearLeftCavity.addObject('Mesh', src='@loader', name='topo')
    rearLeftCavity.addObject('MechanicalObject', name='rearLeftCavity')
    rearLeftCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                valueType="volumeGrowth", value="0.000", triangles='@topo.triangles', drawPressure='0',
                                drawScale='0.0002')
    rearLeftCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    rearRightCavity = model.addChild('rearRightCavity')
    rearRightCavity.addObject('MeshSTLLoader', name='loader', filename=path + rearRightCavityMesh)
    rearRightCavity.addObject('Mesh', src='@loader', name='topo')
    rearRightCavity.addObject('MechanicalObject', name='rearRightCavity')
    rearRightCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                 value="0.00", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                                 valueType="volumeGrowth")
    rearRightCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    frontLeftCavity = model.addChild('frontLeftCavity')
    frontLeftCavity.addObject('MeshSTLLoader', name='loader', filename=path + frontLeftCavityMesh)
    frontLeftCavity.addObject('Mesh', src='@loader', name='topo')
    frontLeftCavity.addObject('MechanicalObject', name='frontLeftCavity')
    frontLeftCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                 value="0.000", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                                 valueType="volumeGrowth")
    frontLeftCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    frontRightCavity = model.addChild('frontRightCavity')
    frontRightCavity.addObject('MeshSTLLoader', name='loader', filename=path + frontRightCavityMesh)
    frontRightCavity.addObject('Mesh', src='@loader', name='topo')
    frontRightCavity.addObject('MechanicalObject', name='frontRightCavity')
    frontRightCavity.addObject('SurfacePressureConstraint', name="SurfacePressureConstraint", template='Vec3d',
                                  value="0.000", triangles='@topo.triangles', drawPressure='0', drawScale='0.0002',
                                  valueType="volumeGrowth")
    frontRightCavity.addObject('BarycentricMapping', name='mapping', mapForces='false', mapMasses='false')

    modelCollis = model.addChild('modelCollis')
    modelCollis.addObject('MeshSTLLoader', name='loader', filename=path + 'quadriped_collision.stl',
                             rotation="0 0 0", translation="0 0 0")
    modelCollis.addObject('TriangleSetTopologyContainer', src='@loader', name='container')
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
                           template='ExtVec3f',
                           color='0.7 0.7 0.7 0.6')

    modelVisu.addObject('BarycentricMapping')

    planeNode = rootNode.addChild('Plane')
    planeNode.addObject('MeshObjLoader', name='loader', filename="mesh/floorFlat.obj", triangulate="true")
    planeNode.addObject('Mesh', src="@loader")
    planeNode.addObject('MechanicalObject', src="@loader", rotation="90 0 0", translation="0 35 -1", scale="15")
    planeNode.addObject('TriangleCollisionModel', simulated="0", moving="0", group="1")
    planeNode.addObject('LineCollisionModel', simulated="0", moving="0", group="1")
    planeNode.addObject('PointCollisionModel', simulated="0", moving="0", group="1")
    planeNode.addObject('OglModel', name="Visual", fileMesh="mesh/floorFlat.obj", color="1 0 0 1", rotation="90 0 0",
                           translation="0 35 -1", scale="15")
    planeNode.addObject('UncoupledConstraintCorrection')

    return rootNode
