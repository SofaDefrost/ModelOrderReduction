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

#include <fstream>

namespace modelorderreduction
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

}
