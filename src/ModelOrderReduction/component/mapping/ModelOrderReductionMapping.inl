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
#ifndef SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_INL
#define SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_INL

#include "ModelOrderReductionMapping.h"
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/component/topology/container/grid/GridTopology.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/helper/ScopedAdvancedTimer.h>
#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <sofa/helper/logging/Messaging.h>
#include "../loader/MatrixLoader.h"

// verify timing
#include <sofa/helper/system/thread/CTime.h>

namespace sofa
{

namespace component
{

namespace mapping
{

using std::vector;
using sofa::component::loader::MatrixLoader;
typedef type::Quat<SReal> Quat;
template<class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::init()
{
    const unsigned n_in = fromModel->getSize();
    const unsigned n_out = toModel->getSize();
    msg_info(this) << "Number of modes: "<<n_in<<" Number of FEM nodes: "<<n_out;

    MatrixLoader<Eigen::MatrixXd>* matLoader = new MatrixLoader<Eigen::MatrixXd>();
    matLoader->m_printLog = this->notMuted();
    matLoader->setFileName(d_modesPath.getValue());
    matLoader->load();
    matLoader->getMatrix(m_modesEigen);

    if (m_modesEigen.cols()<n_in)
    {
        msg_error(this) << "Error in number of modes: " << n_in << " asked, but only " << m_modesEigen.cols() << " present in input file: " << d_modesPath.getValue();
    }
    else
    {
        m_modesEigen.conservativeResize(Eigen::NoChange,n_in);
    }
    msg_info(this) << "Nb rows" << m_modesEigen.rows();
    msg_info(this) << "Nb cols" << m_modesEigen.cols();

    delete matLoader;

    Inherit::init();

    if (d_rotation.getValue()[0] != 0.0 || d_rotation.getValue()[1] != 0.0 || d_rotation.getValue()[2] != 0.0)
        applyRotation(d_rotation.getValue()[0], d_rotation.getValue()[1], d_rotation.getValue()[2]);
}

//Apply Rotation from Euler angles (in degree!)
template <class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::applyRotation(const SReal rx, const SReal ry, const SReal rz)
{
    Quat q = Quat::createQuaterFromEuler(type::Vec< 3, SReal >(rx, ry, rz) * M_PI / 180.0);
    applyRotation(q);
}

template <class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::applyRotation(const type::Quat<SReal>& q)
{
    type::Vec<3, InReal> pos;
    for (unsigned int i = 0; i < m_modesEigen.cols(); i++) // loop over modes
    {
        for (unsigned int j = 0; j < m_modesEigen.rows(); j+=3) // loop over positions
        {
            pos[0] = m_modesEigen(j, i);
            pos[1] = m_modesEigen(j+1, i);
            pos[2] = m_modesEigen(j+2, i);
            type::Vec<3, InReal> newposition = q.rotate(pos);
            m_modesEigen(j, i)   = newposition[0];
            m_modesEigen(j+1, i) = newposition[1];
            m_modesEigen(j+2, i) = newposition[2];
        }
    }
}

template <class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::apply(const core::MechanicalParams * /*mparams*/, Data<VecCoord>& dOut, const Data<InVecCoord>& dIn)
{
    SCOPED_TIMER("apply in ModelOrderReductionMapping");

    helper::WriteOnlyAccessor< Data<VecCoord> > out = dOut;
    helper::ReadAccessor< Data<InVecCoord> > in = dIn;

    const Data<VecCoord>* restPosData = toModel->read(core::VecCoordId::restPosition());
    assert(restPosData != nullptr);

    out.wref() = restPosData->getValue();

    Eigen::Map<Eigen::Matrix<OutReal, Eigen::Dynamic, 1> > outMatrix(out.wref()[0].ptr(), out.size() * 3, 1);
    Eigen::Map<const Eigen::Matrix<InReal, Eigen::Dynamic, 1> > inMatrix(in.ref()[0].ptr(), in.size(), 1);

    outMatrix += m_modesEigen * inMatrix;
}

template <class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::applyJ(const core::MechanicalParams * /*mparams*/, Data<VecDeriv>& dOut, const Data<InVecDeriv>& dIn)
{
    SCOPED_TIMER("applyJ in ModelOrderReductionMapping");

    helper::WriteOnlyAccessor< Data<VecDeriv> > out = dOut;
    helper::ReadAccessor< Data<InVecDeriv> > in = dIn;

    Eigen::VectorXd inEig;
    inEig.resize(in.size());
    Eigen::VectorXd outEig;
    outEig.resize(3*out.size());
    for(unsigned int j=0; j<in.size(); j++)
    {
        inEig(j) = in[j][0];
    }
    outEig = m_modesEigen*inEig;
    for(unsigned int i=0; i<out.size(); i++)
    {
        out[i] = Deriv(outEig(3*i),outEig(3*i+1),outEig(3*i+2));
    }
}

template<class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::applyJT(const core::MechanicalParams * /*mparams*/, Data<InVecDeriv>& dOut, const Data<VecDeriv>& dIn)
{
    SCOPED_TIMER("applyJT in ModelOrderReductionMapping");

    helper::WriteAccessor< Data<InVecDeriv> > out = dOut;
    helper::ReadAccessor< Data<VecDeriv> > in = dIn;

    Eigen::VectorXd inEig;
    inEig.resize(3*in.size());
    Eigen::VectorXd outEig;
    outEig.resize(out.size());


    for(unsigned int i=0; i<in.size(); i++)
    {
        inEig(3*i) = in[i][0];
        inEig(3*i+1) = in[i][1];
        inEig(3*i+2) = in[i][2];
    }

    outEig = m_modesEigen.transpose()*inEig;

    for(unsigned int j=0; j<out.size(); j++)
    {
        out[j][0] += outEig(j);
    }
}

template <class TIn, class TOut>
void ModelOrderReductionMapping<TIn, TOut>::applyJT(const core::ConstraintParams * /*cparams*/, Data<InMatrixDeriv>& dOut, const Data<MatrixDeriv>& dIn)
{
    InMatrixDeriv& out = *dOut.beginEdit();
    const MatrixDeriv& in = dIn.getValue();
    typename Out::MatrixDeriv::RowConstIterator rowItEnd = in.end();
    size_t nbModes = m_modesEigen.cols();

    for (typename Out::MatrixDeriv::RowConstIterator rowIt = in.begin(); rowIt != rowItEnd; ++rowIt)
    {
        typename Out::MatrixDeriv::ColConstIterator colIt = rowIt.begin();
        typename Out::MatrixDeriv::ColConstIterator colItEnd = rowIt.end();

        // Creates a constraints if the input constraint is not empty.
        if (colIt != colItEnd)
        {
            typename In::MatrixDeriv::RowIterator o = out.writeLine(rowIt.index());

            while (colIt != colItEnd)
            {
                for(unsigned int j=0; j<nbModes; j++)

                {
                    InDeriv data;
                    data[0] = Deriv(m_modesEigen(3*(colIt.index()),j),m_modesEigen(3*(colIt.index())+1,j),m_modesEigen(3*(colIt.index())+2,j))*(colIt.val());
                    o.addCol(j,data);
                }

                ++colIt;
            }

        }
        else
        {
            msg_fatal() << "Not implemented #################################";
        }
    }

    dOut.endEdit();
}




template <class TIn, class TOut>
const sofa::linearalgebra::BaseMatrix* ModelOrderReductionMapping<TIn, TOut>::getJ()
{
    return &m_J;
}

template <class TIn, class TOut>
const typename ModelOrderReductionMapping<TIn, TOut>::js_type* ModelOrderReductionMapping<TIn, TOut>::getJs()
{
    return &m_Js;
}


} // namespace mapping

} // namespace component

} // namespace sofa

#endif


