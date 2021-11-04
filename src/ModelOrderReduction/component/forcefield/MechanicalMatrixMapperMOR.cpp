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
#define SOFA_COMPONENT_FORCEFIELD_MECHANICALMATRIXMAPPERMOR_CPP


#include "MechanicalMatrixMapperMOR.inl"
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/ObjectFactory.h>

namespace sofa
{

namespace component
{

namespace interactionforcefield
{

using namespace sofa::defaulttype;


////////////////////////////////////////////    FACTORY    //////////////////////////////////////////////
// Registering the component
// see: http://wiki.sofa-framework.org/wiki/ObjectFactory
// 1-SOFA_DECL_CLASS(componentName) : Set the class name of the component
// 2-RegisterObject("description") + .add<> : Register the component
// 3-.add<>(true) : Set default template
SOFA_DECL_CLASS(MechanicalMatrixMapperMOR)

int MechanicalMatrixMapperMORClass = core::RegisterObject("Partially rigidify a mechanical object using a rigid mapping.")
        .add< MechanicalMatrixMapperMOR<Vec3Types, Rigid3Types> >()
        .add< MechanicalMatrixMapperMOR<Rigid3Types, Rigid3Types> >()
        .add< MechanicalMatrixMapperMOR<Vec3Types, Vec3Types> >()
        .add< MechanicalMatrixMapperMOR<Vec1Types, Rigid3Types> >()
        .add< MechanicalMatrixMapperMOR<Vec1Types, Vec1Types> >()
        ;
////////////////////////////////////////////////////////////////////////////////////////////////////////

// Force template specialization for the most common sofa floating point related type.
// This goes with the extern template declaration in the .h. Declaring extern template
// avoid the code generation of the template for each compilation unit.
// see: http://www.stroustrup.com/C++11FAQ.html#extern-templates
template class MechanicalMatrixMapperMOR<Vec3Types, Rigid3Types>;
template class MechanicalMatrixMapperMOR<Vec3Types, Vec3Types>;
template class MechanicalMatrixMapperMOR<Vec1Types, Rigid3Types>;
template class MechanicalMatrixMapperMOR<Vec1Types, Vec1Types>;

} // namespace interactionforcefield

} // namespace component

} // namespace sofa
