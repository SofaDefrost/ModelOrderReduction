/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, version 1.0 RC 1        *
*                (c) 2006-2011 MGH, INRIA, USTL, UJF, CNRS                    *
*                                                                             *
* This library is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This library is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this library; if not, write to the Free Software Foundation,     *
* Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.          *
*******************************************************************************
*                               SOFA :: Modules                               *
*                                                                             *
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
******************************************************************************/
#ifndef SOFA_COMPONENT_FORCEFIELD_MAPPEDMATRIXFORCEFIELDANDMASSMOR_INL
#define SOFA_COMPONENT_FORCEFIELD_MAPPEDMATRIXFORCEFIELDANDMASSMOR_INL

#include <ModelOrderReduction/component/forcefield/MappedMatrixForceFieldAndMassMOR.h>


namespace sofa
{

namespace component
{

namespace interactionforcefield
{


template<typename DataTypes1, typename DataTypes2>
MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::MappedMatrixForceFieldAndMassMOR()
    :
      performECSW(initData(&performECSW,false,"performECSW",
                                    "Use the reduced model with the ECSW method"))

{
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::buildIdentityBlocksInJacobian(core::behavior::BaseMechanicalState* mstate, sofa::core::MatrixDerivId Id)
{
    if (performECSW.getValue())
    {
        mstate->buildIdentityBlocksInJacobian(listActiveNodes, Id);
    }
    else
    {
        sofa::helper::vector<unsigned int> list;
        std::cout << "mstate->getSize()" << mstate->getSize() << std::endl;
        for (unsigned int i=0; i<mstate->getSize(); i++)
            list.push_back(i);
        mstate->buildIdentityBlocksInJacobian(list, Id);
    }
}

}
}
}




















#endif
