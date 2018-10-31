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
#include <sofa/helper/system/PluginManager.h>
using sofa::helper::system::PluginManager;
using sofa::helper::system::Plugin;

#include <sofa/helper/system/DynamicLibrary.h>
using sofa::helper::system::DynamicLibrary;

#include <sofa/helper/system/FileSystem.h>
using sofa::helper::system::FileSystem;

#include <sofa/helper/Utils.h>
using sofa::helper::Utils;

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

	            std::string configFilePath = modulePath + "/../etc/sofa/python.d/" + getModuleName();
	            std::ifstream configFile(configFilePath.c_str());

	            if (configFile.is_open())
	            {
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
		        else
		        {
		        	std::cout << "File in configFilePath : " << configFilePath.c_str() << "not found" << std::endl; 
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
		return "The ModelOrderReduction plugin builds reduced models by reducing the computational complexity of the system";
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

