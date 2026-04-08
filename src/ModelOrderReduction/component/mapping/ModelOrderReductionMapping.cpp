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
#define SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_CPP
#include "ModelOrderReductionMapping.inl"
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/core/ObjectFactory.h>

namespace sofa
{

namespace component
{

namespace mapping
{

using namespace sofa::defaulttype;
using namespace core;
using namespace core::behavior;


SOFA_DECL_CLASS(ModelOrderReductionMapping)

// Register in the Factory
void registerModelOrderReductionMapping(sofa::core::ObjectFactory* factory)
{
    factory->registerObjects(sofa::core::ObjectRegistrationData("Reduced model")
    .add< ModelOrderReductionMapping< Vec1Types, Vec3Types > >(true));
}

template class SOFA_MODELORDERREDUCTION_API ModelOrderReductionMapping< Vec1Types, Vec3Types >;

} // namespace mapping

} // namespace component

} // namespace sofa



