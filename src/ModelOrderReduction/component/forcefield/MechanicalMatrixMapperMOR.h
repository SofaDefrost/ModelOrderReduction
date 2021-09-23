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
#include <ModelOrderReduction/config.h>

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
    size_t m_nbInteractionForceFieldsMOR;
    bool m_mouseInteraction;

public:
    Data< bool > performECSW;
    sofa::core::objectmodel::DataFileName listActiveNodesPath;
    Data <sofa::type::vector<unsigned int>> listActiveNodes;
    int nbActiveNodesAtStart;
    Data< bool > timeInvariantMapping1;
    Data< bool > timeInvariantMapping2;
    Eigen::SparseMatrix<double> constantJ1;
    Eigen::SparseMatrix<double> constantJ2;

    Data< bool > saveReducedMass;
    Data< bool > usePrecomputedMass;
    sofa::core::objectmodel::DataFileName precomputedMassPath;
    Eigen::SparseMatrix<double> JtMJ;


public:

    virtual void init() override;

protected:
    virtual void accumulateJacobiansOptimized(const MechanicalParams* mparams) override;
    virtual void addMassToSystem(const MechanicalParams* mparams, const DefaultMultiMatrixAccessor* KAccessor) override;
    virtual void addPrecomputedMassToSystem(const MechanicalParams* mparams, const unsigned int mstateSize, const Eigen::SparseMatrix<double>& Jeig, Eigen::SparseMatrix<double>& JtKJeig) override;
    virtual void buildIdentityBlocksInJacobian(core::behavior::BaseMechanicalState* mstate, sofa::core::MatrixDerivId Id) override;
    virtual void optimizeAndCopyMappingJacobianToEigenFormat1(const typename TDataTypes1::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig) override;
    virtual void optimizeAndCopyMappingJacobianToEigenFormat2(const typename TDataTypes2::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig) override;



};

#if !defined(SOFA_COMPONENT_FORCEFIELD_MECHANICALMATRIXMAPPERMOR_CPP)
extern template class SOFA_MODELORDERREDUCTION_API MechanicalMatrixMapperMOR<sofa::defaulttype::Vec3Types, sofa::defaulttype::Rigid3Types>;
extern template class SOFA_MODELORDERREDUCTION_API MechanicalMatrixMapperMOR<sofa::defaulttype::Vec3Types, sofa::defaulttype::Vec3Types>;
extern template class SOFA_MODELORDERREDUCTION_API MechanicalMatrixMapperMOR<sofa::defaulttype::Vec1Types, sofa::defaulttype::Rigid3Types>;
extern template class SOFA_MODELORDERREDUCTION_API MechanicalMatrixMapperMOR<sofa::defaulttype::Vec1Types, sofa::defaulttype::Vec1Types>;
#endif // !defined(SOFA_COMPONENT_FORCEFIELD_MECHANICALMATRIXMAPPERMOR_CPP)

} // namespace interactionforcefield

} // namespace component

} // namespace sofa

#endif // MechanicalMatrixMapperMOR_H
