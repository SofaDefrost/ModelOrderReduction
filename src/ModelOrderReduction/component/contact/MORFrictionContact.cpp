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


namespace sofa
{

namespace component
{

namespace collision
{

using namespace defaulttype;
using namespace sofa::helper;
using simulation::Node;

Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<PointModel, PointModel> > PointPointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineModel, SphereModel> > LineSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineModel, PointModel> > LinePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineModel, LineModel> > LineLineMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleModel, SphereModel> > TriangleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleModel, PointModel> > TrianglePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleModel, LineModel> > TriangleLineMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleModel, TriangleModel> > TriangleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereModel, SphereModel> > SphereSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereModel, PointModel> > SpherePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleModel, CapsuleModel> > CapsuleCapsuleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleModel, TriangleModel> > CapsuleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleModel, SphereModel> > CapsuleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<OBBModel, OBBModel> > OBBOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereModel, OBBModel> > SphereOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleModel, OBBModel> > CapsuleOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleModel, OBBModel> > TriangleOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidSphereModel, RigidSphereModel> > RigidSphereRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<SphereModel, RigidSphereModel> > SphereRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<LineModel, RigidSphereModel> > LineRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<TriangleModel, RigidSphereModel> > TriangleRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidSphereModel, PointModel> > RigidSpherePointMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleModel, RigidSphereModel> > CapsuleRigidSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidSphereModel, OBBModel> > RigidSphereOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidCapsuleModel, RigidCapsuleModel> > RigidCapsuleRigidCapsuleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<CapsuleModel, RigidCapsuleModel> > CapsuleRigidCapsuleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidCapsuleModel, TriangleModel> > RigidCapsuleTriangleMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidCapsuleModel, SphereModel> > RigidCapsuleSphereMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidCapsuleModel, OBBModel> > RigidCapsuleOBBMORFrictionContactClass("MORFrictionContact",true);
Creator<sofa::core::collision::Contact::Factory, MORFrictionContact<RigidCapsuleModel, RigidSphereModel> > RigidCapsuleRigidSphereMORFrictionContactClass("MORFrictionContact",true);


} // namespace collision

} // namespace component

} // namespace sofa
