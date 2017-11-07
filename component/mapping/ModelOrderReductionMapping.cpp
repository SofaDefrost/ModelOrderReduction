/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, development version     *
*                (c) 2006-2015 INRIA, USTL, UJF, CNRS, MGH                    *
*                                                                             *
* This library is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This library is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this library; if not, write to the Free Software Foundation,     *
* Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.          *
*******************************************************************************
*                               SOFA :: Modules                               *
*                                                                             *
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
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
int ModelOrderReductionMappingClass = core::RegisterObject("Reduced model")
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



