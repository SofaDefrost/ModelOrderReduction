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
#include <sofa/defaulttype/Vec3Types.h>
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
#ifndef SOFA_FLOAT
        .add< HyperReducedTetrahedralCorotationalFEMForceField<Vec3dTypes> >()
#endif
#ifndef SOFA_DOUBLE
        .add< HyperReducedTetrahedralCorotationalFEMForceField<Vec3fTypes> >()
#endif
        ;

#ifndef SOFA_FLOAT
template class SOFA_GENERAL_SIMPLE_FEM_API HyperReducedTetrahedralCorotationalFEMForceField<Vec3dTypes>;
#endif
#ifndef SOFA_DOUBLE
template class SOFA_GENERAL_SIMPLE_FEM_API HyperReducedTetrahedralCorotationalFEMForceField<Vec3fTypes>;
#endif

} // namespace forcefield

} // namespace component

} // namespace sofa

