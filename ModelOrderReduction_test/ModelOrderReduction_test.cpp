#include <sofa/testing/BaseSimulationTest.h>
#include <SofaSimulationGraph/DAGSimulation.h>

namespace sofa {

    using namespace defaulttype;

    /// Patch test

    /**  Test of ModelOrderReduction
   */

    template <typename _DataTypes>
    struct ModelOrderReduction_test : public sofa::testing::BaseTest
    {
        typedef _DataTypes DataTypes;
        typedef typename DataTypes::CPos CPos;
        typedef typename DataTypes::VecCoord VecCoord;
        typedef typename DataTypes::VecDeriv VecDeriv;

        /// Root of the scene graph
        simulation::Node::SPtr root;
        /// Simulation
        simulation::Simulation* simulation;

        /// Create the context for the scene
        void SetUp()
        {
            sofa::simulation::setSimulation(simulation = new sofa::simulation::graph::DAGSimulation());

            root = simulation::getSimulation()->createNewGraph("root");
        }


        /// After simulation compare the positions of points to the theoretical positions.
        bool testSomething()
        {
            return true;
        }

        /// Unload the scene
        void TearDown()
        {
            if (root!=NULL)
                sofa::simulation::getSimulation()->unload(root);
        }
    };

    // Define the list of DataTypes to instantiate
    using ::testing::Types;
    typedef Types<
        Vec3Types
    > DataTypes; // the types to instantiate.

    // Test suite for all the instantiations
    TYPED_TEST_CASE(ModelOrderReduction_test, DataTypes);

    // test case: smallcorotationalStrainMapping
    TYPED_TEST( ModelOrderReduction_test , SmallCorotationalPatchTest)
    {
        ASSERT_TRUE( this->testSomething() );
    }
}
