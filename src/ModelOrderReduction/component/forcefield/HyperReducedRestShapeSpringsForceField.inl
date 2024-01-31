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

#include <ModelOrderReduction/component/forcefield/HyperReducedRestShapeSpringsForceField.h>
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
HyperReducedRestShapeSpringsForceField<DataTypes>::HyperReducedRestShapeSpringsForceField()
{
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::parse(core::objectmodel::BaseObjectDescription *arg)
{
    const char* attr = arg->getAttribute("external_rest_shape") ;
    if( attr != nullptr && attr[0] != '@')
    {
            msg_error() << "HyperReducedRestShapeSpringsForceField have changed since 17.06. The parameter 'external_rest_shape' is now a Link. To fix your scene you need to add and '@' in front of the provided path. See PR#315" ;
    }

    Inherit::parse(arg) ;
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::bwdInit()
{
    ForceField<DataTypes>::init();

    if (d_stiffness.getValue().empty())
    {
        msg_info() << "No stiffness is defined, assuming equal stiffness on each node, k = 100.0 ";

        VecReal stiffs;
        stiffs.push_back(100.0);
        d_stiffness.setValue(stiffs);
    }

    if (l_restMState.get() == NULL)
    {
        useRestMState = false;
        msg_info() << "no external rest shape used";

        if(!l_restMState.empty())
        {
            msg_warning() << "external_rest_shape in node " << this->getContext()->getName() << " not found";
        }
    }
    else
    {
        msg_info() << "external rest shape used";
        useRestMState = true;
    }

    recomputeIndices();

    BaseMechanicalState* state = this->getContext()->getMechanicalState();
    if(!state)
    {
        msg_warning() << "MechanicalState of the current context returns null pointer";
    }
    else
    {
        assert(state);
        matS.resize(state->getMatrixSize(),state->getMatrixSize());
    }
    lastUpdatedStep = -1.0;
    this->initMOR(d_points.getValue().size(),notMuted());
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::reinit()
{
    if (d_stiffness.getValue().empty())
    {
        msg_info() << "No stiffness is defined, assuming equal stiffness on each node, k = 100.0 " ;

        VecReal stiffs;
        stiffs.push_back(100.0);
        d_stiffness.setValue(stiffs);
    }
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::recomputeIndices()
{
    m_indices.clear();
    m_ext_indices.clear();

    for (unsigned int i = 0; i < d_points.getValue().size(); i++)
    {
        m_indices.push_back(d_points.getValue()[i]);
    }

    for (unsigned int i = 0; i < d_external_points.getValue().size(); i++)
    {
        m_ext_indices.push_back(d_external_points.getValue()[i]);
    }

    if (m_indices.empty())
    {
        // no point are defined, default case: points = all points
        for (unsigned int i = 0; i < (unsigned)this->mstate->getSize(); i++)
        {
            m_indices.push_back(i);
        }
    }

    if (m_ext_indices.empty())
    {
        if (useRestMState)
        {
            for (unsigned int i = 0; i < getExtPosition()->getValue().size(); i++)
            {
                m_ext_indices.push_back(i);
            }
        }
        else
        {
            for (unsigned int i = 0; i < m_indices.size(); i++)
            {
                m_ext_indices.push_back(m_indices[i]);
            }
        }
    }

    if (!checkOutOfBoundsIndices())
    {
        msg_error() << "The dimension of the source and the targeted points are different ";
        m_indices.clear();
    }
    else
    {
        msg_info() << "Indices successfully checked";
    }
}

template<class DataTypes>
bool HyperReducedRestShapeSpringsForceField<DataTypes>::checkOutOfBoundsIndices()
{
    if (!RestShapeSpringsForceField<DataTypes>::checkOutOfBoundsIndices(m_indices, this->mstate->getSize()))
    {
        msg_error() << "Out of Bounds m_indices detected. ForceField is not activated.";
        return false;
    }
    if (!RestShapeSpringsForceField<DataTypes>::checkOutOfBoundsIndices(m_ext_indices, getExtPosition()->getValue().size()))
    {
        msg_error() << "Out of Bounds m_ext_indices detected. ForceField is not activated.";
        return false;
    }
    if (m_indices.size() != m_ext_indices.size())
    {
        msg_error() << "Dimensions of the source and the targeted points are different. ForceField is not activated.";
        return false;
    }
    return true;
}

template<class DataTypes>
const typename HyperReducedRestShapeSpringsForceField<DataTypes>::DataVecCoord* HyperReducedRestShapeSpringsForceField<DataTypes>::getExtPosition() const
{
    return (useRestMState ? l_restMState->read(VecCoordId::position()) : this->mstate->read(VecCoordId::restPosition()));
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::addForce(const MechanicalParams*  mparams , DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv&  v )
{
    msg_info() << "--------------------------------> addForce";

    SOFA_UNUSED(mparams);
    SOFA_UNUSED(v);
    WriteAccessor< DataVecDeriv > f1 = f;
    ReadAccessor< DataVecCoord > p1 = x;
    ReadAccessor< DataVecCoord > p0 = *this->getExtPosition();

    f1.resize(p1.size());

    if (d_recompute_indices.getValue())
    {
        this->recomputeIndices();
    }

    unsigned int i;
    const VecReal &k = d_stiffness.getValue();
    if ( k.size()!= m_indices.size() )
    {
        const Real k0 = k[0];
        unsigned int nbElementsConsidered;
        if (!d_performECSW.getValue())
        {
            nbElementsConsidered = m_indices.size();
        }
        else
        {
            if (m_RIDsize != 0) {
                nbElementsConsidered = m_RIDsize;
            }
            else
            {
                msg_warning() << "RID is empty!!! Taking all the elements...";
                nbElementsConsidered = m_indices.size();
            }
        }
        for (unsigned int point = 0 ; point<nbElementsConsidered ;++point)
        {
            if (!d_performECSW.getValue())
                i = point;
            else
                i = reducedIntegrationDomain(point);

            const unsigned int index = m_indices[i];

            unsigned int ext_index = m_indices[i];

            if(useRestMState)
                ext_index= m_ext_indices[i];

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
            nbElementsConsidered = m_indices.size();
        else
        {
            if (m_RIDsize != 0) {
                nbElementsConsidered = m_RIDsize;
            }
            else
            {
                nbElementsConsidered = m_indices.size();
                msg_warning("RID is empty! Taking all the elements...");
            }
        }
        for (unsigned int point = 0 ; point<nbElementsConsidered ;++point)
        {
            if (!d_performECSW.getValue())
                i = point;
            else
                i = reducedIntegrationDomain(point);

            const unsigned int index = m_indices[i];

            unsigned int ext_index = m_indices[i];
            if(useRestMState)
                ext_index= m_ext_indices[i];

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
    this->saveGieFile(m_indices.size());
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::addDForce(const MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx)
{
    msg_info() << "--------------------------------> addDForce";

    WriteAccessor< DataVecDeriv > df1 = df;
    ReadAccessor< DataVecDeriv > dx1 = dx;
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    const VecReal &k = d_stiffness.getValue();
    if (k.size()!= m_indices.size() )
    {
        const Real k0 = k[0];
        if (d_performECSW.getValue()){
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                df1[m_indices[reducedIntegrationDomain(i)]] -=  weights(reducedIntegrationDomain(i)) * dx1[m_indices[reducedIntegrationDomain(i)]] * k0 * kFactor;
            }
        }
        else
        {
            for (unsigned int i=0; i<m_indices.size(); i++)
            {
                df1[m_indices[i]] -=  dx1[m_indices[i]] * k0 * kFactor;
                msg_info() << "1st addDForce: kFactor is :" << kFactor << ". Contrib is: " <<  dx1[m_indices[i]] * k0 * kFactor;
                msg_info() << "1st addDForce: k0 is :" << k0 << ". m_indices[i] is: " <<  m_indices[i] << "dx1[m_indices[i]] is " << dx1[m_indices[i]];

            }
        }
    }
    else
    {
        if (d_performECSW.getValue()){
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                df1[m_indices[reducedIntegrationDomain[i]]] -=  weights(reducedIntegrationDomain(i)) * dx1[m_indices[reducedIntegrationDomain(i)]] * k[reducedIntegrationDomain(i)] * kFactor;
            }
        }
        else
        {

            for (unsigned int i=0; i<m_indices.size(); i++)
            {
                df1[m_indices[i]] -=  dx1[m_indices[i]] * k[i] * kFactor ;
            }
        }

    }
}

// draw for standard types (i.e Vec<1,2,3>)
template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::draw(const VisualParams *vparams)
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
    ReadAccessor< DataVecCoord > p  = this->mstate->read(VecCoordId::position());

    const VecIndex& indices = m_indices;
    const VecIndex& ext_indices = (useRestMState ? m_ext_indices : m_indices);

    vector<type::Vec3> vertices;
    if (d_performECSW.getValue()){
        for (unsigned int i=0; i<m_RIDsize; i++)
        {
            const unsigned int index = indices[reducedIntegrationDomain(i)];
            const unsigned int ext_index = ext_indices[reducedIntegrationDomain(i)];

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
        for (unsigned int i=0; i<indices.size(); i++)
        {
            const unsigned int index = indices[i];
            const unsigned int ext_index = ext_indices[i];

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
void HyperReducedRestShapeSpringsForceField<DataTypes>::buildStiffnessMatrix(
    core::behavior::StiffnessMatrix* matrix)
{
    const VecReal& k = d_stiffness.getValue();
    const VecReal& k_a = d_angularStiffness.getValue();
    const auto activeDirections = d_activeDirections.getValue();

    constexpr sofa::Size space_size = Deriv::spatial_dimensions; // == total_size if DataTypes = VecTypes
    constexpr sofa::Size total_size = Deriv::total_size;

    auto dfdx = matrix->getForceDerivativeIn(this->mstate)
                       .withRespectToPositionsIn(this->mstate);
    unsigned int nbIndicesConsidered;
    sofa::Index curIndex;

    if (d_performECSW.getValue())
        nbIndicesConsidered = m_RIDsize;
    else
        nbIndicesConsidered = m_indices.size();

    for (sofa::Index index = 0; index < nbIndicesConsidered ; index++)
    {
        if (!d_performECSW.getValue())
            curIndex = m_indices[index];
        else
            curIndex = m_indices[reducedIntegrationDomain(index)];

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

