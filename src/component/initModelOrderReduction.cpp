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
#include "initModelOrderReduction.h"

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
	    typedef std::map<std::string, Plugin > PluginMap;
	    typedef PluginMap::iterator PluginIterator;

	    PluginMap&  map = PluginManager::getInstance().getPluginMap();
	    for( const auto& elem : map)
	    {
	        Plugin p = elem.second;
	        if ( p.getModuleName() == getModuleName() )
	        {
	            std::string modulePath = elem.first;
	            modulePath.resize( modulePath.find(getModuleName() + std::string(".") + DynamicLibrary::extension) );
	            modulePath = FileSystem::getParentDirectory( modulePath );
	            std::cout << "modulePath = " << modulePath << std::endl;

	            std::string configFilePath = modulePath + "/etc/sofa/python.d/" + getModuleName();
	            std::ifstream configFile(configFilePath.c_str());
	            std::string line;
	            while(std::getline(configFile, line))
	            {
	                if (!FileSystem::isAbsolute(line))
	                {
	                    line = modulePath + "/" + line;
	                }
	                PythonEnvironment::addPythonModulePath(line);
	            }
	        }
	    }
#endif
	}

	const char* getModuleName()
	{
	  return "ModelOrderReduction";
	}

	const char* getModuleVersion()
	{
		return "0.2";
	}

	const char* getModuleLicense()
	{
		return "LGPL";
	}


	const char* getModuleDescription()
	{
		return "TODO: replace this with the description of your plugin";
	}

	const char* getModuleComponentList()
	{
	  /// string containing the names of the classes provided by the plugin
	  return "";
	  //return "MyMappingPendulumInPlane, MyBehaviorModel, MyProjectiveConstraintSet";
	}



} 

} 

/// Use the SOFA_LINK_CLASS macro for each class, to enable linking on all platforms
//SOFA_LINK_CLASS(MyMappingPendulumInPlane)
//SOFA_LINK_CLASS(MyBehaviorModel)
//SOFA_LINK_CLASS(MyProjectiveConstraintSet)

