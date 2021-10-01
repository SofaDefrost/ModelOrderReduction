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
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGSFORCEFIELD_CPP

#include "HyperReducedRestShapeSpringsForceField.inl"

#include <sofa/helper/visual/DrawTool.h>
#include <sofa/core/ObjectFactory.h>

namespace sofa
{

namespace component
{

namespace forcefield
{

using namespace sofa::defaulttype;


SOFA_DECL_CLASS(HyperReducedRestShapeSpringsForceField)


int HyperReducedRestShapeSpringsForceFieldClass = core::RegisterObject("Simple elastic springs applied to given degrees of freedom between their current and rest shape position")
        .add< HyperReducedRestShapeSpringsForceField<Vec3Types> >()
        ;

template class SOFA_MODELORDERREDUCTION_API HyperReducedRestShapeSpringsForceField<Vec3Types>;

} // namespace forcefield

} // namespace component

} // namespace sofa
