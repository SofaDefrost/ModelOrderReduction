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
#ifndef MECHANICALMATRIXMAPPERMOR_INL
#define MECHANICALMATRIXMAPPERMOR_INL

#include "MechanicalMatrixMapperMOR.h"
#include <SofaGeneralAnimationLoop/MechanicalMatrixMapper.inl>
#include <SofaDeformable/SpringForceField.h>
#include <SofaDeformable/StiffSpringForceField.h>
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
MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::MechanicalMatrixMapperMOR()
    :
      performECSW(initData(&performECSW,false,"performECSW",
                           "Use the reduced model with the ECSW method")),
      listActiveNodesPath(initData(&listActiveNodesPath,"listActiveNodesPath",
                                   "Path to the list of active nodes when performing the ECSW method")),
      listActiveNodes(initData(&listActiveNodes,"listActiveNodes",
                                   "list of active nodes when performing the ECSW method")),
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
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::init()
{
    MechanicalMatrixMapper<DataTypes1, DataTypes2>::init();
    //listActiveNodes.resize(0);
    sofa::helper::vector <unsigned int>& listActiveNodesInit = *(listActiveNodes.beginEdit());
    listActiveNodesInit.resize(0);
    if (performECSW.getValue())
    {
        std::ifstream listActiveNodesFile(listActiveNodesPath.getValue(), std::ios::in);
        //nbLine = 0;
        std::string lineValues;  // déclaration d'une chaîne qui contiendra la ligne lue
        while (getline(listActiveNodesFile, lineValues))
        {
            listActiveNodesInit.push_back(std::stoi(lineValues));
            //nbLine++;
        }
        listActiveNodesFile.close();
        msg_info(this) << "list of Active nodes : " << listActiveNodesInit ;
    }
    listActiveNodes.endEdit();
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
    m_nbInteractionForceFieldsMOR = MechanicalMatrixMapper<DataTypes1,DataTypes2>::l_nodeToParse.get()->interactionForceField.size();


}

template<class DataTypes1, class DataTypes2>
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::accumulateJacobiansOptimized(const MechanicalParams* mparams)
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
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::buildIdentityBlocksInJacobian(core::behavior::BaseMechanicalState* mstate, sofa::core::MatrixDerivId Id)
{
    if (performECSW.getValue())
    {

        msg_info(this) << "In buildIdentityBlocksInJacobianMOR, performECSW is true";
        mstate->buildIdentityBlocksInJacobian(listActiveNodes.getValue(), Id);
    }
    else
    {
        msg_info(this) << "In buildIdentityBlocksInJacobianMOR, performECSW is false";
        sofa::helper::vector<unsigned int> list;
        for (unsigned int i=0; i<mstate->getSize(); i++)
            list.push_back(i);
        mstate->buildIdentityBlocksInJacobian(list, Id);
    }
}

template<class DataTypes1, class DataTypes2>
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::optimizeAndCopyMappingJacobianToEigenFormat1(const typename DataTypes1::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig)
{
    msg_info(this) << "type1: ";
    bool timeInvariantMapping = timeInvariantMapping1.getValue();

    sofa::simulation::Node *node = MechanicalMatrixMapper<DataTypes1,DataTypes2>::l_nodeToParse.get();
    size_t currentNbInteractionFFs = node->interactionForceField.size();
    bool mouseInteraction;
    if (m_nbInteractionForceFieldsMOR != currentNbInteractionFFs)
    {

        for(BaseForceField* iforcefield : node->interactionForceField)
        {
            if (iforcefield->getName() == "Spring-Mouse-Contact")
            {
                mouseInteraction = true;
                std::string springData = iforcefield->findData("spring")->getValueString();
                unsigned int index1,mechaIndex;
                std::stringstream ssin(springData);
                ssin >> index1;
                ssin >> mechaIndex;
                sofa::helper::vector <unsigned int>& listActiveNodesUpdate = *(listActiveNodes.beginEdit());
                bool alreadyIn = false;
                for (int i=0;i< listActiveNodesUpdate.size();i++)
                {
                    if (listActiveNodesUpdate[i] == mechaIndex)
                    {
                        alreadyIn = true;
                        break;
                    }
                }
                if (!alreadyIn)
                    listActiveNodesUpdate.push_back(mechaIndex);
                listActiveNodes.endEdit();

            }
            else
            {
                mouseInteraction = false;
            }
        }
        m_nbInteractionForceFieldsMOR = currentNbInteractionFFs;
        if (mouseInteraction)
        {
            msg_info() << "Mouse interaction!";
        }
    }


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
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::optimizeAndCopyMappingJacobianToEigenFormat2(const typename DataTypes2::MatrixDeriv& J, Eigen::SparseMatrix<double>& Jeig)
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
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::addMassToSystem(const MechanicalParams* mparams, const DefaultMultiMatrixAccessor* KAccessor)
{
    if (usePrecomputedMass.getValue() == false)
    {
        if (MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::l_mappedMass != NULL)
        {
            MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::l_mappedMass->addMToMatrix(mparams, KAccessor);
        }
        else
        {
            msg_info(this) << "There is no mappedMass";
        }
    }
}

template<class DataTypes1, class DataTypes2>
void MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::addPrecomputedMassToSystem(const MechanicalParams* mparams,const unsigned int mstateSize, const Eigen::SparseMatrix<double>& Jeig, Eigen::SparseMatrix<double>& JtKJeig)
{
    typedef typename DataTypes1::Real     Real1;

    typedef typename CompressedRowSparseMatrix<Real1>::Range  Range;
    typedef sofa::defaulttype::BaseVector::Index  Index;



    if (this->getContext()->getTime() == 0)
    {
        if (saveReducedMass.getValue() == true)
        {
            if (MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::l_mappedMass != NULL)
            {
                CompressedRowSparseMatrix<typename DataTypes1::Real >* M = new CompressedRowSparseMatrix<typename DataTypes1::Real > ( );
                M->resizeBloc( 3*mstateSize ,  3*mstateSize);
                M->clear();
                DefaultMultiMatrixAccessor* MassAccessor;
                MassAccessor = new DefaultMultiMatrixAccessor;
                MassAccessor->addMechanicalState( this->l_mechanicalState);
                MassAccessor->setGlobalMatrix(M);
                MassAccessor->setupMatrices();
                this->l_mappedMass->addMToMatrix(mparams, MassAccessor);
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
                std::string massName = MechanicalMatrixMapperMOR<DataTypes1, DataTypes2>::l_mappedMass.get()->getName() + "_reduced.txt";
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

} // namespace interactionforcefield

} // namespace component

} // namespace sofa

#endif // MechanicalMatrixMapperMOR_INL
