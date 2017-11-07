#ifndef SOFA_COMPONENT_LOADER_MATRIXLOADER_INL
#define SOFA_COMPONENT_LOADER_MATRIXLOADER_INL

#include "MatrixLoader.h"
#include <fstream>
#include <string>
#include <sstream>
#include <sofa/helper/logging/Messaging.h>


namespace sofa {
namespace component {
namespace loader {

using std::vector;
using std::string;
using std::stringstream;

template< class EigenMatrixType >
void MatrixLoader<EigenMatrixType>::load(){

    std::ifstream modesFile;
    modesFile.open(m_fileName,std::ios::in);
    if (modesFile.is_open())
    {
        std::string lineValues;  // déclaration d'une chaîne qui contiendra la ligne lue
        unsigned int nbLine = 0;
        msg_info("MatrixLoader") << "[MatrixLoader] Reading file " << m_fileName << " ...";
        while (std::getline(modesFile, lineValues))
        {
            std::stringstream ssin(lineValues);
            if (nbLine == 0){
                ssin >> m_nbRows;
                ssin >> m_nbColumns;
                m_matrix.resize(m_nbRows,m_nbColumns);
            }
            else
            {
                for (unsigned j=0; j<m_nbColumns; j++)
                    ssin >> m_matrix(nbLine-1,j);
            }
            nbLine++;
        }

        modesFile.close();
        if (nbLine-1 != m_nbRows)
            msg_warning("MatrixLoader") << "Problem with matrix file " << m_fileName << " : wrong row number !!!";
    }
    else
    {
        msg_warning("MatrixLoader") << "Could not open matrix file " << m_fileName << " !!!";
    }



}

template< class EigenMatrixType >
void MatrixLoader<EigenMatrixType>::getMatrix(EigenMatrixType& matrix){
    matrix = m_matrix;
}

template< class EigenMatrixType >
void MatrixLoader<EigenMatrixType>::setFileName(string fileName){
    m_fileName = fileName;

}


}
}
}
#endif
