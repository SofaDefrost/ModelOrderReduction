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
#include "HyperReducedFixedWeakConstraint.h"

#include <ModelOrderReduction/config.h>

#include <ModelOrderReduction/component/forcefield/HyperReducedHelper.h>
#include <ModelOrderReduction/component/forcefield/HyperReducedFixedWeakConstraint.h>
#include <sofa/component/solidmechanics/spring/RestShapeSpringsForceField.h>

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
class HyperReducedRestShapeSpringsForceField : public virtual RestShapeSpringsForceField<DataTypes>, public virtual modelorderreduction::HyperReducedHelper,  public  HyperReducedFixedWeakConstraint<DataTypes>
{
public:
    SOFA_CLASS3(SOFA_TEMPLATE(HyperReducedRestShapeSpringsForceField, DataTypes), SOFA_TEMPLATE(HyperReducedFixedWeakConstraint, DataTypes), SOFA_TEMPLATE(RestShapeSpringsForceField, DataTypes), HyperReducedHelper);

protected:
    HyperReducedRestShapeSpringsForceField() = default;
public:
    virtual void init(){ RestShapeSpringsForceField<DataTypes>::init(); }
    virtual void bwdInit(){ RestShapeSpringsForceField<DataTypes>::bwdInit(); }
    virtual void reinit(){ RestShapeSpringsForceField<DataTypes>::reinit(); }
    virtual void draw(const sofa::core::visual::VisualParams* vps){ RestShapeSpringsForceField<DataTypes>::draw(vps); }
    virtual bool insertInNode(sofa::core::objectmodel::BaseNode* node){ RestShapeSpringsForceField<DataTypes>::insertInNode(node); }
    virtual bool removeInNode(sofa::core::objectmodel::BaseNode* node){ RestShapeSpringsForceField<DataTypes>::removeInNode(node); }
    virtual sofa::core::behavior::BaseForceField* toBaseForceField(){return RestShapeSpringsForceField<DataTypes>::toBaseForceField();}
    virtual const sofa::core::behavior::BaseForceField* toBaseForceField() const {return RestShapeSpringsForceField<DataTypes>::toBaseForceField();}

};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGSFORCEFIELD_CPP)

extern template class SOFA_MODELORDERREDUCTION_API HyperReducedRestShapeSpringsForceField<sofa::defaulttype::Vec3Types>;

#endif
} // namespace sofa::component::solidmechanics::spring
