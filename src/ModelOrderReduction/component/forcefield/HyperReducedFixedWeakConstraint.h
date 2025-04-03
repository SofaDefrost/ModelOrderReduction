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
#include <sofa/component/solidmechanics/spring/FixedWeakConstraint.h>

namespace sofa::core::behavior
{
template< class T > class MechanicalState;
} // namespace sofa::core::behavior

namespace sofa::component::solidmechanics::spring
{

/**
* @brief This class describes a simple elastic springs ForceField between DOFs positions and rest positions.
*
* Springs are applied to given degrees of freedom between their current positions and their rest shape positions.
* An external MechanicalState reference can also be passed to the ForceField as rest shape position.
*/
template<class DataTypes>
class HyperReducedFixedWeakConstraint : public virtual FixedWeakConstraint<DataTypes>, public modelorderreduction::HyperReducedHelper
{
public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedFixedWeakConstraint, DataTypes), SOFA_TEMPLATE(FixedWeakConstraint, DataTypes), HyperReducedHelper);

    typedef HyperReducedHelper Inherit;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::CPos CPos;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename DataTypes::Real Real;
    typedef type::vector< sofa::Index > VecIndex;
    typedef type::vector< Real >	 VecReal;

    typedef core::objectmodel::Data<VecCoord> DataVecCoord;
    typedef core::objectmodel::Data<VecDeriv> DataVecDeriv;

    ////////////////////////// Inherited attributes ////////////////////////////
    /// https://gcc.gnu.org/onlinedocs/gcc/Name-lookup.html
    /// Bring inherited attributes and function in the current lookup context.
    /// otherwise any access to the base::attribute would require
    /// the "this->" approach.

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


    using FixedWeakConstraint<DataTypes>::d_indices;
    using FixedWeakConstraint<DataTypes>::d_stiffness;
    using FixedWeakConstraint<DataTypes>::d_angularStiffness;
    using FixedWeakConstraint<DataTypes>::d_fixAll;
    using FixedWeakConstraint<DataTypes>::d_drawSpring;
    using FixedWeakConstraint<DataTypes>::d_springColor;
    using FixedWeakConstraint<DataTypes>::l_topology;

protected:
    HyperReducedFixedWeakConstraint();

public:
    /// BaseObject initialization method.
    void bwdInit() override ;

    /// Add the forces.
    virtual void addForce(const core::MechanicalParams* mparams, DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv& v) override;

    virtual void addDForce(const core::MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx) override;

    void buildStiffnessMatrix(core::behavior::StiffnessMatrix* /* matrix */) override;

    virtual void draw(const core::visual::VisualParams* vparams) override;
};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDFIXEDWEAKCONSTRAINT_CPP)

extern template class SOFA_MODELORDERREDUCTION_API HyperReducedFixedWeakConstraint<sofa::defaulttype::Vec3Types>;

#endif
} // namespace sofa::component::solidmechanics::spring
