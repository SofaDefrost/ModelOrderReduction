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
#ifndef MOR_MORUNILATERALINTERACTIONCONSTRAINT_INL
#define MOR_MORUNILATERALINTERACTIONCONSTRAINT_INL

#include "MORUnilateralInteractionConstraint.h"
#include <sofa/component/constraint/lagrangian/model/UnilateralInteractionConstraint.inl>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/type/Vec.h>
#include <sofa/type/RGBAColor.h>
#include <sofa/linearalgebra/BaseVector.h>
#include "../loader/MatrixLoader.h"
#include "../loader/MatrixLoader.inl"

namespace sofa::component::constraint::lagrangian::model
{
using sofa::component::loader::MatrixLoader;
template<class DataTypes>
MORUnilateralInteractionConstraint<DataTypes>::MORUnilateralInteractionConstraint(MechanicalState* object1, MechanicalState* object2, std::string lambdaModesPath, std::string lambdaModesCoeffsPath)
    : UnilateralInteractionConstraint<DataTypes>(object1,object2)
{
    m_lambdaModesPath = lambdaModesPath;
    m_lambdaModesCoeffsPath = lambdaModesCoeffsPath;
    MatrixLoader<Eigen::MatrixXd>* matLoaderModes = new MatrixLoader<Eigen::MatrixXd>();
    matLoaderModes->setFileName(m_lambdaModesPath);
    matLoaderModes->load();
    matLoaderModes->getMatrix(lambdaModes);

    auto* matLoader = new MatrixLoader<Eigen::MatrixXi>();
    matLoader->setFileName(m_lambdaModesCoeffsPath);
    matLoader->load();
    matLoader->getMatrix(contactIndices);
}

template<class DataTypes>
MORUnilateralInteractionConstraint<DataTypes>::~MORUnilateralInteractionConstraint()
{}

template<class DataTypes>
void MORUnilateralInteractionConstraint<DataTypes>::buildConstraintMatrix(const core::ConstraintParams *, DataMatrixDeriv &c1_d, DataMatrixDeriv &c2_d, unsigned int &contactId
        , const DataVecCoord &, const DataVecCoord &)
{
    assert(this->mstate1);
    assert(this->mstate2);
    double myMuForAllContacts;
    reducedContacts.resize(0);
    if (this->mstate1 == this->mstate2)
    {
        MatrixDeriv& c1 = *c1_d.beginEdit();
        for (unsigned int i = 0; i < contacts.size(); i++)
        {
            auto& c = contacts[i];

            c.id = contactId++;
            MatrixDerivRowIterator c1_it = c1.writeLine(c.id);

            c1_it.addCol(c.m1, -c.norm);
            c1_it.addCol(c.m2, c.norm);

            if (c.mu > 0.0)
            {
                c1_it = c1.writeLine(c.id + 1);
                c1_it.setCol(c.m1, -c.t);
                c1_it.setCol(c.m2, c.t);

                c1_it = c1.writeLine(c.id + 2);
                c1_it.setCol(c.m1, -c.s);
                c1_it.setCol(c.m2, c.s);

                contactId += 2;
            }
        }

        c1_d.endEdit();
    }
    else
    {
        MatrixDeriv& c1 = *c1_d.beginEdit();
        MatrixDeriv& c2 = *c2_d.beginEdit();
        unsigned int line = 0;
        bool somethingAdded;

        for (unsigned int numMode=0; numMode < lambdaModes.cols(); numMode++)
        {
            somethingAdded = false;
            MatrixDerivRowIterator c1_it = c1.writeLine(line);
            MatrixDerivRowIterator c2_it = c2.writeLine(line);

            for (unsigned int i = 0; i < contacts.size(); i++)
            {
                auto& c = contacts[i];
                myMuForAllContacts = c.mu;
                c.id = i;
                if (c.mu == 0.0)
                    if (contactIndices(c.m2) != -1 && lambdaModes(contactIndices(c.m2),numMode)!=0.0){
                        c1_it.addCol(c.m1, -lambdaModes(contactIndices(c.m2),numMode)*c.norm);
                        c2_it.addCol(c.m2, lambdaModes(contactIndices(c.m2),numMode)*c.norm);
                        somethingAdded = true;
                    }

                if (c.mu > 0.0)
                {
                    if (contactIndices(3*c.m2) != -1 && lambdaModes(contactIndices(3*c.m2),numMode)!=0.0){
                        c1_it.addCol(c.m1, -lambdaModes(contactIndices(3*c.m2),numMode)*c.norm);
                        c2_it.addCol(c.m2, lambdaModes(contactIndices(3*c.m2),numMode)*c.norm);
                        somethingAdded = true;

                        MatrixDerivRowIterator c1_it_1 = c1.writeLine(line+1);

                        //                    c1_it = c1.writeLine(c.id + 1);
                        c1_it_1.addCol(c.m1, -lambdaModes(contactIndices(3*c.m2+1),numMode)*c.t);

                        MatrixDerivRowIterator c1_it_2 = c1.writeLine(line+2);
                        //                    c1_it = c1.writeLine(c.id + 2);
                        c1_it_2.addCol(c.m1, -lambdaModes(contactIndices(3*c.m2+2),numMode)*c.s);

                        MatrixDerivRowIterator c2_it_1 = c2.writeLine(line+1);
                        //                    c2_it = c2.writeLine(c.id + 1);
                        c2_it_1.addCol(c.m2, lambdaModes(contactIndices(3*c.m2+1),numMode)*c.t);

                        MatrixDerivRowIterator c2_it_2 = c2.writeLine(line+2);
                        //                    c2_it = c2.writeLine(c.id + 2);
                        c2_it_2.addCol(c.m2,lambdaModes(contactIndices(3*c.m2+2),numMode)*c.s);
                    }
                }


            }
            if (somethingAdded){
                if (myMuForAllContacts == 0.0)
                {
                    reducedContacts.resize(line+1);
                    reducedContacts[line] = numMode;
                    line++;
                }
                else
                {
                    reducedContacts.resize(line+3);
                    reducedContacts[line] = numMode;
                    reducedContacts[line+1] = numMode;
                    reducedContacts[line+2] = numMode;
                    line = line + 3;
                }

            }


        }
        contactId += line;

        c1_d.endEdit();
        c2_d.endEdit();
    }
//    if (myMuForAllContacts == 0.0)
//        contactId = contactId - 1;
//    else
//       contactId = contactId - 3;
}

template<class DataTypes>
void MORUnilateralInteractionConstraint<DataTypes>::getConstraintViolation(const core::ConstraintParams *cparams, linearalgebra::BaseVector *v, const DataVecCoord &, const DataVecCoord &
        , const DataVecDeriv &, const DataVecDeriv &)
{
    switch (cparams->constOrder())
    {
    case core::ConstraintParams::POS_AND_VEL :
    case core::ConstraintParams::POS :
        getPositionViolation(v);
        break;

    case core::ConstraintParams::ACC :
    case core::ConstraintParams::VEL :
        UnilateralInteractionConstraint<DataTypes>::getVelocityViolation(v);
        break;

    default :
        msg_error() << this->getClassName() << " doesn't implement " << cparams->getName() << " constraint violation";
        break;
    }
}

template<class DataTypes>
void MORUnilateralInteractionConstraint<DataTypes>::getPositionViolation(linearalgebra::BaseVector *v)
{
    const VecCoord &PfreeVec = this->getMState2()->read(core::ConstVecCoordId::freePosition())->getValue();
    const VecCoord &QfreeVec = this->getMState1()->read(core::ConstVecCoordId::freePosition())->getValue();
    Real dfree = (Real)0.0;
    Real dfree_t = (Real)0.0;
    Real dfree_s = (Real)0.0;

    const unsigned int cSize = contacts.size();
    Eigen::MatrixXd dfreeRed;
    dfreeRed.resize(v->size(),1);
    dfreeRed.setZero(v->size(),1);
    for (unsigned int i = 0; i < cSize; i++)
    {
        const auto c = contacts[i];

        // Compute dfree, dfree_t and d_free_s

        const Coord &Pfree =  PfreeVec[c.m2];
        const Coord &Qfree =  QfreeVec[c.m1];

        const Coord PPfree = Pfree - c.P;
        const Coord QQfree = Qfree - c.Q;

        const Real ref_dist = PPfree.norm() + QQfree.norm();

        dfree = dot(Pfree - Qfree, c.norm) - c.contactDistance;
        const Real delta = dot(c.P - c.Q, c.norm) - c.contactDistance;

        if ((helper::rabs(delta) < 0.00001 * ref_dist) && (helper::rabs(dfree) < 0.00001 * ref_dist))
        {
            dfree_t = dot(PPfree, c.t) - dot(QQfree, c.t);
            dfree_s = dot(PPfree, c.s) - dot(QQfree, c.s);
        }
        else if (helper::rabs(delta - dfree) > 0.001 * delta)
        {
            const Real dt = delta / (delta - dfree);

            if (dt > 0.0 && dt < 1.0)
            {
                const Coord Pt		= c.P * (1 - dt) + Pfree * dt;
                const Coord Qt		= c.Q * (1 - dt) + Qfree * dt;
                const Coord PtPfree = Pfree - Pt;
                const Coord QtQfree = Qfree - Qt;

                dfree_t = dot(PtPfree, c.t) - dot(QtQfree, c.t);
                dfree_s = dot(PtPfree, c.s) - dot(QtQfree, c.s);
            }
            else if (dfree < 0.0)
            {
                dfree_t = dot(PPfree, c.t) - dot(QQfree, c.t);
                dfree_s = dot(PPfree, c.s) - dot(QQfree, c.s);
            }
            else
            {
                dfree_t = 0;
                dfree_s = 0;
            }
        }
        else
        {
            dfree_t = dot(PPfree, c.t) - dot(QQfree, c.t);
            dfree_s = dot(PPfree, c.s) - dot(QQfree, c.s);
        }

        // Sets dfree in global violation vector
        if (c.mu == 0.0){

            for (int k=0;k<reducedContacts.size();k++){
                if (contactIndices(c.m2) != -1)
                    dfreeRed(k) += dfree*lambdaModes(contactIndices(c.m2),reducedContacts[k]);
            }
        }
        else
        {
            for (int k=0;k<reducedContacts.size()/3;k++){
                if (contactIndices(3*c.m2) != -1){
                    dfreeRed(3*k) += dfree*lambdaModes(contactIndices(3*c.m2),reducedContacts[3*k]);
                    dfreeRed(3*k+1) += dfree_t*lambdaModes(contactIndices(3*c.m2+1),reducedContacts[3*k]);
                    dfreeRed(3*k+2) += dfree_s*lambdaModes(contactIndices(3*c.m2+2),reducedContacts[3*k]);

                }
            }
        }



        c.dfree = dfree; // PJ : For isActive() method. Don't know if it's still usefull.
    }
    for (int k=0;k<reducedContacts.size();k++){
        v->set(k, dfreeRed(k));
    }

}

template<class DataTypes>
void MORUnilateralInteractionConstraint<DataTypes>::getConstraintResolution(const core::ConstraintParams *, std::vector<core::behavior::ConstraintResolution*>& resTab, unsigned int& offset)
{
    if(contactsStatus)
    {
        delete[] contactsStatus;
        contactsStatus = NULL;
    }

    if (contacts.size() > 0)
    {
        contactsStatus = new bool[reducedContacts.size()];
        memset(contactsStatus, 0, sizeof(bool)*reducedContacts.size());
    }

    for(unsigned int i=0; i<reducedContacts.size(); i++)
    {
        auto& c = contacts[0];
        if(c.mu > 0.0)
        {
            i = i+2;
            UnilateralConstraintResolutionWithFriction* ucrwf = new UnilateralConstraintResolutionWithFriction(c.mu, NULL, &contactsStatus[i]);
            ucrwf->setTolerance(customTolerance);
            resTab[offset] = ucrwf;
            // TODO : cette méthode de stockage des forces peu mal fonctionner avec 2 threads quand on utilise l'haptique
            offset += 3;
        }
        else
        {
            resTab[offset++] = new UnilateralConstraintResolution();
        }
    }
}
} // namespace sofa::component::constraint::lagrangian::model

#endif
