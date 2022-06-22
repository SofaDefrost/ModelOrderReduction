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
#include "MORFrictionContact.inl"
#include <sofa/component/collision/response/mapper/RigidContactMapper.inl>
#include <sofa/component/collision/response/mapper/BarycentricContactMapper.inl>


namespace sofa::component::collision::geometry
{

using sofa::core::collision::Contact;
using sofa::defaulttype::Vec3Types;
using sofa::defaulttype::Rigid3Types;

Creator<Contact::Factory, MORFrictionContact<PointCollisionModel<Vec3Types>, PointCollisionModel<Vec3Types>> > PointPointMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<LineCollisionModel<Vec3Types>, SphereCollisionModel<Vec3Types>> > LineSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<LineCollisionModel<Vec3Types>, PointCollisionModel<Vec3Types>> > LinePointMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<LineCollisionModel<Vec3Types>, LineCollisionModel<Vec3Types>> > LineLineMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<TriangleCollisionModel<Vec3Types>, SphereCollisionModel<Vec3Types>> > TriangleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<TriangleCollisionModel<Vec3Types>, PointCollisionModel<Vec3Types>> > TrianglePointMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<TriangleCollisionModel<Vec3Types>, LineCollisionModel<Vec3Types>> > TriangleLineMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<TriangleCollisionModel<Vec3Types>, TriangleCollisionModel<Vec3Types>> > TriangleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<SphereCollisionModel<Vec3Types>, SphereCollisionModel<Vec3Types>> > SphereSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<SphereCollisionModel<Vec3Types>, PointCollisionModel<Vec3Types>> > SpherePointMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<RigidSphereModel, RigidSphereModel> > RigidSphereRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<SphereCollisionModel<Vec3Types>, RigidSphereModel> > SphereRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<LineCollisionModel<Vec3Types>, RigidSphereModel> > LineRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<TriangleCollisionModel<Vec3Types>, RigidSphereModel> > TriangleRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<Contact::Factory, MORFrictionContact<RigidSphereModel, PointCollisionModel<Vec3Types>> > RigidSpherePointMORFrictionContactClass("MORFrictionContact",true);


} // namespace sofa::component::collision
