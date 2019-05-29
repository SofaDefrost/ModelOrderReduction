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
#include <ModelOrderReduction/initModelOrderReduction.h>

#ifdef MOR_PYTHON
#include <SofaPython/PythonEnvironment.h>
using sofa::simulation::PythonEnvironment;
#endif

#include <fstream>

namespace sofa
{
namespace component
{

//Here are just several convenient functions to help user to know what contains the plugin

extern "C" {
    SOFA_MODELORDERREDUCTION_API void initExternalModule();
    SOFA_MODELORDERREDUCTION_API const char* getModuleName();
    SOFA_MODELORDERREDUCTION_API const char* getModuleVersion();
    SOFA_MODELORDERREDUCTION_API const char* getModuleLicense();
    SOFA_MODELORDERREDUCTION_API const char* getModuleDescription();
    SOFA_MODELORDERREDUCTION_API const char* getModuleComponentList();
}

void initExternalModule()
{
    static bool first = true;
    if (first)
    {
        first = false;
    }

#ifdef MOR_PYTHON
    PythonEnvironment::addPythonModulePathsForPluginsByName(getModuleName());
#endif
}

const char* getModuleName()
{
  return "ModelOrderReduction";
}

const char* getModuleVersion()
{
    return "1.0";
}

const char* getModuleLicense()
{
    return "GPL";
}


const char* getModuleDescription()
{
    return "The ModelOrderReduction plugin builds reduced models by reducing the computational complexity of the system";
}

const char* getModuleComponentList()
{
  /// string containing the names of the classes provided by the plugin
  return "";
  //return "MyMappingPendulumInPlane, MyBehaviorModel, MyProjectiveConstraintSet";
}


} // namespace component
} // namespace sofa
