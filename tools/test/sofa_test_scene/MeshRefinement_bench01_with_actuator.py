# Required import for python
import Sofa
import SofaRuntime
import Sofa.Gui


def main():
	# Make sure to load all SOFA libraries
	SofaRuntime.importPlugin("SofaBaseMechanics")

	# Call the function to create the scene graph
	root = Sofa.Core.Node("root")
	createScene(root)

	# Once defined, initialization of the scene graph
	Sofa.Simulation.init(root)

	


# Function called when the scene graph is being created
def createScene(root):

    root.gravity=[0, 0, -0.9]
    root.name="root"
    root.dt=0.1

   
    root.addObject('RequiredPlugin', name="loadSOFAModules", pluginName="Sofa.Component.LinearSolver.Iterative Sofa.Component.Mass Sofa.Component.MechanicalLoad Sofa.Component.StateContainer Sofa.Component.ODESolver.Backward Sofa.Component.Visual Sofa.Component.AnimationLoop Sofa.Component.Constraint.Lagrangian.Solver")
    
    
    root.addObject('VisualStyle')
    root.VisualStyle.displayFlags="showForceFields hideCollisionModels showBehaviorModels"

    
    # Collision pipeline
    root.addObject('DefaultPipeline')
    root.addObject('FreeMotionAnimationLoop')
    root.addObject('GenericConstraintSolver', resolutionMethod="UnbuildGaussSeidel", tolerance="1e-3", maxIt="200",   printLog="0")
    root.addObject('BruteForceBroadPhase', name="N2")
    root.addObject('BVHNarrowPhase')
    root.addObject('RuleBasedContactManager', responseParams="mu="+str(0.0), name='Response', response='FrictionContactConstraint')# I copied from SofaPython3 doc
    root.addObject('MinProximityIntersection', name="Proximity", alarmDistance="0.75", contactDistance="0.1")# I am not sure about this linw
    root.addObject('LocalMinDistance', alarmDistance=10, contactDistance=5, angleCone=0.01)

    # Topology
    root.addObject('RegularGridTopology', name="grid_1", n="5 20 5", min="0 0 20", max="10 40 30")
    root.addObject('RegularGridTopology', name="grid_2", n="6 5 5", min="-4 20 0", max="14 30 10")

    # HexaBeams
    HexaBeams = root.addChild("HexaBeams")

    #  Beam_01
    childNode1 = HexaBeams.addChild("Beam_01")

    # Time integration scheme and solver
    childNode1.addObject('EulerImplicitSolver', name="cg_odesolver", printLog="false")
    childNode1.addObject('SparseLDLSolver', name="Torus1_SparseLDLSolver", printLog="false") # Assuming that matrix A is linear

    childNode1.addObject('MechanicalObject', src="@../../grid_1", name="Volume")
    childNode1.addObject('TetrahedronSetTopologyContainer', name="Container")
    childNode1.addObject('TetrahedronSetTopologyModifier', name="Modifier")
    childNode1.addObject('TetrahedronSetGeometryAlgorithms', name="GeomAlgo", template="Vec3d")

    childNode1.addObject('Hexa2TetraTopologicalMapping', name="default28", input="@../../grid_1", output="@Container")
    
    childNode1.addObject('DiagonalMass', massDensity="2.0")
    
    childNode1.addObject('BoxROI', name="ROI1", box="-1 -1 0 10 1 50", drawBoxes="1")
    childNode1.addObject('FixedProjectiveConstraint', indices="@ROI1.indices")
    
    # Adding FEM force field
    childNode1.addObject('TetrahedralCorotationalFEMForceField', name="CFEM", youngModulus="600", poissonRatio="0.3", method="large")
    
    childNode1.addObject('GenericConstraintCorrection', name="Beam_01_ConstraintCorrection", linearSolver='@Torus1_SparseLDLSolver', printLog="0" )

    # Collision subnode for Beam_01
    collision = childNode1.addChild('collision')
    collision.addObject('TriangleSetTopologyContainer', name="collisionModel")
    collision.addObject('TriangleSetTopologyModifier',  name="Modifier")
    collision.addObject('TriangleSetGeometryAlgorithms', name="GeomAlgo", template="Vec3d", drawTriangles="0")
    collision.addObject('Tetra2TriangleTopologicalMapping', input="@../Container", output="@collisionModel")
    collision.addObject('TriangleCollisionModel')
    collision.addObject('PointCollisionModel')

    # Adding ROI box for actuation
    childNode1.addObject('BoxROI', name='ROI_act', box='-1 38 0 10 40 50', drawBoxes='false')

    # Adding actuator to the root node
    actuator = root.addChild('actuator')
    actuator.addObject('MechanicalObject', name = 'actuatorState', position = '@HexaBeams/Beam_01/ROI_act.pointsInROI', template = 'Vec3d')

    cableNodeTip = childNode1.addChild('cableNodeTip')
    cableNodeTip.addObject('MechanicalObject', name="actuatedTip", template="Vec3d", position="5 31.6 27.5")
    cableNodeTip.addObject('CableConstraint', name="tipCable", indices="0", pullPoint="2 45 55", valueType="displacement")
    cableNodeTip.addObject('BarycentricMapping', mapForces="false", mapMasses="false")
    
    # Beam_02
    childNode2 = HexaBeams.addChild("Beam_02")

    # Time integration scheme and solver
    childNode2.addObject('EulerImplicitSolver', name="cg_odesolver", printLog="false")
    childNode2.addObject('SparseLDLSolver', name="Torus2_SparseLDLSolver", printLog="false") # Assuming that matrix A is linear

    childNode2.addObject('MechanicalObject', src="@../../grid_2", name="Volume")
    childNode2.addObject('TetrahedronSetTopologyContainer', name="Container")
    childNode2.addObject('TetrahedronSetTopologyModifier', name="Modifier")
    childNode2.addObject('TetrahedronSetGeometryAlgorithms', name="GeomAlgo", template="Vec3d")
    childNode2.addObject('Hexa2TetraTopologicalMapping', name="default28", input="@../../grid_2", output="@Container")
    
    childNode2.addObject('DiagonalMass', massDensity="2.0")
    
    childNode2.addObject('BoxROI', name="ROI2", box="-5 10 -1 15 40 1", drawBoxes="1")
    childNode2.addObject('FixedProjectiveConstraint', indices="@ROI2.indices")
    # Adding FEM force field
    childNode2.addObject('TetrahedralCorotationalFEMForceField', name="CFEM", youngModulus="600", poissonRatio="0.3", method="large")
    
    childNode2.addObject('GenericConstraintCorrection', name="Beam_01_ConstraintCorrection", linearSolver="@Torus2_SparseLDLSolver" ,printLog="0" )

    # Collision subnode for Beam_02
    collision2 = childNode2.addChild('collision')
    collision2.addObject('TriangleSetTopologyContainer', name="collisionModel")
    collision2.addObject('TriangleSetTopologyModifier',  name="Modifier")
    collision2.addObject('TriangleSetGeometryAlgorithms', name="GeomAlgo", template="Vec3d", drawTriangles="0")
    collision2.addObject('Tetra2TriangleTopologicalMapping', input="@../Container", output="@collisionModel")
    collision2.addObject('TriangleCollisionModel')
    collision2.addObject('PointCollisionModel')

    return root


# Function used only if this script is called from a python environment
if __name__ == '__main__':
    main()
