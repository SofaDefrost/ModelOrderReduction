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
#include <sofa/component/solidmechanics/fem/elastic/TetrahedronFEMForceField.h>

#define SIMPLEFEM_COLORMAP
#define SOFAHYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_COLORMAP


#include <sofa/helper/ColorMap.h>


namespace sofa::component::forcefield
{
namespace  {
using sofa::component::solidmechanics::fem::elastic::TetrahedronFEMForceField;
}



/** This forceField is the HyperReduced version of TetrahedronFEMForceField.
*   At the moment, it is only implemented for the "large" method (i.e not for small, polar or svd).
*/
template<class DataTypes>
class HyperReducedTetrahedronFEMForceField : public virtual TetrahedronFEMForceField<DataTypes>, public modelorderreduction::HyperReducedHelper
{
public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedTetrahedronFEMForceField, DataTypes), SOFA_TEMPLATE(TetrahedronFEMForceField, DataTypes), HyperReducedHelper);

    typedef typename core::behavior::ForceField<DataTypes> InheritForceField;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::VecReal VecReal;
    typedef VecCoord Vector;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename Coord::value_type Real;

    typedef core::objectmodel::Data<VecDeriv>    DataVecDeriv;
    typedef core::objectmodel::Data<VecCoord>    DataVecCoord;

    typedef sofa::Index Index;
    typedef core::topology::BaseMeshTopology::Tetra Element;
    typedef core::topology::BaseMeshTopology::SeqTetrahedra VecElement;
    typedef core::topology::BaseMeshTopology::Tetrahedron Tetrahedron;
    using index_type = sofa::Index;

    enum { SMALL = 0,   ///< Symbol of small displacements tetrahedron solver
            LARGE = 1,   ///< Symbol of corotational large displacements tetrahedron solver based on a QR decomposition    -> Nesme et al 2005 "Efficient, Physically Plausible Finite Elements"
            POLAR = 2,   ///< Symbol of corotational large displacements tetrahedron solver based on a polar decomposition -> Muller et al 2004 "Interactive Virtual Materials"
            SVD = 3      ///< Symbol of corotational large displacements tetrahedron solver based on a SVD decomposition   -> inspired from Irving et al 2004 "Invertible Finite Element for Robust Simulation of Large Deformation"
         };

protected:

    /// @name Per element (tetrahedron) data
    /// @{

    /// Displacement vector (deformation of the 4 corners of a tetrahedron
    typedef type::VecNoInit<12, Real> Displacement;

    /// Material stiffness matrix of a tetrahedron
    typedef type::Mat<6, 6, Real> MaterialStiffness;

    /// Strain-displacement matrix
    typedef type::Mat<12, 6, Real> StrainDisplacement;


    type::MatNoInit<3, 3, Real> R0;

    /// Rigid transformation (rotation) matrix
    typedef type::MatNoInit<3, 3, Real> Transformation;

    /// Stiffness matrix ( = RJKJtRt  with K the Material stiffness matrix, J the strain-displacement matrix, and R the transformation matrix if any )
    typedef type::Mat<12, 12, Real> StiffnessMatrix;

    /// Symmetrical tensor written as a vector following the Voigt notation
    typedef type::VecNoInit<6,Real> VoigtTensor;

    /// @}

    /// Vector of material stiffness of each tetrahedron
    typedef type::vector<MaterialStiffness> VecMaterialStiffness;
    typedef type::vector<StrainDisplacement> VecStrainDisplacement;  ///< a vector of strain-displacement matrices

    /// structures used to compute vonMises stress
    typedef type::Mat<4, 4, Real> Mat44;
    typedef type::Mat<3, 3, Real> Mat33;
    typedef type::Mat<4, 3, Real> Mat43;

    /// Vector of material stiffness matrices of each tetrahedron
    using TetrahedronFEMForceField<DataTypes>::materialsStiffnesses;
    using TetrahedronFEMForceField<DataTypes>::strainDisplacements;   ///< the strain-displacement matrices vector
    using TetrahedronFEMForceField<DataTypes>::rotations;

    using TetrahedronFEMForceField<DataTypes>::_plasticStrains; ///< one plastic strain per element

    using TetrahedronFEMForceField<DataTypes>::_showVonMisesStressPerElement;
    /// @name Full system matrix assembly support
    /// @{

    typedef std::pair<index_type,Real> Col_Value;
    typedef type::vector< Col_Value > CompressedValue;
    typedef type::vector< CompressedValue > CompressedMatrix;

    using TetrahedronFEMForceField<DataTypes>::_stiffnesses;

    /// @}

    using TetrahedronFEMForceField<DataTypes>::m_potentialEnergy;

    using TetrahedronFEMForceField<DataTypes>::m_topology;
    using TetrahedronFEMForceField<DataTypes>::_indexedElements;
    using TetrahedronFEMForceField<DataTypes>::needUpdateTopology;

    using TetrahedronFEMForceField<DataTypes>::data;

    using TetrahedronFEMForceField<DataTypes>::m_restVolume;

public:

    using TetrahedronFEMForceField<DataTypes>::_initialPoints; ///< the initial positions of the points
    using TetrahedronFEMForceField<DataTypes>::method;
    using TetrahedronFEMForceField<DataTypes>::f_method; ///< the computation method of the displacements

    using TetrahedronFEMForceField<DataTypes>:: _poissonRatio;
    using TetrahedronFEMForceField<DataTypes>::_youngModulus;
    using TetrahedronFEMForceField<DataTypes>::_localStiffnessFactor;
    using TetrahedronFEMForceField<DataTypes>::_updateStiffnessMatrix;
    using TetrahedronFEMForceField<DataTypes>::_assembling;


    /// @name Plasticity such as "Interactive Virtual Materials", Muller & Gross, GI 2004
    /// @{
    using TetrahedronFEMForceField<DataTypes>::_plasticMaxThreshold;
    using TetrahedronFEMForceField<DataTypes>::_plasticYieldThreshold;
    using TetrahedronFEMForceField<DataTypes>::_plasticCreep; ///< this parameters is different from the article, here it includes the multiplication by dt
    /// @}


    using TetrahedronFEMForceField<DataTypes>::_gatherPt; //use in GPU version
    using TetrahedronFEMForceField<DataTypes>::_gatherBsize; //use in GPU version
    using TetrahedronFEMForceField<DataTypes>::drawHeterogeneousTetra;

    using TetrahedronFEMForceField<DataTypes>::minYoung;
    using TetrahedronFEMForceField<DataTypes>::maxYoung;

    /// to compute vonMises stress for visualization
    /// two options: either using corotational strain (TODO)
    ///              or full Green strain tensor (which must be therefore computed for each element and requires some pre-calculations in reinit)

    using TetrahedronFEMForceField<DataTypes>::elemLambda;
    using TetrahedronFEMForceField<DataTypes>::elemMu;
    using TetrahedronFEMForceField<DataTypes>::elemShapeFun;

    using TetrahedronFEMForceField<DataTypes>::prevMaxStress;


    using TetrahedronFEMForceField<DataTypes>::_computeVonMisesStress;
    using TetrahedronFEMForceField<DataTypes>::_vonMisesPerElement;
    using TetrahedronFEMForceField<DataTypes>::_vonMisesPerNode;
    using TetrahedronFEMForceField<DataTypes>::_vonMisesStressColors;


#ifdef SOFAHYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_COLORMAP
    using TetrahedronFEMForceField<DataTypes>::m_VonMisesColorMap;

    using TetrahedronFEMForceField<DataTypes>::_showStressColorMap;
    using TetrahedronFEMForceField<DataTypes>::_showStressAlpha;
    using TetrahedronFEMForceField<DataTypes>::_showVonMisesStressPerNode;
#endif
    /// Suppress field for save as function
    using TetrahedronFEMForceField<DataTypes>::_updateStiffness;

    using TetrahedronFEMForceField<DataTypes>::elemDisplacements;

    using TetrahedronFEMForceField<DataTypes>::updateVonMisesStress;
    using TetrahedronFEMForceField<DataTypes>::d_componentState;

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


protected:
    HyperReducedTetrahedronFEMForceField()
    {
        _poissonRatio.setRequired(true);
        _youngModulus.setRequired(true);
        _youngModulus.beginEdit()->push_back((Real)5000.);
        _youngModulus.endEdit();
        _youngModulus.unset();

        data.initPtrData(this);
        this->addAlias(&_assembling, "assembling");
        minYoung = 0.0;
        maxYoung = 0.0;

    }

public:

    virtual void init() override;

    virtual void addForce(const core::MechanicalParams* mparams, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& d_v) override;
    virtual void addDForce(const core::MechanicalParams* mparams, DataVecDeriv& d_df, const DataVecDeriv& d_dx) override;

    // Make other overloaded version of getPotentialEnergy() to show up in subclass.
    using TetrahedronFEMForceField<DataTypes>::getPotentialEnergy;

    virtual void buildStiffnessMatrix(core::behavior::StiffnessMatrix* matrix) override;
    void draw(const core::visual::VisualParams* vparams) override;

protected:

    ////////////// small displacements method
    void accumulateForceSmall( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex );
    void applyStiffnessSmall( Vector& f, const Vector& x, int i=0, Index a=0,Index b=1,Index c=2,Index d=3, SReal fact=1.0  );

    ////////////// large displacements method
    using TetrahedronFEMForceField<DataTypes>::_rotatedInitialElements;   ///< The initials positions in its frame
    using TetrahedronFEMForceField<DataTypes>::_initialRotations;
    void accumulateForceLarge( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex );

    ////////////// polar decomposition method
    using TetrahedronFEMForceField<DataTypes>::_rotationIdx;
    void accumulateForcePolar( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex );

    ////////////// svd decomposition method
    using TetrahedronFEMForceField<DataTypes>::_initialTransformation;
    void accumulateForceSVD( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex );

    void applyStiffnessCorotational( Vector& f, const Vector& x, int i=0, Index a=0,Index b=1,Index c=2,Index d=3, SReal fact=1.0  );


};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_CPP)
extern template class SOFA_MODELORDERREDUCTION_API HyperReducedTetrahedronFEMForceField<defaulttype::Vec3Types>;
#endif
} // namespace sofa::component::forcefield
