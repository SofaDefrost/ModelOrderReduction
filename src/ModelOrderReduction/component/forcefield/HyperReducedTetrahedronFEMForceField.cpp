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
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_CPP
#include <ModelOrderReduction/component/forcefield/HyperReducedTetrahedronFEMForceField.inl>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/core/ObjectFactory.h>
#include <assert.h>
#include <ModelOrderReduction/config.h>

namespace sofa::component::forcefield
{

using namespace sofa::defaulttype;


SOFA_DECL_CLASS(HyperReducedTetrahedronFEMForceField)

// Register in the Factory
int HyperReducedTetrahedronFEMForceFieldClass = core::RegisterObject("Tetrahedral finite elements")
        .add< HyperReducedTetrahedronFEMForceField<Vec3Types> >()
        ;

template class SOFA_MODELORDERREDUCTION_API HyperReducedTetrahedronFEMForceField<Vec3Types>;
} // namespace sofa::component::forcefield


