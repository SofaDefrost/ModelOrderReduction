/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, version 1.0 RC 1        *
*                (c) 2006-2011 MGH, INRIA, USTL, UJF, CNRS                    *
*                                                                             *
* This library is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This library is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this library; if not, write to the Free Software Foundation,     *
* Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.          *
*******************************************************************************
*                               SOFA :: Modules                               *
*                                                                             *
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
******************************************************************************/
#ifndef SOFA_COMPONENT_FORCEFIELD_MAPPEDMATRIXFORCEFIELDANDMASSMOR_INL
#define SOFA_COMPONENT_FORCEFIELD_MAPPEDMATRIXFORCEFIELDANDMASSMOR_INL

#include "MappedMatrixForceFieldAndMassMOR.h"
#include "MappedMatrixForceFieldAndMass.inl"

#include "../loader/MatrixLoader.h"

#include <fstream>


namespace sofa
{

namespace component
{

namespace interactionforcefield
{

using sofa::component::loader::MatrixLoader;

template<typename DataTypes1, typename DataTypes2>
MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::MappedMatrixForceFieldAndMassMOR()
    :
      performECSW(initData(&performECSW,false,"performECSW",
                           "Use the reduced model with the ECSW method")),
      listActiveNodesPath(initData(&listActiveNodesPath,"listActiveNodesPath",
                                   "Path to the list of active nodes when performing the ECSW method")),
      timeInvariantMapping1(initData(&timeInvariantMapping1,false,"timeInvariantMapping1",
                                     "Are the mapping matrices to the first mechanicalObject constant with time? If yes, set to true to avoid useless recomputations.")),
      timeInvariantMapping2(initData(&timeInvariantMapping2,false,"timeInvariantMapping2",
                                     "Are the mapping matrices to the second mechanicalObject constant with time? If yes, set to true to avoid useless recomputations.")),
      saveReducedMass(initData(&saveReducedMass,false,"saveReducedMass",
                               "Save the mass in the reduced space: Jt*M*J. Only make sense if timeInvariantMapping is set to true.")),
      usePrecomputedMass(initData(&usePrecomputedMass,false,"usePrecomputedMass",
                                  "Skip computation of the mass by using the value of the precomputed mass in the reduced space: Jt*M*J")),
      precomputedMassPath(initData(&precomputedMassPath,"precomputedMassPath",
                                   "Path to the precomputed reduced Mass Matrix Jt*M*J. usePrecomputedMass has to be set to true."))



{
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::init()
{
    MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::init();

    listActiveNodes.resize(0);
    if (performECSW.getValue())
    {
        std::ifstream listActiveNodesFile(listActiveNodesPath.getValue(), std::ios::in);
        //nbLine = 0;
        std::string lineValues;  // déclaration d'une chaîne qui contiendra la ligne lue
        while (getline(listActiveNodesFile, lineValues))
        {
            listActiveNodes.push_back(std::stoi(lineValues));
            //nbLine++;
        }
        listActiveNodesFile.close();
        msg_info(this) << "list of Active nodes : " << listActiveNodes ;
    }
    if (usePrecomputedMass.getValue() == true)
    {
        Eigen::MatrixXd denseJtMJ;
        MatrixLoader<Eigen::MatrixXd>* matLoader = new MatrixLoader<Eigen::MatrixXd>();
        matLoader->setFileName(precomputedMassPath.getValue());
        matLoader->load();
        matLoader->getMatrix(denseJtMJ);
        delete matLoader;
        JtMJ = denseJtMJ.sparseView();

    }

}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::accumulateJacobiansOptimized(const MechanicalParams* mparams)
{
    if (((timeInvariantMapping1.getValue() || timeInvariantMapping2.getValue()) == false) || (this->getContext()->getTime() == 0))
    {
        this->accumulateJacobians(mparams);
    }
    else
    {
        msg_info(this) <<"Skipping Jacobian computation.";
    }
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::buildIdentityBlocksInJacobian(core::behavior::BaseMechanicalState* mstate, sofa::core::MatrixDerivId Id)
{
    if (performECSW.getValue())
    {
        msg_info(this) << "In buildIdentityBlocksInJacobianMOR, performECSW is true";
        mstate->buildIdentityBlocksInJacobian(listActiveNodes, Id);
    }
    else
    {
        msg_info(this) << "In buildIdentityBlocksInJacobianMOR, performECSW is false";
        sofa::helper::vector<unsigned int> list;
        std::cout << "mstate->getSize()" << mstate->getSize() << std::endl;
        for (unsigned int i=0; i<mstate->getSize(); i++)
            list.push_back(i);
        mstate->buildIdentityBlocksInJacobian(list, Id);
    }
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::optimizeAndCopyMappingJacobianToEigenFormat1(const typename DataTypes1::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig)
{
    msg_info(this) << "type1: ";
    bool timeInvariantMapping = timeInvariantMapping1.getValue();



    if ((timeInvariantMapping == false) || (this->getContext()->getTime() == 0))
    {
        copyMappingJacobianToEigenFormat<DataTypes1>(J, Jeig);
    }

    if (timeInvariantMapping == true){
        if (this->getContext()->getTime() == 0)
        {
            constantJ1.resize(Jeig.rows(), Jeig.cols());
            constantJ1.reserve(Eigen::VectorXi::Constant(Jeig.rows(),Jeig.cols()));
            constantJ1 = Jeig;
        }
        else
        {
            Jeig = constantJ1;
        }
    }
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::optimizeAndCopyMappingJacobianToEigenFormat2(const typename DataTypes2::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig)
{

    msg_info(this) << "type2: ";
    bool timeInvariantMapping = timeInvariantMapping2.getValue();



    if ((timeInvariantMapping == false) || (this->getContext()->getTime() == 0))
    {
        copyMappingJacobianToEigenFormat<DataTypes2>(J, Jeig);
    }

    if (timeInvariantMapping == true){
        if (this->getContext()->getTime() == 0)
        {
            constantJ2.resize(Jeig.rows(), Jeig.cols());
            constantJ2.reserve(Eigen::VectorXi::Constant(Jeig.rows(),Jeig.cols()));
            constantJ2 = Jeig;
        }
        else
        {
            Jeig = constantJ2;
        }
    }
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::addMassToSystem(const MechanicalParams* mparams, const DefaultMultiMatrixAccessor* KAccessor)
{
    if (usePrecomputedMass.getValue() == false)
    {
        if (MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::d_mappedMass != NULL)
        {
            MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::d_mappedMass.get()->addMToMatrix(mparams, KAccessor);
        }
        else
        {
            msg_info(this) << "There is no d_mappedMass";
        }
    }
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMassMOR<DataTypes1, DataTypes2>::addPrecomputedMassToSystem(const MechanicalParams* mparams,const unsigned int mstateSize, const Eigen::SparseMatrix<double>& Jeig, Eigen::SparseMatrix<double>& JtKJeig)
{
    typedef typename DataTypes1::Real     Real1;

    typedef typename CompressedRowSparseMatrix<Real1>::Range  Range;
    typedef sofa::defaulttype::BaseVector::Index  Index;



    if (this->getContext()->getTime() == 0)
    {
        if (saveReducedMass.getValue() == true)
        {
            if (MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::d_mappedMass != NULL)
            {
                CompressedRowSparseMatrix<typename DataTypes1::Real >* M = new CompressedRowSparseMatrix<typename DataTypes1::Real > ( );
                M->resizeBloc( 3*mstateSize ,  3*mstateSize);
                M->clear();
                DefaultMultiMatrixAccessor* MassAccessor;
                MassAccessor = new DefaultMultiMatrixAccessor;
                MassAccessor->addMechanicalState(  MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::d_mappedMass.get()->getContext()->getMechanicalState() );
                MassAccessor->setGlobalMatrix(M);
                MassAccessor->setupMatrices();
                MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::d_mappedMass.get()->addMToMatrix(mparams, MassAccessor);
                M->compress();

                std::vector< Eigen::Triplet<double> > tripletListM;
                tripletListM.reserve(M->colsValue.size());
                Eigen::SparseMatrix<double,Eigen::ColMajor> Meig(M->nRow,M->nRow);
                int row;
                for (unsigned int it_rows_m=0; it_rows_m < M->rowIndex.size() ; it_rows_m ++)
                {
                    row = M->rowIndex[it_rows_m] ;
                    Range rowRange( M->rowBegin[it_rows_m], M->rowBegin[it_rows_m+1] );
                    for( Index xj = rowRange.begin() ; xj < rowRange.end() ; xj++ )  // for each non-null block
                    {
                        int col = M->colsIndex[xj];     // block column
                        const typename DataTypes1::Real& m = M->colsValue[xj]; // non-null element of the matrix
                        tripletListM.push_back(Eigen::Triplet<double>(row,col,m));
                    }
                }
                Meig.setFromTriplets(tripletListM.begin(), tripletListM.end());
                unsigned int nbColsJ1 = JtKJeig.cols();
                Eigen::SparseMatrix<double>  JtMJeigen(nbColsJ1,nbColsJ1);
                JtMJeigen = Jeig.transpose()*Meig*Jeig;
                msg_info(this) << JtMJeigen;
                std::string massName = MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::d_mappedMass.get()->getName() + "_reduced.txt";
                msg_info(this) << "Storing " << massName << " ... ";
                std::ofstream file(massName);
                if (file.is_open())
                {
                    file << nbColsJ1 << ' ' << nbColsJ1 << "\n";
                    for (unsigned int i=0; i<nbColsJ1; i++)
                    {
                        for (unsigned int j=0; j<nbColsJ1; j++)
                        {
                            file << JtMJeigen.coeff(i,j) << ' ';
                        }
                        file << '\n';
                    }
                    file.close();

                }

            }
            else
            {
                msg_warning(this) << "Cannot save reduced mass because mappedMass is NULL. Please fill the field mappedMass to save the mass.";
            }
        }
    }
    if (usePrecomputedMass.getValue() == true)
    {
        msg_info(this) << "Adding reduced precomputed mass ...";
        JtKJeig = JtKJeig + JtMJ;
    }


}

}
}
}




















#endif
