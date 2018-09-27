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
#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_INL
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_INL

#include "HyperReducedRestShapeSpringsForceField.h"
#include <sofa/core/visual/VisualParams.h>
#include <sofa/helper/system/config.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>

#include <sofa/defaulttype/RGBAColor.h>

#include <assert.h>
#include <iostream>

namespace sofa
{

namespace component
{

namespace forcefield
{

using helper::WriteAccessor;
using helper::ReadAccessor;
using core::behavior::BaseMechanicalState;
using core::behavior::MultiMatrixAccessor;
using core::behavior::ForceField;
using defaulttype::BaseMatrix;
using core::VecCoordId;
using core::MechanicalParams;
using defaulttype::Vector3;
using defaulttype::Vec4f;
using helper::vector;
using core::visual::VisualParams;

template<class DataTypes>
HyperReducedRestShapeSpringsForceField<DataTypes>::HyperReducedRestShapeSpringsForceField()
//    : points(initData(&points, "points", "points controlled by the rest shape springs"))
//    , stiffness(initData(&stiffness, "stiffness", "stiffness values between the actual position and the rest shape position"))
//    , angularStiffness(initData(&angularStiffness, "angularStiffness", "angularStiffness assigned when controlling the rotation of the points"))
//    , pivotPoints(initData(&pivotPoints, "pivot_points", "global pivot points used when translations instead of the rigid mass centers"))
//    , external_points(initData(&external_points, "external_points", "points from the external Mechancial State that define the rest shape springs"))
//    , recompute_indices(initData(&recompute_indices, true, "recompute_indices", "Recompute indices (should be false for BBOX)"))
//    , drawSpring(initData(&drawSpring,false,"drawSpring","draw Spring"))
//    , springColor(initData(&springColor, defaulttype::RGBAColor(0.0,1.0,0.0,1.0), "springColor","spring color. (default=[0.0,1.0,0.0,1.0])"))
//    , restMState(initLink("external_rest_shape", "rest_shape can be defined by the position of an external Mechanical State"))
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

template <class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::init()
{
    //this->initMOR(m_indices.size()); //--> move to bwdInit
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::bwdInit()
{
    ForceField<DataTypes>::init();

    if (stiffness.getValue().empty())
    {
        msg_info() << "No stiffness is defined, assuming equal stiffness on each node, k = 100.0 ";

        VecReal stiffs;
        stiffs.push_back(100.0);
        stiffness.setValue(stiffs);
    }

    if (restMState.get() == NULL)
    {
        useRestMState = false;
      
        if(!restMState.empty())
            msg_warning() << "external_rest_shape in node " << this->getContext()->getName() << " not found";
    }
    else
    {
        useRestMState = true;
    }

    k = stiffness.getValue();

    recomputeIndices();

    this->initMOR(m_indices.size());
    msg_info() << "---------------------------------------> BWDINIT";

    BaseMechanicalState* state = this->getContext()->getMechanicalState();
    assert(state);
    matS.resize(state->getMatrixSize(),state->getMatrixSize());
    lastUpdatedStep = -1.0;

}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::reinit()
{
    if (stiffness.getValue().empty())
    {
        msg_info() << "No stiffness is defined, assuming equal stiffness on each node, k = 100.0 " ;

        VecReal stiffs;
        stiffs.push_back(100.0);
        stiffness.setValue(stiffs);
    }
    k = stiffness.getValue();
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::recomputeIndices()
{
    m_indices.clear();
    m_ext_indices.clear();

    for (unsigned int i = 0; i < points.getValue().size(); i++)
        m_indices.push_back(points.getValue()[i]);

    for (unsigned int i = 0; i < external_points.getValue().size(); i++)
        m_ext_indices.push_back(external_points.getValue()[i]);

    m_pivots = pivotPoints.getValue();

    if (m_indices.size()==0)
    {
        for (unsigned int i = 0; i < (unsigned)this->mstate->getSize(); i++)
        {
            m_indices.push_back(i);
        }
    }

    if (m_ext_indices.size()==0)
    {
        if (useRestMState)
        {
            for (unsigned int i = 0; i < (unsigned)restMState->getSize(); i++)
            {
                m_ext_indices.push_back(i);
            }
        }
        else
        {
            for (unsigned int i = 0; i < (unsigned)this->mstate->getSize(); i++)
            {
                m_ext_indices.push_back(i);
            }
        }
    }

    if (m_indices.size() > m_ext_indices.size())
    {
        msg_error() << "The dimention of the source and the targeted points are different ";
        m_indices.clear();
    }
}


template<class DataTypes>
const typename HyperReducedRestShapeSpringsForceField<DataTypes>::DataVecCoord* HyperReducedRestShapeSpringsForceField<DataTypes>::getExtPosition() const
{
    return (useRestMState ? restMState->read(VecCoordId::position()) : this->mstate->read(VecCoordId::restPosition()));
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::addForce(const MechanicalParams*  mparams , DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv&  v )
{
    msg_info() << "--------------------------------> addForce";

    SOFA_UNUSED(mparams);
    SOFA_UNUSED(v);
    std::vector<double> GieUnit;
    if (d_prepareECSW.getValue())
    {
        GieUnit.resize(d_nbModes.getValue());
    }
    WriteAccessor< DataVecDeriv > f1 = f;
    ReadAccessor< DataVecCoord > p1 = x;
    ReadAccessor< DataVecCoord > p0 = *getExtPosition();

    f1.resize(p1.size());

    if (recompute_indices.getValue())
    {
        recomputeIndices();
    }

    //Springs_dir.resize(m_indices.size() );
    if ( k.size()!= m_indices.size() )
    {
        const Real k0 = k[0];
        if (d_performECSW.getValue()){
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                const unsigned int index = m_indices[reducedIntegrationDomain(i)];

                unsigned int ext_index = m_indices[reducedIntegrationDomain(i)];
                if(useRestMState)
                    ext_index= m_ext_indices[reducedIntegrationDomain(i)];

                Deriv dx = p1[index] - p0[ext_index];

                f1[index] -=  weights(reducedIntegrationDomain(i))* dx * k0 ;
            }

        }
        else
        {
            for (size_t numElem=0; numElem<m_indices.size(); numElem++)
            {
                const unsigned int index = m_indices[numElem];
                unsigned int ext_index = m_indices[numElem];
                if(useRestMState)
                    ext_index= m_ext_indices[numElem];

                Deriv dx = p1[index] - p0[ext_index];
                f1[index] -=  dx * k0 ;
                if (d_prepareECSW.getValue())
                {
                    int numTest = this->getContext()->getTime()/this->getContext()->getDt();
                    if (numTest%d_periodSaveGIE.getValue() == 0)       // Take a measure every periodSaveGIE timesteps
                    {
                        numTest = numTest/d_periodSaveGIE.getValue();
                        for (unsigned int modNum = 0 ; modNum < d_nbModes.getValue() ; modNum++)
                        {

                            GieUnit[modNum] = 0;
                            GieUnit[modNum] -= (dx * k0)*Deriv(m_modes(3*index,modNum),m_modes(3*index+1,modNum),m_modes(3*index+2,modNum));
                        }
                        for (unsigned int i = 0 ; i < d_nbModes.getValue() ; i++)
                        {
                            if ( d_nbModes.getValue()*numTest < d_nbModes.getValue()*d_nbTrainingSet.getValue() )
                            {
                                Gie[d_nbModes.getValue()*numTest+i][numElem] = GieUnit[i];
                            }
                        }
                    }
                }
            }
        }
        this->saveGieFile(m_indices.size());
    }
    else
    {
        if (d_performECSW.getValue()){
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                const unsigned int index = m_indices[reducedIntegrationDomain(i)];

                unsigned int ext_index = m_indices[reducedIntegrationDomain(i)];
                if(useRestMState)
                    ext_index= m_ext_indices[reducedIntegrationDomain(i)];

                Deriv dx = p1[index] - p0[ext_index];

                f1[index] -=  weights(reducedIntegrationDomain(i))* dx * k[reducedIntegrationDomain(i)] ;
            }

        }
        else
        {
            for (unsigned int i=0; i<m_indices.size(); i++)
            {
                const unsigned int index = m_indices[i];
                unsigned int ext_index = m_indices[i];
                if(useRestMState)
                    ext_index= m_ext_indices[i];

                Deriv dx = p1[index] - p0[ext_index];
                f1[index] -=  dx * k[i];

            }
        }
    }
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::addDForce(const MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx)
{
    //  remove to be able to build in parallel
    // 	const VecIndex& indices = points.getValue();
    // 	const VecReal& k = stiffness.getValue();
    msg_info() << "--------------------------------> addDForce";

    WriteAccessor< DataVecDeriv > df1 = df;
    ReadAccessor< DataVecDeriv > dx1 = dx;
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

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
    if (!vparams->displayFlags().getShowForceFields() || !drawSpring.getValue())
        return;  /// \todo put this in the parent class

    if(DataTypes::spatial_dimensions > 3)
    {
        msg_error() << "Draw function not implemented for this DataType";
        return;
    }

    vparams->drawTool()->saveLastState();
    vparams->drawTool()->setLightingEnabled(false);

    ReadAccessor< DataVecCoord > p0 = *getExtPosition();
    ReadAccessor< DataVecCoord > p  = this->mstate->read(VecCoordId::position());

    const VecIndex& indices = m_indices;
    const VecIndex& ext_indices = (useRestMState ? m_ext_indices : m_indices);

    vector<Vector3> vertices;
    if (d_performECSW.getValue()){
        for (unsigned int i=0; i<m_RIDsize; i++)
        {
            const unsigned int index = indices[reducedIntegrationDomain(i)];
            const unsigned int ext_index = ext_indices[reducedIntegrationDomain(i)];

            Vector3 v0(0.0, 0.0, 0.0);
            Vector3 v1(0.0, 0.0, 0.0);
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

            Vector3 v0(0.0, 0.0, 0.0);
            Vector3 v1(0.0, 0.0, 0.0);
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
    vparams->drawTool()->drawLines(vertices,5,Vec4f(springColor.getValue()));
    vparams->drawTool()->restoreLastState();
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::addKToMatrix(const MechanicalParams* mparams, const MultiMatrixAccessor* matrix )
{
    //  remove to be able to build in parallel
    // 	const VecIndex& indices = points.getValue();
    // 	const VecReal& k = stiffness.getValue();
    MultiMatrixAccessor::MatrixRef mref = matrix->getMatrix(this->mstate);
    BaseMatrix* mat = mref.matrix;
    unsigned int offset = mref.offset;
    Real kFact = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    const int N = Coord::total_size;

    unsigned int curIndex = 0;

    if (k.size()!= m_indices.size() )
    {
        const Real k0 = k[0];
        if (d_performECSW.getValue()){
            for(unsigned int index = 0 ; index <m_RIDsize ; index++)
            {
                curIndex = m_indices[reducedIntegrationDomain(index)];

                for(int i = 0; i < N; i++)
                {
                    mat->add(offset + N * curIndex + i, offset + N * curIndex + i, -kFact * k0 * weights(reducedIntegrationDomain(index)));
                }

            }
        }
        else
        {
            for (unsigned int index = 0; index < m_indices.size(); index++)
            {
                curIndex = m_indices[index];

                for(int i = 0; i < N; i++)
                {
                    mat->add(offset + N * curIndex + i, offset + N * curIndex + i, -kFact * k0);
                }
                msg_info() << "1st: kfact is :" << kFact << ". Contrib is: " << -kFact * k0;
            }
        }

    }
    else
    {
        if (d_performECSW.getValue()){
            for(unsigned int index = 0 ; index <m_RIDsize ; index++)
            {
                curIndex = m_indices[reducedIntegrationDomain(index)];

                for(int i = 0; i < N; i++)
                {
                    mat->add(offset + N * curIndex + i, offset + N * curIndex + i, -kFact * k[reducedIntegrationDomain(index)] * weights(reducedIntegrationDomain(index)));
                }

            }
        }
        else
        {
            for (unsigned int index = 0; index < m_indices.size(); index++)
            {
                curIndex = m_indices[index];

                for(int i = 0; i < N; i++)
                {
                    mat->add(offset + N * curIndex + i, offset + N * curIndex + i, -kFact * k[index]);
                }
                msg_info() << "2nd: kfact is :" << kFact << ". Contrib is " << -kFact * k[index];
            }
        }

    }
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::addSubKToMatrix(const MechanicalParams* mparams, const MultiMatrixAccessor* matrix, const vector<unsigned> & addSubIndex )
{
    //  remove to be able to build in parallel
    // 	const VecIndex& indices = points.getValue();
    // 	const VecReal& k = stiffness.getValue();
    MultiMatrixAccessor::MatrixRef mref = matrix->getMatrix(this->mstate);
    BaseMatrix* mat = mref.matrix;
    unsigned int offset = mref.offset;
    Real kFact = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    const int N = Coord::total_size;

    unsigned int curIndex = 0;

    if (k.size()!= m_indices.size() )
    {
        const Real k0 = k[0];
        for (unsigned int index = 0; index < m_indices.size(); index++)
        {
            curIndex = m_indices[index];

            bool contains=false;
            for (unsigned s=0;s<addSubIndex.size() && !contains;s++) if (curIndex==addSubIndex[s]) contains=true;
            if (!contains) continue;

            for(int i = 0; i < N; i++)
            {
                mat->add(offset + N * curIndex + i, offset + N * curIndex + i, -kFact * k0);
            }
        }
    }
    else
    {
        for (unsigned int index = 0; index < m_indices.size(); index++)
        {
            curIndex = m_indices[index];

            bool contains=false;
            for (unsigned s=0;s<addSubIndex.size() && !contains;s++) if (curIndex==addSubIndex[s]) contains=true;
            if (!contains) continue;

            for(int i = 0; i < N; i++)
            {
                mat->add(offset + N * curIndex + i, offset + N * curIndex + i, -kFact * k[index]);
            }
        }
    }
}

template<class DataTypes>
void HyperReducedRestShapeSpringsForceField<DataTypes>::updateForceMask()
{
    for (unsigned int i=0; i<m_indices.size(); i++)
        this->mstate->forceMask.insertEntry(m_indices[i]);
}


} // namespace forcefield

} // namespace component

} // namespace sofa

#endif // SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_INL



