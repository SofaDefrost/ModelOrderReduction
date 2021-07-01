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
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTRIANGLEFEMFORCEFIELD_CPP

#include "HyperReducedTriangleFEMForceField.inl"
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>

// #define DEBUG_TRIANGLEFEM

namespace sofa
{

namespace component
{

namespace forcefield
{

SOFA_DECL_CLASS(HyperReducedTriangleFEMForceField)

using namespace sofa::defaulttype;

// Register in the Factory
int HyperReducedTriangleFEMForceFieldClass = core::RegisterObject("Triangular finite elements")
        .add< HyperReducedTriangleFEMForceField<Vec3Types> >()
        ;

template class SOFA_MODELORDERREDUCTION_API HyperReducedTriangleFEMForceField<Vec3Types>;

} // namespace forcefield

} // namespace component

} // namespace sofa
