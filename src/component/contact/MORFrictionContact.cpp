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
#include <SofaMeshCollision/RigidContactMapper.inl>
#include <SofaMeshCollision/BarycentricContactMapper.inl>

#include <SofaMiscCollision/CapsuleContactMapper.h>
#include <SofaMiscCollision/OBBContactMapper.h>

namespace sofa
{

namespace component
{

namespace collision
{

using namespace defaulttype;
using namespace sofa::helper;
using simulation::Node;

Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<PointCollisionModel<sofa::defaulttype::Vec3Types>, PointCollisionModel<sofa::defaulttype::Vec3Types>> > PointPointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineCollisionModel<sofa::defaulttype::Vec3Types>, SphereCollisionModel<sofa::defaulttype::Vec3Types>> > LineSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineCollisionModel<sofa::defaulttype::Vec3Types>, PointCollisionModel<sofa::defaulttype::Vec3Types>> > LinePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineCollisionModel<sofa::defaulttype::Vec3Types>, LineCollisionModel<sofa::defaulttype::Vec3Types>> > LineLineMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleCollisionModel<sofa::defaulttype::Vec3Types>, SphereCollisionModel<sofa::defaulttype::Vec3Types>> > TriangleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleCollisionModel<sofa::defaulttype::Vec3Types>, PointCollisionModel<sofa::defaulttype::Vec3Types>> > TrianglePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleCollisionModel<sofa::defaulttype::Vec3Types>, LineCollisionModel<sofa::defaulttype::Vec3Types>> > TriangleLineMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleCollisionModel<sofa::defaulttype::Vec3Types>, TriangleCollisionModel<sofa::defaulttype::Vec3Types>> > TriangleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereCollisionModel<sofa::defaulttype::Vec3Types>, SphereCollisionModel<sofa::defaulttype::Vec3Types>> > SphereSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereCollisionModel<sofa::defaulttype::Vec3Types>, PointCollisionModel<sofa::defaulttype::Vec3Types>> > SpherePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Vec3Types>, CapsuleCollisionModel<sofa::defaulttype::Vec3Types>> > CapsuleCapsuleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Vec3Types>, TriangleCollisionModel<sofa::defaulttype::Vec3Types>> > CapsuleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Vec3Types>, SphereCollisionModel<sofa::defaulttype::Vec3Types>> > CapsuleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<OBBCollisionModel<sofa::defaulttype::Rigid3Types>, OBBCollisionModel<sofa::defaulttype::Rigid3Types>> > OBBOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereCollisionModel<sofa::defaulttype::Vec3Types>, OBBCollisionModel<sofa::defaulttype::Rigid3Types>> > SphereOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Vec3Types>, OBBCollisionModel<sofa::defaulttype::Rigid3Types>> > CapsuleOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleCollisionModel<sofa::defaulttype::Vec3Types>, OBBCollisionModel<sofa::defaulttype::Rigid3Types>> > TriangleOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidSphereModel, RigidSphereModel> > RigidSphereRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereCollisionModel<sofa::defaulttype::Vec3Types>, RigidSphereModel> > SphereRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineCollisionModel<sofa::defaulttype::Vec3Types>, RigidSphereModel> > LineRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleCollisionModel<sofa::defaulttype::Vec3Types>, RigidSphereModel> > TriangleRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidSphereModel, PointCollisionModel<sofa::defaulttype::Vec3Types>> > RigidSpherePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Vec3Types>, RigidSphereModel> > CapsuleRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidSphereModel, OBBCollisionModel<sofa::defaulttype::Rigid3Types>> > RigidSphereOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>, CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>> > RigidCapsuleRigidCapsuleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Vec3Types>, CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>> > CapsuleRigidCapsuleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>, TriangleCollisionModel<sofa::defaulttype::Vec3Types>> > RigidCapsuleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>, SphereCollisionModel<sofa::defaulttype::Vec3Types>> > RigidCapsuleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>, OBBCollisionModel<sofa::defaulttype::Rigid3Types>> > RigidCapsuleOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleCollisionModel<sofa::defaulttype::Rigid3Types>, RigidSphereModel> > RigidCapsuleRigidSphereMORFrictionContactClass("MORFrictionContact",true);


} // namespace collision

} // namespace component

} // namespace sofa
