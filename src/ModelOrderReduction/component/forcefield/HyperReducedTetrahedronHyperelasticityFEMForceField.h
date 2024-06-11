/******************************************************************************
*            Model Order Reduction plugin for SOFA                            *
*                         version 1.0                                         *
*                       Copyright © Inria                                     *
*                       All rights reserved                                   *
*                       2018                                                  *
*                                                                             *
* This software is under the GNU General Public License v2 (GPLv2)            *
*            https://www.gnu.org/licenses/licenses.en.html                    *
*                                                                             *
*                                                                             *
*                                                                             *
* Authors: Olivier Goury, Felix Vanneste                                      *
*                                                                             *
* Contact information: https://project.inria.fr/modelorderreduction/contact   *
******************************************************************************/
#pragma once
#include <ModelOrderReduction/config.h>
#include <ModelOrderReduction/component/forcefield/HyperReducedHelper.h>
#include <sofa/component/solidmechanics/fem/hyperelastic/TetrahedronHyperelasticityFEMForceField.h>

namespace sofa::component::forcefield
{
using namespace std;
using namespace sofa::defaulttype;
using namespace sofa::core::topology;
using namespace solidmechanics::fem::hyperelastic;

//***************** Tetrahedron FEM code for several elastic models: TotalLagrangianForceField************************//

/** Compute Finite Element forces based on tetrahedral elements.
*/
template<class DataTypes>
class HyperReducedTetrahedronHyperelasticityFEMForceField : public virtual solidmechanics::fem::hyperelastic::TetrahedronHyperelasticityFEMForceField<DataTypes>, public modelorderreduction::HyperReducedHelper
{
  public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedTetrahedronHyperelasticityFEMForceField, DataTypes),
        SOFA_TEMPLATE(solidmechanics::fem::hyperelastic::TetrahedronHyperelasticityFEMForceField, DataTypes), HyperReducedHelper);

    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename Coord::value_type Real;
    typedef typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation EdgeInformation;

    typedef core::objectmodel::Data<VecDeriv>    DataVecDeriv;
    typedef core::objectmodel::Data<VecCoord>    DataVecCoord;

    typedef type::Mat<3,3,Real> Matrix3;
    typedef type::MatSym<3,Real> MatrixSym;
    typedef std::pair<MatrixSym,MatrixSym> MatrixPair;
    typedef std::pair<Real,MatrixSym> MatrixCoeffPair;


    typedef type::vector<Real> SetParameterArray;
    typedef type::vector<Coord> SetAnisotropyDirectionArray;


    typedef sofa::Index Index;
    typedef core::topology::BaseMeshTopology::Tetra Element;
    typedef core::topology::BaseMeshTopology::SeqTetrahedra VecElement;
    typedef sofa::core::topology::Topology::Tetrahedron Tetrahedron;
    typedef sofa::core::topology::Topology::TetraID TetraID;
    typedef sofa::core::topology::Topology::Tetra Tetra;
    typedef sofa::core::topology::Topology::Edge Edge;
    typedef sofa::core::topology::BaseMeshTopology::EdgesInTriangle EdgesInTriangle;
    typedef sofa::core::topology::BaseMeshTopology::EdgesInTetrahedron EdgesInTetrahedron;
    typedef sofa::core::topology::BaseMeshTopology::TrianglesInTetrahedron TrianglesInTetrahedron;


public :
	
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::globalParameters;


 protected :
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::m_topology;
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::m_initialPoints;	/// the intial positions of the points
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::m_updateMatrix;
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::d_stiffnessMatrixRegularizationWeight;
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::d_materialName; /// the name of the material
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::d_parameterSet;
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::d_anisotropySet;

    // Reduced Order Variables

    using HyperReducedHelper::d_prepareECSW;
    using HyperReducedHelper::d_nbModes;
    using HyperReducedHelper::d_modesPath;
    using HyperReducedHelper::d_nbTrainingSet;
    using HyperReducedHelper::d_periodSaveGIE;

    using HyperReducedHelper::d_performECSW;
    using HyperReducedHelper::d_RIDPath;
    using HyperReducedHelper::d_weightsPath;

    using HyperReducedHelper::Gie;
    using HyperReducedHelper::weights;
    using HyperReducedHelper::reducedIntegrationDomain;

    using HyperReducedHelper::m_modes;
    using HyperReducedHelper::m_RIDsize;
    Eigen::Matrix<unsigned int, Eigen::Dynamic, 1> reducedIntegrationDomainWithEdges;

    unsigned int m_RIDedgeSize;

    using TetrahedronHyperelasticityFEMForceField<DataTypes>::m_tetrahedronInfo;
    using TetrahedronHyperelasticityFEMForceField<DataTypes>::m_edgeInfo;
   
protected:
   HyperReducedTetrahedronHyperelasticityFEMForceField();
   
   virtual   ~HyperReducedTetrahedronHyperelasticityFEMForceField();
public:

    virtual void init() override;
    
    virtual void addForce(const core::MechanicalParams* mparams /* PARAMS FIRST */, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& d_v) override;
    virtual void addDForce(const core::MechanicalParams* mparams /* PARAMS FIRST */, DataVecDeriv& d_df, const DataVecDeriv& d_dx) override;
    void buildStiffnessMatrix(core::behavior::StiffnessMatrix* /* matrix */) override;

    void draw(const core::visual::VisualParams* vparams) override;

  protected:

    /// the array that describes the complete material energy and its derivatives

    using TetrahedronHyperelasticityFEMForceField<DataTypes>::m_myMaterial;

    void updateTangentMatrix();
};

using sofa::defaulttype::Vec3dTypes;
using sofa::defaulttype::Vec3fTypes;

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_CPP)
extern template class SOFA_MODELORDERREDUCTION_API HyperReducedTetrahedronHyperelasticityFEMForceField<Vec3Types>;
#endif // !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_CPP)
} // namespace sofa::component::forcefield
