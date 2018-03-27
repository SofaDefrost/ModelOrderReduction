#ifndef SOFA_COMPONENT_LOADER_MATRIXLOADER_H
#define SOFA_COMPONENT_LOADER_MATRIXLOADER_H

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
