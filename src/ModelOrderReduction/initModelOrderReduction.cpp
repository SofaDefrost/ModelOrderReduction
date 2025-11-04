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
#include <ModelOrderReduction/config.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/helper/system/PluginManager.h>

#include <fstream>

namespace sofa::component::solidmechanics::spring
{
    extern void registerHyperReducedRestShapeSpringsForceField(sofa::core::ObjectFactory* factory);
}
namespace sofa::component::solidmechanics::fem::elastic
{
    extern void registerHyperReducedTetrahedralCorotationalFEMForceField(sofa::core::ObjectFactory* factory);
    extern void registerHyperReducedTriangleFEMForceField(sofa::core::ObjectFactory* factory);
}
namespace sofa::component::forcefield
{
    extern void registerHyperReducedHexahedronFEMForceField(sofa::core::ObjectFactory* factory);
    extern void registerHyperReducedTetrahedronHyperelasticityFEMForceField(sofa::core::ObjectFactory* factory);
    extern void registerHyperReducedTetrahedronFEMForceField(sofa::core::ObjectFactory* factory);
}
namespace sofa::component::mapping
{
    extern void registerMORContactMapping(sofa::core::ObjectFactory* factory);
    extern void registerModelOrderReductionMapping(sofa::core::ObjectFactory* factory);
}
namespace sofa::component::constraint::lagrangian::model
{
    extern void registerMORUnilateralInteractionConstraint(sofa::core::ObjectFactory* factory);
}
namespace sofa::component::collision::geometry
{
    extern void registerMORPointCollisionModel(sofa::core::ObjectFactory* factory);
}

namespace modelorderreduction
{
//Here are just several convenient functions to help user to know what contains the plugin

extern "C" {
    SOFA_MODELORDERREDUCTION_API void initExternalModule();
    SOFA_MODELORDERREDUCTION_API const char* getModuleName();
    SOFA_MODELORDERREDUCTION_API const char* getModuleVersion();
    SOFA_MODELORDERREDUCTION_API const char* getModuleLicense();
    SOFA_MODELORDERREDUCTION_API const char* getModuleDescription();
    SOFA_MODELORDERREDUCTION_API void registerObjects(sofa::core::ObjectFactory* factory);
}

void initExternalModule()
{
    static bool first = true;
    if (first)
    {
        // make sure that this plugin is registered into the PluginManager
        sofa::helper::system::PluginManager::getInstance().registerPlugin(MODULE_NAME);

        first = false;
    }
}

const char* getModuleName()
{
  return MODULE_NAME;
}

const char* getModuleVersion()
{
    return MODULE_VERSION;
}

const char* getModuleLicense()
{
    return "GPL";
}


void registerObjects(sofa::core::ObjectFactory* factory)
{
    sofa::component::solidmechanics::spring::registerHyperReducedRestShapeSpringsForceField(factory);
    sofa::component::solidmechanics::fem::elastic::registerHyperReducedTetrahedralCorotationalFEMForceField( factory);
    sofa::component::solidmechanics::fem::elastic::registerHyperReducedTriangleFEMForceField(factory);
    sofa::component::forcefield::registerHyperReducedHexahedronFEMForceField(factory);
    sofa::component::forcefield::registerHyperReducedTetrahedronHyperelasticityFEMForceField(factory);
    sofa::component::forcefield::registerHyperReducedTetrahedronFEMForceField(factory);
    sofa::component::mapping::registerMORContactMapping(factory);
    sofa::component::mapping::registerModelOrderReductionMapping(factory);
    sofa::component::constraint::lagrangian::model::registerMORUnilateralInteractionConstraint(factory);
    sofa::component::collision::geometry::registerMORPointCollisionModel(factory);
}

}
