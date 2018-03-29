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

public:

    virtual void init();

protected:
    virtual void buildIdentityBlocksInJacobian(core::behavior::BaseMechanicalState* mstate, sofa::core::MatrixDerivId Id);


};


} // namespace interactionforcefield

} // namespace component

} // namespace sofa

















#endif // MAPPEDMATRIXFORCEFIELDANDMASSMOR_H
