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
#include <sofa/component/solidmechanics/fem/elastic/TetrahedralCorotationalFEMForceField.h>

namespace sofa::component::solidmechanics::fem::elastic
{

/** Compute Finite Element forces based on tetrahedral elements.
 */
template<class DataTypes>
class HyperReducedTetrahedralCorotationalFEMForceField : public virtual TetrahedralCorotationalFEMForceField<DataTypes>, public modelorderreduction::HyperReducedHelper
{
public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedTetrahedralCorotationalFEMForceField, DataTypes), SOFA_TEMPLATE(TetrahedralCorotationalFEMForceField, DataTypes),HyperReducedHelper);

    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::VecReal VecReal;
    typedef VecCoord Vector;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename Coord::value_type Real;

    typedef core::objectmodel::Data<VecDeriv>    DataVecDeriv;
    typedef core::objectmodel::Data<VecCoord>    DataVecCoord;

    enum { SMALL = 0, ///< Symbol of small displacements tetrahedron solver
            LARGE = 1, ///< Symbol of large displacements tetrahedron solver
            POLAR = 2  ///< Symbol of polar displacements tetrahedron solver
         };
protected:

    /// @name Per element (tetrahedron) data
    /// @{

    /// Displacement vector (deformation of the 4 corners of a tetrahedron
    typedef type::VecNoInit<12, Real> Displacement;

    /// Material stiffness matrix of a tetrahedron
    typedef type::Mat<6, 6, Real> MaterialStiffness;

    /// Strain-displacement matrix
    typedef type::Mat<12, 6, Real> StrainDisplacementTransposed;

    /// Rigid transformation (rotation) matrix
    typedef type::MatNoInit<3, 3, Real> Transformation;

    /// Stiffness matrix ( = RJKJtRt  with K the Material stiffness matrix, J the strain-displacement matrix, and R the transformation matrix if any )
    typedef type::Mat<12, 12, Real> StiffnessMatrix;

    /// @}

    /// container that stotes all requires information for each tetrahedron
    using TetrahedralCorotationalFEMForceField<DataTypes>::tetrahedronInfo;

    /// @name Full system matrix assembly support
    /// @{

    typedef std::pair<int,Real> Col_Value;
    typedef type::vector< Col_Value > CompressedValue;
    typedef type::vector< CompressedValue > CompressedMatrix;
    typedef unsigned int Index;

    using TetrahedralCorotationalFEMForceField<DataTypes>::_stiffnesses;
    /// @}

    using TetrahedralCorotationalFEMForceField<DataTypes>::m_potentialEnergy;

    using TetrahedralCorotationalFEMForceField<DataTypes>::_topology;

public:
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


    using TetrahedralCorotationalFEMForceField<DataTypes>::method;
    using TetrahedralCorotationalFEMForceField<DataTypes>::f_method; ///< the computation method of the displacements
    using TetrahedralCorotationalFEMForceField<DataTypes>::_poissonRatio; ///< FEM Poisson Ratio
    using TetrahedralCorotationalFEMForceField<DataTypes>::_youngModulus; ///< FEM Young Modulus
    using TetrahedralCorotationalFEMForceField<DataTypes>::_localStiffnessFactor; ///< Allow specification of different stiffness per element. If there are N element and M values are specified, the youngModulus factor for element i would be localStiffnessFactor[i*M/N]
    using TetrahedralCorotationalFEMForceField<DataTypes>::_updateStiffnessMatrix;
    using TetrahedralCorotationalFEMForceField<DataTypes>::_assembling;
    using TetrahedralCorotationalFEMForceField<DataTypes>::f_drawing; ///<  draw the forcefield if true
    using TetrahedralCorotationalFEMForceField<DataTypes>::_displayWholeVolume;
    using TetrahedralCorotationalFEMForceField<DataTypes>::drawColor1; ///<  draw color for faces 1
    using TetrahedralCorotationalFEMForceField<DataTypes>::drawColor2; ///<  draw color for faces 2
    using TetrahedralCorotationalFEMForceField<DataTypes>::drawColor3; ///<  draw color for faces 3
    using TetrahedralCorotationalFEMForceField<DataTypes>::drawColor4; ///<  draw color for faces 4
    using TetrahedralCorotationalFEMForceField<DataTypes>::_volumeGraph;
protected:
    HyperReducedTetrahedralCorotationalFEMForceField();
public:

    virtual void init() override;

    virtual void addForce(const core::MechanicalParams* mparams, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& d_v) override;
    virtual void addDForce(const core::MechanicalParams* mparams, DataVecDeriv& d_df, const DataVecDeriv& d_dx) override;

    void buildStiffnessMatrix(core::behavior::StiffnessMatrix* /* matrix */) override;

    void draw(const core::visual::VisualParams* vparams) override;

protected:

    ////////////// small displacements method
    void accumulateForceSmall( Vector& f, const Vector & p, Index elementIndex );
    void applyStiffnessSmall( Vector& f, const Vector& x, int i=0, Index a=0,Index b=1,Index c=2,Index d=3, SReal fact=1.0 );

    ////////////// large displacements method
    void accumulateForceLarge( Vector& f, const Vector & p, Index elementIndex );
    void applyStiffnessLarge( Vector& f, const Vector& x, int i=0, Index a=0,Index b=1,Index c=2,Index d=3, SReal fact=1.0 );

    ////////////// polar decomposition method
    void accumulateForcePolar( Vector& f, const Vector & p,Index elementIndex );
    void applyStiffnessPolar( Vector& f, const Vector& x, int i=0, Index a=0,Index b=1,Index c=2,Index d=3, SReal fact=1.0 );

};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRALCOROTATIONALFEMFORCEFIELD_CPP)
extern template class SOFA_MODELORDERREDUCTION_API HyperReducedTetrahedralCorotationalFEMForceField<sofa::defaulttype::Vec3Types>;
#endif // !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRALCOROTATIONALFEMFORCEFIELD_CPP)
} // namespace sofa::component::solidmechanics::fem::elastic
