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
#include "MechanicalMatrixMapperMOR.inl"
#include <sofa/defaulttype/Vec3Types.h>
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
#ifdef SOFA_WITH_FLOAT
        .add< MechanicalMatrixMapperMOR<Vec3fTypes, Rigid3fTypes> >()
        .add< MechanicalMatrixMapperMOR<Rigid3fTypes, Rigid3fTypes> >()
        .add< MechanicalMatrixMapperMOR<Vec3fTypes, Vec3fTypes> >()
        .add< MechanicalMatrixMapperMOR<Vec1fTypes, Rigid3fTypes> >()
        .add< MechanicalMatrixMapperMOR<Vec1fTypes, Vec1fTypes> >()
#endif
#ifdef SOFA_WITH_DOUBLE
        .add< MechanicalMatrixMapperMOR<Vec3dTypes, Rigid3dTypes> >(true)
        .add< MechanicalMatrixMapperMOR<Rigid3dTypes, Rigid3dTypes> >(true)
        .add< MechanicalMatrixMapperMOR<Vec3dTypes, Vec3dTypes> >(true)
        .add< MechanicalMatrixMapperMOR<Vec1dTypes, Rigid3dTypes> >(true)
        .add< MechanicalMatrixMapperMOR<Vec1dTypes, Vec1dTypes> >(true)
#endif
        ;
////////////////////////////////////////////////////////////////////////////////////////////////////////

// Force template specialization for the most common sofa floating point related type.
// This goes with the extern template declaration in the .h. Declaring extern template
// avoid the code generation of the template for each compilation unit.
// see: http://www.stroustrup.com/C++11FAQ.html#extern-templates
#ifdef SOFA_WITH_DOUBLE
template class MechanicalMatrixMapperMOR<Vec3dTypes, Rigid3dTypes>;
template class MechanicalMatrixMapperMOR<Vec3dTypes, Vec3dTypes>;
template class MechanicalMatrixMapperMOR<Vec1dTypes, Rigid3dTypes>;
template class MechanicalMatrixMapperMOR<Vec1dTypes, Vec1dTypes>;
#endif
#ifdef SOFA_WITH_FLOAT
template class MechanicalMatrixMapperMOR<Vec3fTypes, Rigid3fTypes>;
template class MechanicalMatrixMapperMOR<Vec3fTypes, Vec3fTypes>;
template class MechanicalMatrixMapperMOR<Vec1fTypes, Rigid3fTypes>;
template class MechanicalMatrixMapperMOR<Vec1fTypes, Vec1fTypes>;
#endif

} // namespace interactionforcefield

} // namespace component

} // namespace sofa
