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
#ifndef INITMODELORDERREDUCTION_H
#define INITMODELORDERREDUCTION_H


#include <sofa/helper/system/config.h>

#ifdef SOFA_BUILD_MODELORDERREDUCTION
#define SOFA_MODELORDERREDUCTION_API SOFA_EXPORT_DYNAMIC_LIBRARY
#else
#define SOFA_MODELORDERREDUCTION_API  SOFA_IMPORT_DYNAMIC_LIBRARY
#endif

/** \mainpage
  This is a the starting page of the plugin documentation, defined in file initModelOrderReduction.h
  */

#endif // INITINITMODELORDERREDUCTION_H


