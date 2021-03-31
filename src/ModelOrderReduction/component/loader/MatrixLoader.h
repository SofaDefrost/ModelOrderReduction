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
#ifndef SOFA_COMPONENT_LOADER_MATRIXLOADER_H
#define SOFA_COMPONENT_LOADER_MATRIXLOADER_H
#include <ModelOrderReduction/config.h>

#include <iostream>
#include <vector>

namespace sofa {
namespace component {
namespace loader {

template< class EigenMatrixType >
class MatrixLoader {

public:

    MatrixLoader(){}
    virtual ~MatrixLoader(){}

    void load();
    void getMatrix(EigenMatrixType& matrix);
    void setFileName(std::string fileName);

    bool m_printLog = false;

protected:

    unsigned int m_nbRows;
    unsigned int m_nbColumns;
    std::string m_fileName;
    EigenMatrixType m_matrix;

};



}
}
}

#endif
