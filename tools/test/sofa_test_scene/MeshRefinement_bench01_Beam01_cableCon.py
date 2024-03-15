# Required import for python
import Sofa
import SofaRuntime
import Sofa.Gui

plugins=["SofaPython3","SoftRobots","ModelOrderReduction","STLIB",
         # normally plugin Sofa.Component is enough but still warning
         "Sofa.Component.Visual",
         "Sofa.Component.AnimationLoop",
         "Sofa.GL.Component.Rendering3D",
         "Sofa.Component.Constraint.Lagrangian.Solver",
         'Sofa.Component.IO.Mesh',
         'Sofa.Component.Playback',
         'Sofa.Component.Constraint.Lagrangian.Correction', # Needed to use components [GenericConstraintCorrection]
         
         'Sofa.Component.Engine.Select', # Needed to use components [BoxROI]
         'Sofa.Component.LinearSolver.Direct', # Needed to use components [SparseLDLSolver]
         'Sofa.Component.Mapping.Linear', # Needed to use components [BarycentricMapping]
         'Sofa.Component.Mass', # Needed to use components [UniformMass]
         'Sofa.Component.ODESolver.Backward', # Needed to use components [EulerImplicitSolver]
         'Sofa.Component.SolidMechanics.FEM.Elastic', # Needed to use components [TetrahedronFEMForceField]
         'Sofa.Component.SolidMechanics.Spring', # Needed to use components [RestShapeSpringsForceField]
         'Sofa.Component.StateContainer', # Needed to use components [MechanicalObject]
         'Sofa.Component.Topology.Container.Dynamic'] # Needed to use components [TetrahedronSetTopologyContainer]



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


    #  Beam_01
    childNode1 = root.addChild("Beam_01")

    # Time integration scheme and solver
    childNode1.addObject('EulerImplicitSolver', name="cg_odesolver", printLog="false")
    childNode1.addObject('SparseLDLSolver', name="Torus1_SparseLDLSolver", printLog="false") # Assuming that matrix A is linear

    #childNode1.addObject('MechanicalObject', src="@../../grid_1", name="Volume")
    childNode1.addObject('MechanicalObject')
    #childNode1.addObject('UniformMass', totalMass="0.1")
    childNode1.addObject('RegularGrid', name="grid_1", n="5 20 5", min="0 0 20", max="10 40 30")
    
    childNode1.addObject('BoxROI', name="ROI1", box="-1 -1 0 10 1 50", drawBoxes="1")
    childNode1.addObject('FixedProjectiveConstraint', indices="@ROI1.indices")
    
    #childNode1.addObject('TetrahedronSetTopologyContainer', name="Container")
   # childNode1.addObject('TetrahedronSetTopologyModifier', name="Modifier")
    #childNode1.addObject('TetrahedronSetGeometryAlgorithms', name="GeomAlgo", template="Vec3d")

    #childNode1.addObject('Hexa2TetraTopologicalMapping', name="default28", input="@../../grid_1", output="@Container")
    childNode1.addObject('DiagonalMass', massDensity="2.0")
    
    
    # Adding FEM force field
    childNode1.addObject('HexahedronFEMForceField', name="CFEM", youngModulus="600", poissonRatio="0.3", method="large")
    
    childNode1.addObject('GenericConstraintCorrection', name="Beam_01_ConstraintCorrection", linearSolver='@Torus1_SparseLDLSolver', printLog="0" )

    # Collision subnode for Beam_01
    #collision = childNode1.addChild('collision')
    #collision.addObject('TriangleSetTopologyContainer', name="collisionModel")
    #collision.addObject('TriangleSetTopologyModifier',  name="Modifier")
    #collision.addObject('TriangleSetGeometryAlgorithms', name="GeomAlgo", template="Vec3d", drawTriangles="0")
    #collision.addObject('Tetra2TriangleTopologicalMapping', input="@../Container", output="@collisionModel")
    #collision.addObject('TriangleCollisionModel')
    #collision.addObject('PointCollisionModel')

    # Adding actuator to the root node
    cableNodeTip = childNode1.addChild('cableNodeTip')
    cableNodeTip.addObject('MechanicalObject', name="actuatedTip", template="Vec3d", position="5 31.6 27.5")
    cableNodeTip.addObject('CableConstraint', name="tipCable", indices="0", pullPoint="2 45 55", valueType="displacement")
    cableNodeTip.addObject('BarycentricMapping', mapForces="false", mapMasses="false")
   
    return root


# Function used only if this script is called from a python environment
if __name__ == '__main__':
    main()
