#ifndef MAPPEDMATRIXFORCEFIELDANDMASSMOR_H
#define MAPPEDMATRIXFORCEFIELDANDMASSMOR_H


#include <ModelOrderReduction/component/forcefield/MappedMatrixForceFieldAndMass.h>

namespace sofa
{

namespace component
{

namespace interactionforcefield
{


template<typename TDataTypes1, typename TDataTypes2>
class MappedMatrixForceFieldAndMassMOR : public MappedMatrixForceFieldAndMass<TDataTypes1, TDataTypes2>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE2(MappedMatrixForceFieldAndMassMOR, TDataTypes1, TDataTypes2), SOFA_TEMPLATE2(MappedMatrixForceFieldAndMass, TDataTypes1, TDataTypes2));
    typedef MappedMatrixForceFieldAndMass<TDataTypes1, TDataTypes2> Inherit;



protected:
    MappedMatrixForceFieldAndMassMOR();

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

















#endif // MAPPEDMATRIXFORCEFIELDANDMASSMOR_H
