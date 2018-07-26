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
#ifndef MECHANICALMATRIXMAPPERMOR_H
#define MECHANICALMATRIXMAPPERMOR_H

#include <SofaGeneralAnimationLoop/MechanicalMatrixMapper.h>

namespace sofa
{

namespace component
{

namespace interactionforcefield
{


template<typename TDataTypes1, typename TDataTypes2>
class MechanicalMatrixMapperMOR : public MechanicalMatrixMapper<TDataTypes1, TDataTypes2>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE2(MechanicalMatrixMapperMOR, TDataTypes1, TDataTypes2), SOFA_TEMPLATE2(MechanicalMatrixMapper, TDataTypes1, TDataTypes2));
    typedef MechanicalMatrixMapper<TDataTypes1, TDataTypes2> Inherit;


protected:
    MechanicalMatrixMapperMOR();

public:
    Data< bool > performECSW;
    sofa::helper::vector<unsigned int> listActiveNodes;
    sofa::core::objectmodel::DataFileName listActiveNodesPath;
    Data< bool > timeInvariantMapping1;
    Data< bool > timeInvariantMapping2;
    Eigen::SparseMatrix<double> constantJ1;
    Eigen::SparseMatrix<double> constantJ2;

    Data< bool > saveReducedMass;
    Data< bool > usePrecomputedMass;
    sofa::core::objectmodel::DataFileName precomputedMassPath;
    Eigen::SparseMatrix<double> JtMJ;


public:

    virtual void init();

protected:
    virtual void accumulateJacobiansOptimized(const MechanicalParams* mparams);
    virtual void addMassToSystem(const MechanicalParams* mparams, const DefaultMultiMatrixAccessor* KAccessor);
    virtual void addPrecomputedMassToSystem(const MechanicalParams* mparams, const unsigned int mstateSize, const Eigen::SparseMatrix<double>& Jeig, Eigen::SparseMatrix<double>& JtKJeig);
    virtual void buildIdentityBlocksInJacobian(core::behavior::BaseMechanicalState* mstate, sofa::core::MatrixDerivId Id);
    virtual void optimizeAndCopyMappingJacobianToEigenFormat1(const typename TDataTypes1::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig);
    virtual void optimizeAndCopyMappingJacobianToEigenFormat2(const typename TDataTypes2::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig);



};


} // namespace interactionforcefield

} // namespace component

} // namespace sofa

#endif // MechanicalMatrixMapperMOR_H
