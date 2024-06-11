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
#ifndef MOR_MORUNILATERALINTERACTIONCONSTRAINT_H
#define MOR_MORUNILATERALINTERACTIONCONSTRAINT_H

#include <sofa/core/behavior/PairInteractionConstraint.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/VecTypes.h>
#include <iostream>
#include <map>
#include <deque>
#include <sofa/component/constraint/lagrangian/model/UnilateralInteractionConstraint.h>
#include <Eigen/Sparse>

namespace sofa::component::constraint::lagrangian::model
{
class MORUnilateralConstraintResolution : public UnilateralConstraintResolution
{
public:

    MORUnilateralConstraintResolution() : UnilateralConstraintResolution()
    {
//        Load lambdaModes
    }

//    void resolution(int line, double** w, double* d, double* force, double *dfree) override
//    {
//        SOFA_UNUSED(dfree);
//        force[line] -= d[line] / w[line][line];
//        if(force[line] < 0)
//            force[line] = 0.0;
//    }
};

// A little experiment on how to best save the forces for the hot start.
//  TODO : save as a map (index of the contact <-> force)


template<class DataTypes>
class MORUnilateralInteractionConstraint : public UnilateralInteractionConstraint<DataTypes>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE(MORUnilateralInteractionConstraint,DataTypes), SOFA_TEMPLATE(UnilateralInteractionConstraint,DataTypes));

    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::MatrixDeriv MatrixDeriv;
    typedef typename DataTypes::MatrixDeriv::RowConstIterator MatrixDerivRowConstIterator;
    typedef typename DataTypes::MatrixDeriv::ColConstIterator MatrixDerivColConstIterator;
    typedef typename DataTypes::MatrixDeriv::RowIterator MatrixDerivRowIterator;
    typedef typename DataTypes::MatrixDeriv::ColIterator MatrixDerivColIterator;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename Coord::value_type Real;
    typedef typename core::behavior::MechanicalState<DataTypes> MechanicalState;

    typedef core::behavior::BaseConstraint::ConstraintBlockInfo ConstraintBlockInfo;
    typedef core::behavior::BaseConstraint::PersistentID PersistentID;
    typedef core::behavior::BaseConstraint::ConstCoord ConstCoord;
    typedef core::behavior::BaseConstraint::ConstDeriv ConstDeriv;
    typedef core::behavior::BaseConstraint::ConstArea ConstArea;

    typedef core::behavior::BaseConstraint::VecConstraintBlockInfo VecConstraintBlockInfo;
    typedef core::behavior::BaseConstraint::VecPersistentID VecPersistentID;
    typedef core::behavior::BaseConstraint::VecConstCoord VecConstCoord;
    typedef core::behavior::BaseConstraint::VecConstDeriv VecConstDeriv;
    typedef core::behavior::BaseConstraint::VecConstArea VecConstArea;

    typedef core::objectmodel::Data<VecCoord>		DataVecCoord;
    typedef core::objectmodel::Data<VecDeriv>		DataVecDeriv;
    typedef core::objectmodel::Data<MatrixDeriv>    DataMatrixDeriv;

    typedef typename core::behavior::PairInteractionConstraint<DataTypes> Inherit;

    std::string m_lambdaModesPath;
    std::string m_lambdaModesCoeffsPath;
    Eigen::MatrixXd lambdaModes;
    Eigen::MatrixXi contactIndices;
    sofa::type::vector<unsigned int> reducedContacts;


protected:

    using UnilateralInteractionConstraint<DataTypes>::contacts;
    using UnilateralInteractionConstraint<DataTypes>::epsilon;
    using UnilateralInteractionConstraint<DataTypes>::yetIntegrated;
    using UnilateralInteractionConstraint<DataTypes>::customTolerance;

    using UnilateralInteractionConstraint<DataTypes>::prevForces;
    using UnilateralInteractionConstraint<DataTypes>::contactsStatus;

//    /// Computes constraint violation
//    in position and stores it into resolution global vector
//    ///
//    /// @param v Global resolution vector
    virtual void getPositionViolation(linearalgebra::BaseVector *v) override;

public:

    using UnilateralInteractionConstraint<DataTypes>::constraintId;
protected:
    MORUnilateralInteractionConstraint(MechanicalState* object1=nullptr, MechanicalState* object2=nullptr, std::string lambdaModesPath=nullptr,std::string lambdaModesCoeffsPath=nullptr);
    ~MORUnilateralInteractionConstraint();

public:
    void buildConstraintMatrix(const core::ConstraintParams* cParams, DataMatrixDeriv &c1, DataMatrixDeriv &c2, unsigned int &cIndex
            , const DataVecCoord &x1, const DataVecCoord &x2) override;

    void getConstraintViolation(const core::ConstraintParams* cParams, linearalgebra::BaseVector *v, const DataVecCoord &x1, const DataVecCoord &x2
            , const DataVecDeriv &v1, const DataVecDeriv &v2) override;


//    void getConstraintInfo(const core::ConstraintParams* cParams, VecConstraintBlockInfo& blocks, VecPersistentID& ids, VecConstCoord& positions, VecConstDeriv& directions, VecConstArea& areas) override;

    virtual void getConstraintResolution(const core::ConstraintParams *,std::vector<core::behavior::ConstraintResolution*>& resTab, unsigned int& offset) override;
//    bool isActive() const override;

//    void draw(const core::visual::VisualParams* vparams) override;
};


#if  !defined(MOR_MORUNILATERALINTERACTIONCONSTRAINT_CPP)
extern template class SOFA_MODELORDERREDUCTION_API MORUnilateralInteractionConstraint<defaulttype::Vec3Types>;
#endif
} // namespace sofa::component::constraint::lagrangian::model

#endif // SOFA_COMPONENT_CONSTRAINTSET_UNILATERALINTERACTIONCONSTRAINT_H
