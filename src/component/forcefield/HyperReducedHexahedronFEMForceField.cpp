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
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDHEXAHEDRONFEMFORCEFIELD_CPP
#include "HyperReducedHexahedronFEMForceField.inl"
#include <sofa/defaulttype/Vec3Types.h>
#include <sofa/core/ObjectFactory.h>


namespace sofa
{

namespace component
{

namespace forcefield
{

using namespace sofa::defaulttype;


SOFA_DECL_CLASS(HyperReducedHexahedronFEMForceField)

// Register in the Factory
int HyperReducedHexahedronFEMForceFieldClass = core::RegisterObject("Hexahedral finite elements")
        .add< HyperReducedHexahedronFEMForceField<Vec3Types> >()
        ;

template class SOFA_MODELORDERREDUCTION_API HyperReducedHexahedronFEMForceField<Vec3Types>;

} // namespace forcefield

} // namespace component

} // namespace sofa

