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
#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_H
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_H

#include "HyperReducedHelper.h"
#include <SofaDeformable/RestShapeSpringsForceField.h>
namespace sofa
{
namespace core
{
namespace behavior
{
template< class T > class MechanicalState;

} // namespace behavior
} // namespace core
} // namespace sofa

namespace sofa
{

namespace component
{

namespace forcefield
{

/**
* @brief This class describes a simple elastic springs ForceField between DOFs positions and rest positions.
*
* Springs are applied to given degrees of freedom between their current positions and their rest shape positions.
* An external MechanicalState reference can also be passed to the ForceField as rest shape position.
*/
template<class DataTypes>
class HyperReducedRestShapeSpringsForceField : public virtual RestShapeSpringsForceField<DataTypes>, public HyperReducedHelper
{
public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedRestShapeSpringsForceField, DataTypes), SOFA_TEMPLATE(RestShapeSpringsForceField, DataTypes), HyperReducedHelper);

    typedef HyperReducedHelper Inherit;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::CPos CPos;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename DataTypes::Real Real;
    typedef helper::vector< unsigned int > VecIndex;
    typedef helper::vector< Real >	 VecReal;

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


    using RestShapeSpringsForceField<DataTypes>::points;
    using RestShapeSpringsForceField<DataTypes>::stiffness;
    using RestShapeSpringsForceField<DataTypes>::angularStiffness;
    using RestShapeSpringsForceField<DataTypes>::pivotPoints;
    using RestShapeSpringsForceField<DataTypes>::external_points;
    using RestShapeSpringsForceField<DataTypes>::recompute_indices;
    using RestShapeSpringsForceField<DataTypes>::drawSpring;
    using RestShapeSpringsForceField<DataTypes>::springColor;
    using RestShapeSpringsForceField<DataTypes>::restMState;

    using RestShapeSpringsForceField<DataTypes>::matS;

protected:
    HyperReducedRestShapeSpringsForceField();

public:
    /// BaseObject initialization method.
    void bwdInit() override ;
    virtual void parse(core::objectmodel::BaseObjectDescription *arg) override ;
    virtual void reinit() override ;

    /// Add the forces.
    virtual void addForce(const core::MechanicalParams* mparams, DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv& v) override;

    virtual void addDForce(const core::MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx) override;

    virtual SReal getPotentialEnergy(const core::MechanicalParams* mparams, const DataVecCoord& x) const override
    {
        SOFA_UNUSED(mparams);
        SOFA_UNUSED(x);

        msg_error() << "Get potentialEnergy not implemented";
        return 0.0;
    }

    /// Brings ForceField contribution to the global system stiffness matrix.
    virtual void addKToMatrix(const core::MechanicalParams* mparams, const sofa::core::behavior::MultiMatrixAccessor* matrix ) override;

    virtual void addSubKToMatrix(const core::MechanicalParams* mparams, const sofa::core::behavior::MultiMatrixAccessor* matrix, const helper::vector<unsigned> & addSubIndex ) override;

    virtual void draw(const core::visual::VisualParams* vparams) override;

protected :

    using RestShapeSpringsForceField<DataTypes>::m_indices;
    using RestShapeSpringsForceField<DataTypes>::k;
    using RestShapeSpringsForceField<DataTypes>::m_ext_indices;
    using RestShapeSpringsForceField<DataTypes>::m_pivots;

    using RestShapeSpringsForceField<DataTypes>::lastUpdatedStep;

private :

    bool useRestMState; /// An external MechanicalState is used as rest reference.
};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGSFORCEFIELD_CPP)

#ifndef SOFA_FLOAT
extern template class SOFA_DEFORMABLE_API HyperReducedRestShapeSpringsForceField<sofa::defaulttype::Vec3dTypes>;
#endif
#ifndef SOFA_DOUBLE
extern template class SOFA_DEFORMABLE_API HyperReducedRestShapeSpringsForceField<sofa::defaulttype::Vec3fTypes>;
#endif

#endif

} // namespace forcefield

} // namespace component

} // namespace sofa

#endif // SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_H
