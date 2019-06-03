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

#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_CPP

#include "HyperReducedTetrahedronHyperelasticityFEMForceField.inl"
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/Vec3Types.h>
#include <SofaMiscFem/initMiscFEM.h>
namespace sofa
{

namespace component
{

namespace forcefield
{

using namespace sofa::defaulttype;

//////////****************To register in the factory******************

SOFA_DECL_CLASS(HyperReducedTetrahedronHyperelasticityFEMForceField)

// Register in the Factory
int HyperReducedTetrahedronHyperelasticityFEMForceFieldClass = core::RegisterObject("Generic Tetrahedral finite elements")
    .add< HyperReducedTetrahedronHyperelasticityFEMForceField<Vec3Types> >()
    ;

template class SOFA_MODELORDERREDUCTION_API HyperReducedTetrahedronHyperelasticityFEMForceField<Vec3Types>;

} // namespace forcefield

} // namespace component

} // namespace sofa

