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
#ifndef SOFA_COMPONENT_FORCEFIELD_MappedMatrixForceFieldAndMass_INL
#define SOFA_COMPONENT_FORCEFIELD_MappedMatrixForceFieldAndMass_INL


#include "MappedMatrixForceFieldAndMass.h"
#include <sofa/core/visual/VisualParams.h>
#include <sofa/helper/gl/template.h>
#include <sofa/helper/system/config.h>
#include <sofa/helper/system/glut.h>
#include <sofa/helper/rmath.h>
#include <assert.h>
#include <iostream>
#include <fstream>

// accumulate jacobian
#include <sofa/core/ExecParams.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/MapMapSparseMatrix.h>

// verify timing
#include <sofa/helper/system/thread/CTime.h>

//  Sparse Matrix
#include <Eigen/Sparse>
#include "../loader/modules/MatrixLoader.h"

namespace sofa
{

namespace component
{

namespace interactionforcefield
{

using sofa::component::linearsolver::DefaultMultiMatrixAccessor ;
using sofa::core::behavior::BaseMechanicalState ;
using sofa::component::loader::MatrixLoader;



template<class DataTypes1, class DataTypes2>
MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::MappedMatrixForceFieldAndMass()
    :
      d_mappedForceField(initLink("mappedForceField",
                                  "link to the forcefield that is mapped under the subsetMultiMapping")),
      d_mappedForceField2(initLink("mappedForceField2",
                                   "link to an other forcefield defined at the same node than mappedForceField")),
      d_mappedMass(initLink("mappedMass",
                                   "link to a mass defined at the same node than mappedForceField")),
      performECSW(initData(&performECSW,false,"performECSW",
                                    "Use the reduced model with the ECSW method")),
      listActiveNodesPath(initData(&listActiveNodesPath,"listActiveNodesPath",
                                   "Path to the list of active nodes when performing the ECSW method")),
      timeInvariantMapping(initData(&timeInvariantMapping,false,"timeInvariantMapping",
                                    "Are the mapping matrices constant with time? If yes, set to true to avoid useless recomputations.")),
      saveReducedMass(initData(&saveReducedMass,false,"saveReducedMass",
                                    "Use the mass in the reduced space: Jt*M*J")),
      usePrecomputedMass(initData(&usePrecomputedMass,false,"usePrecomputedMass",
                                         "Skip computation of the mass by using the value of the precomputed mass in the reduced space: Jt*M*J")),
      precomputedMassPath(initData(&precomputedMassPath,"precomputedMassPath",
                                       "Path to the precomputed reduced Mass Matrix Jt*M*J. usePrecomputedMass has to be set to true."))


{
}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::init()
{
    sofa::core::behavior::BaseInteractionForceField::init();

    if (mstate1.get() == NULL || mstate2.get() == NULL)
    {
        serr<< "Init of MixedInteractionForceField " << getContext()->getName() << " failed!" << sendl;
        //getContext()->removeObject(this);
        return;
    }

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
        std::cout << "list of Active nodes : " << listActiveNodes << std::endl;
    }
//    else
//    {
//        core::behavior::BaseMechanicalState* mstate = d_mappedForceField.get()->getContext()->getMechanicalState();
//        for (unsigned int i=0; i<mstate->getSize(); i++)
//            listActiveNodes.push_back(i);
//        std::cout << "list of Active nodes : " << listActiveNodes << std::endl;
//    }
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
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::accumulateJacobians(const MechanicalParams* mparams)
{

    // STEP1 : accumulate Jacobians J1 and J2

    const core::ExecParams* eparams = dynamic_cast<const core::ExecParams *>( mparams );
    core::ConstraintParams cparams = core::ConstraintParams(*eparams);

    core::behavior::BaseMechanicalState* mstate = d_mappedForceField.get()->getContext()->getMechanicalState();


    sofa::helper::vector<unsigned int> list;
    if (!performECSW.getValue())
    {
        std::cout << "mstate->getSize()" << mstate->getSize() << std::endl;
        for (unsigned int i=0; i<mstate->getSize(); i++)
            list.push_back(i);
    }


    sofa::core::MatrixDerivId Id= sofa::core::MatrixDerivId::mappingJacobian();

    core::objectmodel::BaseContext* context = this->getContext();
    simulation::Node* gnode = dynamic_cast<simulation::Node*>(context);
    simulation::MechanicalResetConstraintVisitor(eparams).execute(gnode);

    if (performECSW.getValue())
    {
        mstate->buildIdentityBlocksInJacobian(listActiveNodes, Id);
    }
    else
    {
        mstate->buildIdentityBlocksInJacobian(list, Id);
    }
    MechanicalAccumulateJacobian(&cparams, core::MatrixDerivId::mappingJacobian()).execute(gnode);

}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::copyKToEigenFormat(CompressedRowSparseMatrix< Real1 >* K, Eigen::SparseMatrix<double,Eigen::ColMajor>& Keig)
{
    Keig.resize(K->nRow,K->nRow);
    Keig.reserve(K->colsValue.size());
    std::vector< Eigen::Triplet<double> > tripletList;
    tripletList.reserve(K->colsValue.size());

    int row;

    ///////////////////////    COPY K IN EIGEN FORMAT //////////////////////////////////////
    for (unsigned int it_rows_k=0; it_rows_k < K->rowIndex.size() ; it_rows_k ++)
    {
        row = K->rowIndex[it_rows_k] ;
        Range rowRange( K->rowBegin[it_rows_k], K->rowBegin[it_rows_k+1] );
        for( Index xj = rowRange.begin() ; xj < rowRange.end() ; xj++ )  // for each non-null block
        {
            int col = K->colsIndex[xj];     // block column
            const Real1& k = K->colsValue[xj]; // non-null element of the matrix
            tripletList.push_back(Eigen::Triplet<double>(row,col,k));
        }
    }
    Keig.setFromTriplets(tripletList.begin(), tripletList.end());
}




template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::copyMappingJacobian1ToEigenFormat(const MatrixDeriv1 &J, Eigen::SparseMatrix<double>& Jeig)
{
    msg_info(this) << "Start of J1 copy ";
    int nbRowsJ = Jeig.rows();
    int nbColsJ = Jeig.cols();
    int maxColIndex = 0;
    msg_info(this) << "nbRowsJ J1 : " << nbRowsJ;
    msg_info(this) << "nbColsJ J1 : " << nbColsJ;
    std::vector< Eigen::Triplet<double> > tripletListJ;

    for (MatrixDeriv1RowConstIterator rowIt = J.begin(); rowIt !=  J.end(); ++rowIt)
    {
        int rowIndex = rowIt.index();
        for (MatrixDeriv1ColConstIterator colIt = rowIt.begin(); colIt !=  rowIt.end(); ++colIt)
        {
            int colIndex = colIt.index();
            Deriv1 elemVal = colIt.val();
            for (int i=0;i<DerivSize1;i++)
            {
                tripletListJ.push_back(Eigen::Triplet<double>(rowIndex,DerivSize1*colIndex + i,elemVal[i]));
                //msg_info(this) << "Triplet is: " << rowIndex << " " << DerivSize1*colIndex + i << " " << elemVal[i] << "colIndex was:" << colIndex ;
                if (colIndex>maxColIndex)
                        maxColIndex = colIndex;
            }
            //msg_info(this) << "J1: " << elemVal;
        }
    }
    msg_info(this) << "End of J1 copy. MaxColIndex = " << maxColIndex;
    Jeig.resize(nbRowsJ,DerivSize1*(maxColIndex+1));
    Jeig.reserve(J.size());
    msg_info(this) << "End of J1 reserve copy ";
    Jeig.setFromTriplets(tripletListJ.begin(), tripletListJ.end());
    msg_info(this) << "Real End of J1 copy ";


}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::copyMappingJacobian2ToEigenFormat(const MatrixDeriv2 &J, Eigen::SparseMatrix<double>& Jeig)
{
    msg_info(this) << "Start of J2 copy ";
    int nbRowsJ = Jeig.rows();
    int nbColsJ = Jeig.cols();
    int maxColIndex = 0;
    msg_info(this) << "nbRowsJ J2 : " << nbRowsJ;
    msg_info(this) << "nbColsJ J2 : " << nbColsJ;
    std::vector< Eigen::Triplet<double> > tripletListJ;

    for (MatrixDeriv2RowConstIterator rowIt = J.begin(); rowIt !=  J.end(); ++rowIt)
    {
        int rowIndex = rowIt.index();
        for (MatrixDeriv2ColConstIterator colIt = rowIt.begin(); colIt !=  rowIt.end(); ++colIt)
        {
            int colIndex = colIt.index();
            Deriv2 elemVal = colIt.val();
            for (int i=0;i<DerivSize2;i++)
            {
                tripletListJ.push_back(Eigen::Triplet<double>(rowIndex,DerivSize2*colIndex + i,elemVal[i]));
                //msg_info(this) << "Triplet is: " << rowIndex << " " << DerivSize2*colIndex + i << " " << elemVal[i] << "colIndex was:" << colIndex ;
                if (colIndex>maxColIndex)
                        maxColIndex = colIndex;
            }
            //msg_info(this) << "J2: " << elemVal;
        }
    }
    msg_info(this) << "End of J2 copy. MaxColIndex = " << maxColIndex;
    Jeig.resize(nbRowsJ,DerivSize2*(maxColIndex+1));
    Jeig.reserve(J.size());
    msg_info(this) << "End of J2 reserve copy ";
    Jeig.setFromTriplets(tripletListJ.begin(), tripletListJ.end());
    msg_info(this) << "Real End of J2 copy ";
}


template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::addKToMatrix(const MechanicalParams* mparams,
                                                                         const MultiMatrixAccessor* matrix)
{

    sofa::helper::system::thread::CTime *timer;
    double timeScale, time, totime ;
    timeScale = 1000.0 / (double)sofa::helper::system::thread::CTime::getTicksPerSec();

    time = (double)timer->getTime();
    totime = (double)timer->getTime();
    if(f_printLog.getValue())
        sout << "ENTERING addKToMatrix" << sendl;


    sofa::core::behavior::MechanicalState<DataTypes1>* ms1 = this->getMState1();
    sofa::core::behavior::MechanicalState<DataTypes2>* ms2 = this->getMState2();


    sofa::core::behavior::BaseMechanicalState*  bms1 = this->getMechModel1();
    sofa::core::behavior::BaseMechanicalState*  bms2 = this->getMechModel2();
    msg_info(this) << "Same object or not?";
    if (bms1 == bms2)
    {
        msg_info(this) << "Same object ++++++++++++++++++++++++++++++++++++++++++++++++++";
    }
    else
    {
        msg_info(this) << "Not same object ++++++++++++++++++++++++++++++++++++++++++++++++++";
    }


    MultiMatrixAccessor::MatrixRef mat11 = matrix->getMatrix(mstate1);
    MultiMatrixAccessor::MatrixRef mat22 = matrix->getMatrix(mstate2);
    MultiMatrixAccessor::InteractionMatrixRef mat12 = matrix->getMatrix(mstate1, mstate2);
    MultiMatrixAccessor::InteractionMatrixRef mat21 = matrix->getMatrix(mstate2, mstate1);
    msg_info(this)<<"Info about mat11: " <<  mat11->rows() << " "<<  mat11->cols() << " " <<  mat11->bRowSize() << " "<<  mat11->bColSize() << mat11->getElementType();
    msg_info(this)<<mat11;
    msg_info(this)<<"Info about mat12: " <<  mat12->rows() << " "<<  mat12->cols() << " " <<  mat12->bRowSize() << " "<<  mat12->bColSize() << mat12->getElementType();
    msg_info(this)<<mat12;
    msg_info(this)<<"Info about mat21: " <<  mat21->rows() << " "<<  mat21->cols() << " " <<  mat21->bRowSize() << " "<<  mat21->bColSize() << mat21->getElementType();
    msg_info(this)<<mat21;
    msg_info(this)<<"Info about mat22: " <<  mat22->rows() << " "<<  mat22->cols() << " " <<  mat22->bRowSize() << " "<<  mat22->bColSize() << mat22->getElementType();
    msg_info(this)<<mat22;


    ///////////////////////////     STEP 1      ////////////////////////////////////
    /* -------------------------------------------------------------------------- */
    /*              compute jacobians using generic implementation                */
    /* -------------------------------------------------------------------------- */

    if ((timeInvariantMapping.getValue() == false) || (this->getContext()->getTime() == 0))
    {
        this->accumulateJacobians(mparams);
        msg_info(this) <<" accumulate J : "<<( (double)timer->getTime() - time)*timeScale<<" ms";
    }
    else
    {
        msg_info(this) <<"Skipping Jacobian computation.";
    }
    time= (double)timer->getTime();


    ///////////////////////////     STEP 2      ////////////////////////////////////
    /* -------------------------------------------------------------------------- */
    /*  compute the stiffness K of the forcefield and put it in a rowsparseMatrix */
    /*          get the stiffness matrix from the mapped ForceField               */
    /* TODO: use the template of the FF for Real                                  */
    /* -------------------------------------------------------------------------- */


    ///////////////////////     GET K       ////////////////////////////////////////
    core::behavior::BaseMechanicalState* mstate = d_mappedForceField.get()->getContext()->getMechanicalState();
    CompressedRowSparseMatrix< Real1 >* K = new CompressedRowSparseMatrix< Real1 > ( );

    K->resizeBloc( 3*mstate->getSize() ,  3*mstate->getSize());
    K->clear();
    DefaultMultiMatrixAccessor* KAccessor;
    KAccessor = new DefaultMultiMatrixAccessor;
    KAccessor->addMechanicalState(  d_mappedForceField.get()->getContext()->getMechanicalState() );
    KAccessor->setGlobalMatrix(K);
    KAccessor->setupMatrices();


    //------------------------------------------------------------------------------


    msg_info(this)<<" time get K : "<<( (double)timer->getTime() - time)*timeScale<<" ms";
    time= (double)timer->getTime();


    d_mappedForceField.get()->addKToMatrix(mparams, KAccessor);
    //d_mappedForceField2.get()->addKToMatrix(mparams, KAccessor);
    if (d_mappedForceField2 != NULL)
    {
        d_mappedForceField2.get()->addKToMatrix(mparams, KAccessor);
    }

    if (usePrecomputedMass.getValue() == false)
    {
        if (d_mappedMass != NULL)
        {
            d_mappedMass.get()->addMToMatrix(mparams, KAccessor);
        }
        else
        { msg_info(this) << "There is no d_mappedMass"; }
    }
    msg_info(this)<<" time addKtoMatrix K : "<<( (double)timer->getTime() - time)*timeScale<<" ms";
    time= (double)timer->getTime();

    if (!K)
    {
        std::cout<<"matrix of the force-field system not found"<<std::endl;
        return;
    }


    ///////////////////////     COMPRESS K       ///////////////////////////////////
    K->compress();
    //------------------------------------------------------------------------------


    msg_info(this) << " time compress K : "<<( (double)timer->getTime() - time)*timeScale<<" ms";

    ///////////////////////////     STEP 3      ////////////////////////////////////
    /* -------------------------------------------------------------------------- */
    /*                  we now get the matrices J1 and J2                         */
    /* -------------------------------------------------------------------------- */


    msg_info(this)<<" nRow: "<< K->nRow << " nCol: " << K->nCol;


    ///////////////////////////     STEP 4      ////////////////////////////////////
    /* -------------------------------------------------------------------------- */
    /*          perform the multiplication with [J1t J2t] * K * [J1 J2]           */
    /* -------------------------------------------------------------------------- */

    double startTime= (double)timer->getTime();
    msg_info(this) << "listActiveNodes.size() " << listActiveNodes.size();
    Eigen::SparseMatrix<double,Eigen::ColMajor> Keig;
    copyKToEigenFormat(K,Keig);
    msg_info(this) << Keig.size();

    //--------------------------------------------------------------------------------------------------------------------

    msg_info(this)<<" time set Keig : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";
    startTime= (double)timer->getTime();

    ///////////////////////    COPY J1 AND J2 IN EIGEN FORMAT //////////////////////////////////////

    Eigen::SparseMatrix<double> J1eig;
    Eigen::SparseMatrix<double> J2eig;
    unsigned int nbColsJ1 = 0, nbColsJ2 = 0;
    if ((timeInvariantMapping.getValue() == false) || (this->getContext()->getTime() == 0))
    {
        time= (double)timer->getTime();

        sofa::core::MultiMatrixDerivId c = sofa::core::MatrixDerivId::mappingJacobian();
        const MatrixDeriv1 &J1 = c[ms1].read()->getValue();
        MatrixDeriv1RowConstIterator rowItJ1= J1.begin();
        const MatrixDeriv2 &J2 = c[ms2].read()->getValue();
        MatrixDeriv2RowConstIterator rowItJ2= J2.begin();
        msg_info(this)<<"Just got J1. Size=" << J1.size();
        msg_info(this)<<"Just got J2. Size=" << J2.size();

        msg_info(this)<<" time get J : "<<( (double)timer->getTime() - time)*timeScale<<" ms";
        J1eig.resize(K->nRow, J1.begin().row().size()*DerivSize1);
        copyMappingJacobian1ToEigenFormat(J1, J1eig);

        if (bms1 != bms2)
        {
            double startTime2= (double)timer->getTime();
            J2eig.resize(K->nRow, J2.begin().row().size()*DerivSize2);
            copyMappingJacobian2ToEigenFormat(J2, J2eig);
            msg_info(this)<<" time set J2eig alone : "<<( (double)timer->getTime() - startTime2)*timeScale<<" ms";
            //msg_info(this) << "J2eig: " << J2eig;
        }
        //msg_info(this) << "J1eig: " << J1eig;


    }

    if ((timeInvariantMapping.getValue() == true) && (this->getContext()->getTime() == 0))
    {
        constantJ1.resize(J1eig.rows(), J1eig.cols());
        constantJ1.reserve(Eigen::VectorXi::Constant(K->nRow,nbColsJ1));
        constantJ1 = J1eig;
    }

    msg_info(this)<<" time getJ + set J1eig (and potentially J2eig) : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";
    startTime= (double)timer->getTime();

    ///////////////////////     J1t * K * J1    //////////////////////////////////////////////////////////////////////////
    if (timeInvariantMapping.getValue() == true)
    {
        nbColsJ1 = constantJ1.cols();
    }
    else
    {
        msg_info(this) << "J1eig cols() out out of convertFunction: " << J1eig.cols();

        nbColsJ1 = J1eig.cols();
        if (bms1 != bms2)
        {
            nbColsJ2 = J2eig.cols();
        }
    }
    msg_info(this)<<"nbColsJ1 " << nbColsJ1;
    Eigen::SparseMatrix<double>  J1tKJ1eigen(nbColsJ1,nbColsJ1);
    msg_info(this)<<"TOTO ";
    if (timeInvariantMapping.getValue() == true)
    {
        J1tKJ1eigen = constantJ1.transpose()*Keig*constantJ1;
    }
    else
    {
        J1tKJ1eigen = J1eig.transpose()*Keig*J1eig;
    }
    //msg_info(this)<<J1tKJ1eigen;

    if (usePrecomputedMass.getValue() == true)
    {
        msg_info(this) << "Adding reduced precomputed mass ...";
        J1tKJ1eigen = J1tKJ1eigen + JtMJ;
    }
    msg_info(this)<<" time compute J1tKJ1eigen alone : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";

    Eigen::SparseMatrix<double>  J2tKJ2eigen(nbColsJ2,nbColsJ2);
    Eigen::SparseMatrix<double>  J1tKJ2eigen(nbColsJ1,nbColsJ2);
    Eigen::SparseMatrix<double>  J2tKJ1eigen(nbColsJ2,nbColsJ1);

    if (bms1 != bms2)
    {
        double startTime2= (double)timer->getTime();
        J2tKJ2eigen = J2eig.transpose()*Keig*J2eig;
        J1tKJ2eigen = J1eig.transpose()*Keig*J2eig;
        J2tKJ1eigen = J2eig.transpose()*Keig*J1eig;
        msg_info(this)<<" time compute J1tKJ2eigen J2TKJ2 and J2tKJ1 : "<<( (double)timer->getTime() - startTime2)*timeScale<<" ms";

    }

    //--------------------------------------------------------------------------------------------------------------------

    msg_info(this)<<" time compute all JtKJeigen with J1eig and J2eig : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";
    int row;
    if (this->getContext()->getTime() == 0)
    {
        if (saveReducedMass.getValue() == true)
        {
            if (d_mappedMass != NULL)
            {
                CompressedRowSparseMatrix< Real1 >* M = new CompressedRowSparseMatrix< Real1 > ( );
                M->resizeBloc( 3*mstate->getSize() ,  3*mstate->getSize());
                M->clear();
                DefaultMultiMatrixAccessor* MassAccessor;
                MassAccessor = new DefaultMultiMatrixAccessor;
                MassAccessor->addMechanicalState(  d_mappedMass.get()->getContext()->getMechanicalState() );
                MassAccessor->setGlobalMatrix(M);
                MassAccessor->setupMatrices();
                d_mappedMass.get()->addMToMatrix(mparams, MassAccessor);
                M->compress();

                std::vector< Eigen::Triplet<double> > tripletListM;
                tripletListM.reserve(M->colsValue.size());
                Eigen::SparseMatrix<double,Eigen::ColMajor> Meig(M->nRow,M->nRow);
                for (unsigned int it_rows_m=0; it_rows_m < M->rowIndex.size() ; it_rows_m ++)
                {
                    row = M->rowIndex[it_rows_m] ;
                    Range rowRange( M->rowBegin[it_rows_m], M->rowBegin[it_rows_m+1] );
                    for( Index xj = rowRange.begin() ; xj < rowRange.end() ; xj++ )  // for each non-null block
                    {
                        int col = M->colsIndex[xj];     // block column
                        const Real1& m = M->colsValue[xj]; // non-null element of the matrix
                        tripletListM.push_back(Eigen::Triplet<double>(row,col,m));
                    }
                }
                Meig.setFromTriplets(tripletListM.begin(), tripletListM.end());
                Eigen::SparseMatrix<double>  JtMJeigen(nbColsJ1,nbColsJ1);
                JtMJeigen = J1eig.transpose()*Meig*J1eig;
                msg_info(this) << JtMJeigen;
                std::string massName = d_mappedMass.get()->getName() + "_reduced.txt";
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

//    startTime= (double)timer->getTime();
//    for (unsigned int i=0; i<nbColsJ1; i++)
//    {
//        for (unsigned int j=0; j<nbColsJ1; j++)
//        {
//            mat11.matrix->add(i, j, J1tKJ1eigen.coeff(i,j));
//        }
//    }
//    msg_info(this)<<" time copy J1tKJ1eigen back to J1tKJ1 in CompressedRowSparse : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";

    startTime= (double)timer->getTime();
    for (int k=0; k<J1tKJ1eigen.outerSize(); ++k)
      for (Eigen::SparseMatrix<double>::InnerIterator it(J1tKJ1eigen,k); it; ++it)
      {
              mat11.matrix->add(it.row(), it.col(), it.value());
      }
    msg_info(this)<<" time copy J1tKJ1eigen back to J1tKJ1 in CompressedRowSparse in the clever way: "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";

    if (bms1 != bms2)
    {
        startTime= (double)timer->getTime();
        for (unsigned int i=0; i<nbColsJ2; i++)
        {
            for (unsigned int j=0; j<nbColsJ2; j++)
            {
                mat22.matrix->add(i, j, J2tKJ2eigen.coeff(i,j));
            }
        }
        msg_info(this)<<" time copy J2tKJ2eigen back to J2tKJ2 in CompressedRowSparse : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";
        startTime= (double)timer->getTime();

        for (unsigned int i=0; i<nbColsJ1; i++)
        {
            for (unsigned int j=0; j<nbColsJ2; j++)
            {
                mat12.matrix->add(i, j, J1tKJ2eigen.coeff(i,j));
            }
        }
        msg_info(this)<<" time copy J1tKJ2eigen back to J1tKJ2 in CompressedRowSparse : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";
        startTime= (double)timer->getTime();

        for (unsigned int i=0; i<nbColsJ2; i++)
        {
            for (unsigned int j=0; j<nbColsJ1; j++)
            {
                mat21.matrix->add(i, j, J2tKJ1eigen.coeff(i,j));
            }
        }
        msg_info(this)<<" time copy J2tKJ1eigen back to J2tKJ1 in CompressedRowSparse : "<<( (double)timer->getTime() - startTime)*timeScale<<" ms";

    }

    msg_info(this)<<" total time compute J() * K * J: "<<( (double)timer->getTime() - totime)*timeScale<<" ms";

    //std::cout<<"matrix11"<<(*mat11.matrix)<<std::endl;

    delete KAccessor;
    delete K;


    if(f_printLog.getValue())
        sout << "EXIT addKToMatrix\n" << sendl;


    const core::ExecParams* eparams = dynamic_cast<const core::ExecParams *>( mparams );
    core::ConstraintParams cparams = core::ConstraintParams(*eparams);

    core::objectmodel::BaseContext* context = this->getContext();
    simulation::Node* gnode = dynamic_cast<simulation::Node*>(context);
    simulation::MechanicalResetConstraintVisitor(eparams).execute(gnode);

}

template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::testBuildJacobian(const MechanicalParams* /*mparams*/)
{

    /*  TODO => ADAPT
    CompressedRowSparseMatrix< _3_3_Matrix_Type >* mappedFFMatrix = new CompressedRowSparseMatrix< _3_3_Matrix_Type > ( );

    core::behavior::BaseMechanicalState* mstate = d_mappedForceField.get()->getContext()->getMechanicalState();
    mappedFFMatrix->resizeBloc( mstate->getSize() ,  mstate->getSize());

    DefaultMultiMatrixAccessor* mappedFFMatrixAccessor;
    mappedFFMatrixAccessor = new DefaultMultiMatrixAccessor;

    mappedFFMatrixAccessor->addMechanicalState(  d_mappedForceField.get()->getContext()->getMechanicalState() );
    mappedFFMatrixAccessor->setGlobalMatrix(mappedFFMatrix);
    mappedFFMatrixAccessor->setupMatrices();

    //--Warning r set but unused : TODO clean or refactorize

    //MultiMatrixAccessor::MatrixRef r = mappedFFMatrixAccessor->getMatrix(  d_mappedForceField.get()->getContext()->getMechanicalState()  );

    //--

    d_mappedForceField.get()->addKToMatrix(mparams, mappedFFMatrixAccessor);

    // CompressedRowSparseMatrix<_3_6_Matrix_Type> J1Jr ;
    // CompressedRowSparseMatrix<_3_3_Matrix_Type> J0tK ;
    // CompressedRowSparseMatrix<_3_3_Matrix_Type> J0tKJ0 ;
    // CompressedRowSparseMatrix<_3_6_Matrix_Type> J0tKJ1Jr ;
    // CompressedRowSparseMatrix<_6_6_Matrix_Type> JrtJ1tKJ1Jr ;
    // CompressedRowSparseMatrix<_6_3_Matrix_Type> JrtJ1tK ;
    // CompressedRowSparseMatrix<_6_3_Matrix_Type> JrtJ1tKJ0 ;

    //--Warning K set but unused : TODO clean or refactorize

    //CompressedRowSparseMatrix<_3_3_Matrix_Type>* K ;
    //K = dynamic_cast<CompressedRowSparseMatrix<_3_3_Matrix_Type>*>(r.matrix);

    //--

    sofa::core::State<DataTypes1> * state = dynamic_cast<sofa::core::State<DataTypes1> *>(mstate);
    unsigned int stateSize = mstate->getSize();

    sofa::core::MultiMatrixDerivId c = sofa::core::MatrixDerivId::nonHolonomicC();

    DataMatrixDeriv1* out = c[state].write();

    MatrixDeriv1 * IdentityTestMatrix = out->beginEdit();

    for(unsigned int i = 0; i < stateSize; i++)
    {
        typename MatrixDeriv1::RowIterator o = IdentityTestMatrix->writeLine(3 * i);
        Deriv1 v(1, 0, 0);
        o.addCol(i, v);

        o = IdentityTestMatrix->writeLine(3 * i +1 );
        Deriv1 w(0, 1, 0);
        o.addCol(i, w);

        o = IdentityTestMatrix->writeLine(3 * i +2 );
         Deriv1 u(0, 0, 1);
         o.addCol(i, u);
    }

    out->endEdit();

    delete mappedFFMatrix;
    delete mappedFFMatrixAccessor;

    */
}



// Even though it does nothing, this method has to be implemented
// since it's a pure virtual in parent class
template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::addForce(const MechanicalParams* mparams,
                                                              DataVecDeriv1& f1,
                                                              DataVecDeriv2& f2,
                                                              const DataVecCoord1& x1,
                                                              const DataVecCoord2& x2,
                                                              const DataVecDeriv1& v1,
                                                              const DataVecDeriv2& v2)
{
    SOFA_UNUSED(mparams);
    SOFA_UNUSED(f1);
    SOFA_UNUSED(f2);
    SOFA_UNUSED(x1);
    SOFA_UNUSED(x2);
    SOFA_UNUSED(v1);
    SOFA_UNUSED(v2);
}

// Even though it does nothing, this method has to be implemented
// since it's a pure virtual in parent class
template<class DataTypes1, class DataTypes2>
void MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::addDForce(const MechanicalParams* mparams,
                                                               DataVecDeriv1& df1,
                                                               DataVecDeriv2& df2,
                                                               const DataVecDeriv1& dx1,
                                                               const DataVecDeriv2& dx2)
{
    SOFA_UNUSED(mparams);
    SOFA_UNUSED(df1);
    SOFA_UNUSED(df2);
    SOFA_UNUSED(dx1);
    SOFA_UNUSED(dx2);
}

// Even though it does nothing, this method has to be implemented
// since it's a pure virtual in parent class
template<class DataTypes1, class DataTypes2>
double MappedMatrixForceFieldAndMass<DataTypes1, DataTypes2>::getPotentialEnergy(const MechanicalParams* mparams,
                                                                          const DataVecCoord1& x1,
                                                                          const DataVecCoord2& x2) const
{
    SOFA_UNUSED(mparams);
    SOFA_UNUSED(x1);
    SOFA_UNUSED(x2);

    return 0.0;
}

} // namespace forcefield

} // namespace component

} // namespace sofa

#endif
