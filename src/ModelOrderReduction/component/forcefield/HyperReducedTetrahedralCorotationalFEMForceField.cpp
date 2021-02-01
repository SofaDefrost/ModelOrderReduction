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
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRALCOROTATIONALFEMFORCEFIELD_CPP

#include "HyperReducedTetrahedralCorotationalFEMForceField.inl"
#include <sofa/defaulttype/VecTypes.h>
#include <SofaBaseMechanics/MechanicalObject.h>
#include <sofa/core/ObjectFactory.h>
//#include <typeinfo>


namespace sofa
{

namespace component
{

namespace forcefield
{

using namespace sofa::defaulttype;


SOFA_DECL_CLASS(HyperReducedTetrahedralCorotationalFEMForceField)

// Register in the Factory
int HyperReducedTetrahedralCorotationalFEMForceFieldClass = core::RegisterObject("Corotational FEM Tetrahedral finite elements")
        .add< HyperReducedTetrahedralCorotationalFEMForceField<Vec3Types> >()
        ;

template class SOFA_MODELORDERREDUCTION_API HyperReducedTetrahedralCorotationalFEMForceField<Vec3Types>;

} // namespace forcefield

} // namespace component

} // namespace sofa

