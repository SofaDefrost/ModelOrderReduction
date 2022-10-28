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
#ifndef MOR_MORFRICTIONCONTACT_INL
#define MOR_MORFRICTIONCONTACT_INL

#include <sofa/component/collision/response/contact/FrictionContact.inl>
#include <ModelOrderReduction/component/contact/MORFrictionContact.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/component/collision/response/contact/DefaultContactManager.h>
#include <sofa/component/collision/response/mapper/BarycentricContactMapper.h>
#include <sofa/component/collision/response/mapper/IdentityContactMapper.h>
#include <sofa/component/collision/response/mapper/RigidContactMapper.inl>
#include <sofa/simulation/Node.h>
#include <iostream>

namespace sofa::component::collision::response::contact
{

template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::MORFrictionContact()
    : MORFrictionContact(nullptr, nullptr, nullptr)
{
}

//template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
//MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::MORFrictionContact(CollisionModel1* model1_, CollisionModel2* model2_, Intersection* intersectionMethod_)
//    : FrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>(model1_, model2_, intersectionMethod_)
//{
//}

template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::MORFrictionContact(CollisionModel1* model1_, CollisionModel2* model2_, Intersection* intersectionMethod_)
    : FrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>(model1_, model2_, intersectionMethod_)
    , d_lambdaModesPath (initData(&d_lambdaModesPath, "lambdaModesPath", "path to the file containing the lambda modes"))
    , d_lambdaModesCoeffsPath (initData(&d_lambdaModesCoeffsPath, "lambdaModesCoeffsPath", "path to the file containing the coefficients of lambda modes"))
{
}

template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::~MORFrictionContact()
{
}

template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
void MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::cleanup()
{
    msg_warning() << "Cleaning up MORfrictionContact!!!";
    if (m_constraint)
    {
        msg_warning() << "plop!";
        m_constraint->cleanup();
        msg_warning() << "plip!";
        if (parent != NULL){
            msg_warning() << "Really Cleaning up frictionContact!!!";
            parent->removeObject(m_constraint);}
        msg_warning() << "plap!";
        parent = NULL;
        sofa::component::constraint::lagrangian::model::MORUnilateralInteractionConstraint<sofa::defaulttype::Vec3Types>::SPtr tmp( dynamic_cast<sofa::component::constraint::lagrangian::model::MORUnilateralInteractionConstraint<sofa::defaulttype::Vec3Types>*>(m_constraint.get()) );
        tmp.reset();
//        m_MORconstraint.reset();
        msg_warning() << "plup!";
        mapper1.cleanup();
        msg_warning() << "plep!";
        if (!selfCollision)
            mapper2.cleanup();
        msg_warning() << "plyp!";
    }

    contacts.clear();
    mappedContacts.clear();
    msg_warning() << "Done cleaning up MORfrictionContact!!!";
}

//template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
//void MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::createResponse(core::objectmodel::BaseContext* group)
//{

//    activateMappers();
//    const double mu_ = this->mu.getValue();
//    // Checks if friction is considered
//    if ( mu_ < 0.0 )
//        serr << sendl << "Error: mu has to take positive values" << sendl;

//    int i=0;
//    if (m_MORconstraint)
//    {
//        for (std::vector<sofa::core::collision::DetectionOutput*>::const_iterator it = contacts.begin(); it!=contacts.end(); it++, i++)
//        {
//            sofa::core::collision::DetectionOutput* o = *it;
//            int index1 = mappedContacts[i].first.first;
//            int index2 = mappedContacts[i].first.second;
//            double distance = mappedContacts[i].second;

//            // Polynome de Cantor de NxN sur N bijectif f(x,y)=((x+y)^2+3x+y)/2
//            long index = cantorPolynomia(o->id /*cantorPolynomia(index1, index2)*/,id);

//            // Add contact in unilateral constraint
//            m_MORconstraint->addContact(mu_, o->normal, distance, index1, index2, index, o->id);
//        }

//        if (parent!=NULL)
//        {
//            parent->removeObject(this);
//            parent->removeObject(m_MORconstraint);
//        }

//        parent = group;
//        if (parent!=NULL)
//        {
//            parent->addObject(this);
//            parent->addObject(m_MORconstraint);
//        }
//    }
//}

//template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
//void MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::removeResponse()
//{
//    if (m_MORconstraint)
//    {
//        mapper1.resize(0);
//        mapper2.resize(0);
//        if (parent!=NULL)
//        {
//            parent->removeObject(this);
//            parent->removeObject(m_MORconstraint);
//        }
//        parent = NULL;
//    }
//}

//template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
//void MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::setInteractionTags(MechanicalState1* mstate1, MechanicalState2* mstate2)
//{
//    sofa::core::objectmodel::TagSet tagsm1 = mstate1->getTags();
//    sofa::core::objectmodel::TagSet tagsm2 = mstate2->getTags();
//    sofa::core::objectmodel::TagSet::iterator it;
//    for(it=tagsm1.begin(); it != tagsm1.end(); it++)
//        m_MORconstraint->addTag(*it);
//    for(it=tagsm2.begin(); it!=tagsm2.end(); it++)
//        m_MORconstraint->addTag(*it);
//}

template < class TCollisionModel1, class TCollisionModel2, class ResponseDataTypes  >
void MORFrictionContact<TCollisionModel1,TCollisionModel2,ResponseDataTypes>::activateMappers()
{
    if (!m_constraint)
    {
        // Get the mechanical model from mapper1 to fill the constraint vector
        MechanicalState1* mmodel1 = mapper1.createMapping(this->getName().c_str());
        // Get the mechanical model from mapper2 to fill the constraints vector
        MechanicalState2* mmodel2;
        if (selfCollision)
        {
            mmodel2 = mmodel1;
        }
        else
        {
            mmodel2 = mapper2.createMapping(this->getName().c_str());
        }
        msg_warning() << "Creating new UnilateralInteractionConstraint!!!!!!!!!!!!!!!!!";
        msg_warning() << "lambdapath is: " << d_lambdaModesPath.getValue();
        msg_warning() << "lambdaCoeffspath is: " << d_lambdaModesCoeffsPath.getValue();
        msg_warning() << "mu is: " << mu.getValue();

        msg_warning() << "********************************************************************************************************************";
        m_constraint = sofa::core::objectmodel::New<sofa::component::constraint::lagrangian::model::MORUnilateralInteractionConstraint<defaulttype::Vec3Types> >(mmodel1, mmodel2, d_lambdaModesPath.getValue(), d_lambdaModesCoeffsPath.getValue());
        m_constraint->setName( this->getName() );
        this->setInteractionTags(mmodel1, mmodel2);
        m_constraint->setCustomTolerance( tol.getValue() );
    }

    int size = contacts.size();
    msg_warning() << "size of contacts in frictionContact:" << size;
    m_constraint->clear(size);
    if (selfCollision)
        mapper1.resize(2*size);
    else
    {
        mapper1.resize(size);
        mapper2.resize(size);
    }
    int i = 0;
    const double d0 = intersectionMethod->getContactDistance() + model1->getProximity() + model2->getProximity(); // - 0.001;

    mappedContacts.resize(contacts.size());
    for (std::vector<sofa::core::collision::DetectionOutput*>::const_iterator it = contacts.begin(); it!=contacts.end(); it++, i++)
    {
        sofa::core::collision::DetectionOutput* o = *it;
        CollisionElement1 elem1(o->elem.first);
        CollisionElement2 elem2(o->elem.second);
        int index1 = elem1.getIndex();
        int index2 = elem2.getIndex();

        typename DataTypes1::Real r1 = 0.;
        typename DataTypes2::Real r2 = 0.;

        // Create mapping for first point
        index1 = mapper1.addPointB(o->point[0], index1, r1);
        // Create mapping for second point
        if (selfCollision)
        {
            index2 = mapper1.addPointB(o->point[1], index2, r2);
        }
        else
        {
            index2 = mapper2.addPointB(o->point[1], index2, r2);
        }
        double distance = d0 + r1 + r2;

        mappedContacts[i].first.first = index1;
        mappedContacts[i].first.second = index2;
        mappedContacts[i].second = distance;
    }

    // Update mappings
    mapper1.update();
    mapper1.updateXfree();
    if (!selfCollision) mapper2.update();
    if (!selfCollision) mapper2.updateXfree();
}


} // namespace sofa::component::collision::response::contact

#endif
