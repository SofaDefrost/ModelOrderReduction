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
#ifndef SOFA_COMPONENT_LOADER_MATRIXLOADER_CPP
#define SOFA_COMPONENT_LOADER_MATRIXLOADER_CPP

#include "MatrixLoader.inl"
#include <Eigen/Sparse>
#include <Eigen/Dense>


namespace sofa {
namespace component {
namespace loader {

template class MatrixLoader<Eigen::MatrixXd>;
template class MatrixLoader<Eigen::MatrixXf>;
template class MatrixLoader<Eigen::MatrixXi>;
template class MatrixLoader<Eigen::VectorXd>;
template class MatrixLoader<Eigen::VectorXf>;
template class MatrixLoader<Eigen::VectorXi>;
}
}
}
#endif
