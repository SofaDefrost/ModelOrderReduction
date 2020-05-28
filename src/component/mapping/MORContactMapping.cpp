/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, development version     *
*                (c) 2006-2019 INRIA, USTL, UJF, CNRS, MGH                    *
*                                                                             *
* This program is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This program is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this program. If not, see <http://www.gnu.org/licenses/>.        *
*******************************************************************************
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
******************************************************************************/
#define SOFA_COMPONENT_MAPPING_MORCONTACTMAPPING_CPP
#include "MORContactMapping.inl"
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
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


// Register in the Factory
int MORContactMappingClass = core::RegisterObject("Special case of mapping where the child points are the same as the parent points")
        .add< MORContactMapping< Vec3dTypes, Vec3dTypes > >()
        .add< MORContactMapping< Vec2Types, Vec2Types > >()
        .add< MORContactMapping< Vec1Types, Vec1Types > >()
        .add< MORContactMapping< Vec6Types, Vec3dTypes > >()
        .add< MORContactMapping< Vec6Types, Vec6Types > >()
        .add< MORContactMapping< Rigid3Types, Rigid3Types > >()
        .add< MORContactMapping< Rigid2Types, Rigid2Types > >()



// Rigid -> Vec
        .add< MORContactMapping< Rigid3Types, Vec3dTypes > >()
        .add< MORContactMapping< Rigid2Types, Vec2Types > >()

        ;


template class SOFA_BASE_MECHANICS_API MORContactMapping< Vec3dTypes, Vec3dTypes >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Vec2Types, Vec2Types >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Vec1Types, Vec1Types >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Vec6Types, Vec3dTypes >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Vec6Types, Vec6Types >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Rigid3Types, Rigid3Types >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Rigid2Types, Rigid2Types >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Rigid3Types, Vec3dTypes >;
template class SOFA_BASE_MECHANICS_API MORContactMapping< Rigid2Types, Vec2Types >;





} // namespace mapping

} // namespace component

} // namespace sofa

