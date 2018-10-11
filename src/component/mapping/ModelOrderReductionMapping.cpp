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
static int ModelOrderReductionMappingClass = core::RegisterObject("Reduced model")
#ifdef SOFA_WITH_DOUBLE
        .add< ModelOrderReductionMapping< Vec1dTypes, Vec3dTypes > >(true)
#endif

#ifdef SOFA_WITH_FLOAT
        .add< ModelOrderReductionMapping< Vec1fTypes, Vec3fTypes > >()
#endif

;



#ifdef SOFA_WITH_DOUBLE
template class SOFA_BASE_MECHANICS_API ModelOrderReductionMapping< Vec1dTypes, Vec3dTypes >;
#endif

#ifdef SOFA_WITH_FLOAT
template class SOFA_BASE_MECHANICS_API ModelOrderReductionMapping< Vec1fTypes, Vec3fTypes >;
#endif


} // namespace mapping

} // namespace component

} // namespace sofa



