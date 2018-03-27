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
