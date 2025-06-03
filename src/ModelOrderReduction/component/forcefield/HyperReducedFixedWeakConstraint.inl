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
#pragma once

#include <ModelOrderReduction/component/forcefield/HyperReducedFixedWeakConstraint.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/behavior/MultiMatrixAccessor.h>
#include <sofa/helper/config.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/type/RGBAColor.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>


#include <assert.h>
#include <iostream>

namespace // anonymous
{
    // Boiler-plate code to test if a type implements a method
    // explanation https://stackoverflow.com/a/30848101

    template <typename...>
    using void_t = void;

    // Primary template handles all types not supporting the operation.
    template <typename, template <typename> class, typename = void_t<>>
    struct detect : std::false_type {};

    // Specialization recognizes/validates only types supporting the archetype.
    template <typename T, template <typename> class Op>
    struct detect<T, Op, void_t<Op<T>>> : std::true_type {};

    // Actual test if DataType::Coord implements getOrientation() (hence is a RigidType)
    template <typename T>
    using isRigid_t = decltype(std::declval<typename T::Coord>().getOrientation());

    template <typename T>
    using isRigidType = detect<T, isRigid_t>;
} // anonymous

namespace sofa::component::solidmechanics::spring
{

using helper::WriteAccessor;
using helper::ReadAccessor;
using core::behavior::BaseMechanicalState;
using core::behavior::MultiMatrixAccessor;
using core::behavior::ForceField;
using linearalgebra::BaseMatrix;
using core::VecCoordId;
using core::MechanicalParams;
using type::Vec3;
using type::Vec4f;
using type::vector;
using core::visual::VisualParams;

template<class DataTypes>
HyperReducedFixedWeakConstraint<DataTypes>::HyperReducedFixedWeakConstraint()
{

}

template<class DataTypes>
void HyperReducedFixedWeakConstraint<DataTypes>::bwdInit()
{
    FixedWeakConstraint<DataTypes>::init();
    this->initMOR(d_indices.getValue().size(),notMuted());
}


template<class DataTypes>
void HyperReducedFixedWeakConstraint<DataTypes>::addForce(const MechanicalParams*  mparams , DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv&  v )
{
    msg_info() << "--------------------------------> addForce";

    SOFA_UNUSED(mparams);
    SOFA_UNUSED(v);
    WriteAccessor< DataVecDeriv > f1 = f;
    ReadAccessor< DataVecCoord > p1 = x;
    ReadAccessor< DataVecCoord > p0 = *this->getExtPosition();

    f1.resize(p1.size());

    const auto & indices = this->getIndices();
    const auto & extIndices = this->getExtIndices();
    const bool fixedAll = this->d_fixAll.getValue();
    const unsigned maxIt = fixedAll ? this->mstate->getSize() : indices.size();

    unsigned int i;
    const VecReal &k = d_stiffness.getValue();
    if ( k.size()!= maxIt )
    {
        const Real k0 = k[0];
        unsigned int nbElementsConsidered;
        if (!d_performECSW.getValue())
        {
            nbElementsConsidered = maxIt;
        }
        else
        {
            if (m_RIDsize != 0) {
                nbElementsConsidered = m_RIDsize;
            }
            else
            {
                msg_warning() << "RID is empty!!! Taking all the elements...";
                nbElementsConsidered = maxIt;
            }
        }
        for (unsigned int point = 0 ; point<nbElementsConsidered ;++point)
        {
            if (!d_performECSW.getValue())
                i = point;
            else
                i = reducedIntegrationDomain(point);

            unsigned int index = i;
            unsigned int ext_index = i;

            if (!fixedAll)
            {
                index = indices[i];
                ext_index = extIndices[i];
            }


            Deriv dx = p1[index] - p0[ext_index];
            std::vector<Deriv> contrib;
            std::vector<unsigned int> indexList;
            contrib.resize(1);
            indexList.resize(1);
            contrib[0] = -dx * k0;
            indexList[0] = index;
            if (!d_performECSW.getValue())
                f1[index] +=  contrib[0] ;
            else
                f1[index] +=  weights(i)* contrib[0] ;

            this->template updateGie<DataTypes>(indexList, contrib, i);
        }
    }
    else
    {

        unsigned int nbElementsConsidered;
        if (!d_performECSW.getValue())
            nbElementsConsidered = maxIt;
        else
        {
            if (m_RIDsize != 0) {
                nbElementsConsidered = m_RIDsize;
            }
            else
            {
                nbElementsConsidered = maxIt;
                msg_warning("RID is empty! Taking all the elements...");
            }
        }
        for (unsigned int point = 0 ; point<nbElementsConsidered ;++point)
        {
            if (!d_performECSW.getValue())
                i = point;
            else
                i = reducedIntegrationDomain(point);

            unsigned int index = i;
            unsigned int ext_index = i;

            if (!fixedAll)
            {
                index = indices[i];
                ext_index = extIndices[i];
            }

            Deriv dx = p1[index] - p0[ext_index];
            std::vector<Deriv> contrib;
            std::vector<unsigned int> indexList;
            contrib.resize(1);
            indexList.resize(1);
            contrib[0] = -dx * k[i];
            indexList[0] = index;
            if (!d_performECSW.getValue())
                f1[index] +=  contrib[0] ;
            else
                f1[index] +=  weights(i)* contrib[0] ;
            this->template updateGie<DataTypes>(indexList, contrib, i);
        }
    }
    this->saveGieFile(maxIt);
}

template<class DataTypes>
void HyperReducedFixedWeakConstraint<DataTypes>::addDForce(const MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx)
{
    msg_info() << "--------------------------------> addDForce";

    WriteAccessor< DataVecDeriv > df1 = df;
    ReadAccessor< DataVecDeriv > dx1 = dx;
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    const auto & indices = this->getIndices();
    const bool fixedAll = this->d_fixAll.getValue();
    const unsigned maxIt = fixedAll ? this->mstate->getSize() : indices.size();
    sofa::Index index;

    const VecReal &k = d_stiffness.getValue();
    if (k.size()!= maxIt )
    {
        const Real k0 = k[0];
        if (d_performECSW.getValue()){
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                if (!fixedAll)
                {
                    index = indices[reducedIntegrationDomain(i)];
                }
                else
                {
                    index = reducedIntegrationDomain(i);
                }
                df1[index] -=  weights(reducedIntegrationDomain(i)) * dx1[index] * k0 * kFactor;
            }
        }
        else
        {
            for (unsigned int i=0; i<maxIt; i++)
            {
                if (!fixedAll)
                {
                    index = indices[i];
                }
                else
                {
                    index = i;
                }
                df1[index] -=  dx1[index] * k0 * kFactor;
                msg_info() << "1st addDForce: kFactor is :" << kFactor << ". Contrib is: " <<  dx1[index] * k0 * kFactor;
                msg_info() << "1st addDForce: k0 is :" << k0 << ". index is: " <<  index<< "dx1[index] is " << dx1[index];

            }
        }
    }
    else
    {
        if (d_performECSW.getValue()){
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                if (!fixedAll)
                {
                    index = indices[reducedIntegrationDomain(i)];
                }
                else
                {
                    index = reducedIntegrationDomain(i);
                }
                df1[index] -=  weights(reducedIntegrationDomain(i)) * dx1[index] * k[reducedIntegrationDomain(i)] * kFactor;
            }
        }
        else
        {

            for (unsigned int i=0; i<maxIt; i++)
            {
                if (!fixedAll)
                {
                    index = indices[i];
                }
                else
                {
                    index = i;
                }
                df1[index] -=  dx1[index] * k[i] * kFactor ;
            }
        }

    }
}

// draw for standard types (i.e Vec<1,2,3>)
template<class DataTypes>
void HyperReducedFixedWeakConstraint<DataTypes>::draw(const VisualParams *vparams)
{
    if (!vparams->displayFlags().getShowForceFields() || !d_drawSpring.getValue())
        return;  /// \todo put this in the parent class

    if(DataTypes::spatial_dimensions > 3)
    {
        msg_error() << "Draw function not implemented for this DataType";
        return;
    }

    vparams->drawTool()->saveLastState();
    vparams->drawTool()->setLightingEnabled(false);

    ReadAccessor< DataVecCoord > p0 = *this->getExtPosition();
    ReadAccessor< DataVecCoord > p  = this->mstate->read(sofa::core::vec_id::read_access::position);

    const VecIndex& indices = this->getIndices();
    const VecIndex& ext_indices = this->getExtIndices();

    const bool fixedAll = this->d_fixAll.getValue();
    const unsigned maxIt = fixedAll ? this->mstate->getSize() : indices.size();
    unsigned int index;
    unsigned int ext_index;

    vector<type::Vec3> vertices;
    if (d_performECSW.getValue()){
        for (unsigned int i=0; i<m_RIDsize; i++)
        {
            if (!fixedAll)
            {
                index = indices[reducedIntegrationDomain(i)];
                ext_index = ext_indices[reducedIntegrationDomain(i)];
            }
            else
            {
                index = reducedIntegrationDomain(i);
                ext_index = reducedIntegrationDomain(i);
            }

            type::Vec3 v0(0.0, 0.0, 0.0);
            type::Vec3 v1(0.0, 0.0, 0.0);
            for(unsigned int j=0 ; j<DataTypes::spatial_dimensions ; j++)
            {
                v0[j] = p[index][j];
                v1[j] = p0[ext_index][j];
            }

            vertices.push_back(v0);
            vertices.push_back(v1);
        }
    }
    else
    {
        for (unsigned int i=0; i<maxIt; i++)
        {
            if (!fixedAll)
            {
                index = indices[i];
                ext_index = ext_indices[i];
            }
            else
            {
                index = i;
                ext_index = i;
            }

            type::Vec3 v0(0.0, 0.0, 0.0);
            type::Vec3 v1(0.0, 0.0, 0.0);
            for(unsigned int j=0 ; j<DataTypes::spatial_dimensions ; j++)
            {
                v0[j] = p[index][j];
                v1[j] = p0[ext_index][j];
            }

            vertices.push_back(v0);
            vertices.push_back(v1);
        }
    }
    //todo(dmarchal) because of https://github.com/sofa-framework/sofa/issues/64
    vparams->drawTool()->drawLines(vertices,5, sofa::type::RGBAColor(d_springColor.getValue()));
    vparams->drawTool()->restoreLastState();
}

template <class DataTypes>
void HyperReducedFixedWeakConstraint<DataTypes>::buildStiffnessMatrix(
    core::behavior::StiffnessMatrix* matrix)
{
    const VecReal& k = d_stiffness.getValue();
    const VecReal& k_a = d_angularStiffness.getValue();
    const auto activeDirections = this->getActiveDirections();

    constexpr sofa::Size space_size = Deriv::spatial_dimensions; // == total_size if DataTypes = VecTypes
    constexpr sofa::Size total_size = Deriv::total_size;

    auto dfdx = matrix->getForceDerivativeIn(this->mstate)
                       .withRespectToPositionsIn(this->mstate);
    unsigned int nbIndicesConsidered;
    sofa::Index curIndex;
    const VecIndex& indices = this->getIndices();
    const bool fixedAll = this->d_fixAll.getValue();
    const unsigned maxIt = fixedAll ? this->mstate->getSize() : indices.size();

    if (d_performECSW.getValue())
        nbIndicesConsidered = m_RIDsize;
    else
        nbIndicesConsidered = maxIt;

    for (sofa::Index index = 0; index < nbIndicesConsidered ; index++)
    {
        if (!d_performECSW.getValue())
        {
            if (!fixedAll)
            {
                curIndex = indices[index];
            }
            else
            {
                curIndex = index;
            }
        }
        else
            curIndex = indices[reducedIntegrationDomain(index)];

        // translation
        const auto vt = -k[(curIndex < k.size()) * curIndex];
        for(sofa::Index i = 0; i < space_size; i++)
        {
            if (!d_performECSW.getValue())
                dfdx(total_size * curIndex + i, total_size * curIndex + i) += vt;
            else
                dfdx(total_size * curIndex + i, total_size * curIndex + i) += vt*weights(reducedIntegrationDomain(index));

        }

        // rotation (if applicable)
        if constexpr (isRigidType<DataTypes>())
        {
            const auto vr = -k_a[(curIndex < k_a.size()) * curIndex];
            for (sofa::Size i = space_size; i < total_size; ++i)
            {
                // Contribution to the stiffness matrix are only taken into
                // account for 1 values in d_activeDirections
                if (activeDirections[i])
                {
                    if (!d_performECSW.getValue())
                        dfdx(total_size * index + i, total_size * index + i) += vr;
                    else
                        dfdx(total_size * index + i, total_size * index + i) += vr*weights(reducedIntegrationDomain(index));
                }
            }
        }
    }
}

} // namespace sofa::component::solidmechanics::spring

