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

#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_INL
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_INL

#include <sofa/helper/system/gl.h>
#include <SofaMiscFem/BoyceAndArruda.h>
#include <SofaMiscFem/NeoHookean.h>
#include <SofaMiscFem/MooneyRivlin.h>
#include <SofaMiscFem/VerondaWestman.h>
#include <SofaMiscFem/STVenantKirchhoff.h>
#include <SofaMiscFem/HyperelasticMaterial.h>
#include <SofaMiscFem/Costa.h>
#include <SofaMiscFem/Ogden.h>
#include "HyperReducedTetrahedronHyperelasticityFEMForceField.h"
#include <sofa/core/visual/VisualParams.h>
#include <sofa/defaulttype/VecTypes.h>
#include <SofaBaseMechanics/MechanicalObject.h>
#include <sofa/core/ObjectFactory.h>
#include <fstream> // for reading the file
#include <iostream> //for debugging
#include <sofa/helper/gl/template.h>
#include <sofa/core/behavior/ForceField.inl>
#include <SofaBaseTopology/TopologyData.inl>
#include <algorithm>
#include <iterator>

#include <sofa/helper/system/thread/CTime.h>
#include "../loader/MatrixLoader.h"


namespace sofa
{
namespace component
{
namespace forcefield
{
using namespace sofa::defaulttype;
using namespace	sofa::component::topology;
using namespace core::topology;
using sofa::component::loader::MatrixLoader;


template <class DataTypes> HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::HyperReducedTetrahedronHyperelasticityFEMForceField()
{
}

template <class DataTypes> HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::~HyperReducedTetrahedronHyperelasticityFEMForceField()
{
}

template <class DataTypes> void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::init()
{
    TetrahedronHyperelasticityFEMForceField<DataTypes>::init();
    this->initMOR(m_topology->getNbTetrahedra(),notMuted());
    msg_info(this) << "RID is: " << reducedIntegrationDomain ;
    msg_info(this) << "d_performECSW is: " << d_performECSW.getValue() ;
    msg_info(this) << "d_prepareECSW is: " << d_prepareECSW.getValue() ;

    reducedIntegrationDomainWithEdges.resize(m_topology->getNbEdges());
    int nbEdgesStored = 0;
    unsigned int i;
    for (unsigned int iECSW = 0; iECSW<m_RIDsize; iECSW++)
    {
        i = reducedIntegrationDomain(iECSW);
        BaseMeshTopology::EdgesInTetrahedron te=m_topology->getEdgesInTetrahedron(i);
        msg_info(this) << "Tet num: " << i << " edges :" << te;
        bool alreadyIn0 = false;
        bool alreadyIn1 = false;
        bool alreadyIn2 = false;
        bool alreadyIn3 = false;
        bool alreadyIn4 = false;
        bool alreadyIn5 = false;

        for (int j=0; j<nbEdgesStored;j++)
            if (te[0] == reducedIntegrationDomainWithEdges(j)){
                alreadyIn0 = true;
                break;
            }
        for (int j=0; j<nbEdgesStored;j++)
            if (te[1] == reducedIntegrationDomainWithEdges(j)){
                alreadyIn1 = true;
                break;
            }
        for (int j=0; j<nbEdgesStored;j++)
            if (te[2] == reducedIntegrationDomainWithEdges(j)){
                alreadyIn2 = true;
                break;
            }
        for (int j=0; j<nbEdgesStored;j++)
            if (te[3] == reducedIntegrationDomainWithEdges(j)){
                alreadyIn3 = true;
                break;
            }
        for (int j=0; j<nbEdgesStored;j++)
            if (te[4] == reducedIntegrationDomainWithEdges(j)){
                alreadyIn4 = true;
                break;
            }
        for (int j=0; j<nbEdgesStored;j++)
            if (te[5] == reducedIntegrationDomainWithEdges(j)){
                alreadyIn5 = true;
                break;
            }
        if (!alreadyIn0)
        {
            reducedIntegrationDomainWithEdges(nbEdgesStored) = te[0];
            nbEdgesStored = nbEdgesStored+1;

        }
        else
        {
            msg_info(this) << te[0] << "already in !!!!!! ";
        }
        if (!alreadyIn1)
        {
            reducedIntegrationDomainWithEdges(nbEdgesStored) = te[1];
            nbEdgesStored = nbEdgesStored+1;

        }
        else
        {
            msg_info(this) << te[1] << "already in !!!!!! ";
        }
        if (!alreadyIn2)
        {
            reducedIntegrationDomainWithEdges(nbEdgesStored) = te[2];
            nbEdgesStored = nbEdgesStored+1;

        }
        else
        {
            msg_info(this) << te[2] << "already in !!!!!! ";
        }
        if (!alreadyIn3)
        {
            reducedIntegrationDomainWithEdges(nbEdgesStored) = te[3];
            nbEdgesStored = nbEdgesStored+1;

        }
        else
        {
            msg_info(this) << te[3] << "already in !!!!!! ";
        }
        if (!alreadyIn4)
        {
            reducedIntegrationDomainWithEdges(nbEdgesStored) = te[4];
            nbEdgesStored = nbEdgesStored+1;

        }
        else
        {
            msg_info(this) << te[4] << "already in !!!!!! ";
        }
        if (!alreadyIn5)
        {
            reducedIntegrationDomainWithEdges(nbEdgesStored) = te[5];
            nbEdgesStored = nbEdgesStored+1;

        }
        else
        {
            msg_info(this) << te[5] << "already in !!!!!! ";
        }


    }
    reducedIntegrationDomainWithEdges.conservativeResize(nbEdgesStored);
    msg_info(this) << "reducedIntegrationDomainWithEdges: " << reducedIntegrationDomainWithEdges;

    m_RIDedgeSize = nbEdgesStored;

}

template <class DataTypes> 
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::addForce(const core::MechanicalParams* /* mparams */ /* PARAMS FIRST */, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& /* d_v */)
{
    VecDeriv& f = *d_f.beginEdit();
    const VecCoord& x = d_x.getValue();

    const bool printLog = this->f_printLog.getValue();
    if (printLog && !m_meshSaved)
    {
        this->saveMesh( "D:/Steph/sofa-result.stl" );
        printf( "Mesh saved.\n" );
        m_meshSaved = true;
    }
    unsigned int i=0,j=0,k=0,l=0;
    unsigned int nbTetrahedra=m_topology->getNbTetrahedra();

    helper::vector<typename TetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronRestInformation>& tetrahedronInf = *(m_tetrahedronInfo.beginEdit());


    typename TetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronRestInformation *tetInfo;

    assert(this->mstate);

    Coord dp[3],x0,sv;

    unsigned int nbElementsConsidered;
    if (!d_performECSW.getValue()){
        nbElementsConsidered = nbTetrahedra;
    }
    else
    {
        nbElementsConsidered = m_RIDsize;
    }
    for( unsigned int tetNum = 0 ; tetNum<nbElementsConsidered ;++tetNum)
    {

        if (!d_performECSW.getValue()){
            i = tetNum;
        }
        else
        {
            i = reducedIntegrationDomain(tetNum);
        }

        tetInfo=&tetrahedronInf[i];
        const Tetrahedron &ta= m_topology->getTetrahedron(i);

        x0=x[ta[0]];

        // compute the deformation gradient
        // deformation gradient = sum of tensor product between vertex position and shape vector
        // optimize by using displacement with first vertex
        dp[0]=x[ta[1]]-x0;
        sv=tetInfo->m_shapeVector[1];
        for (k=0;k<3;++k) {
            for (l=0;l<3;++l) {
                tetInfo->m_deformationGradient[k][l]=dp[0][k]*sv[l];
            }
        }
        for (j=1;j<3;++j) {
            dp[j]=x[ta[j+1]]-x0;
            sv=tetInfo->m_shapeVector[j+1];
            for (k=0;k<3;++k) {
                for (l=0;l<3;++l) {
                    tetInfo->m_deformationGradient[k][l]+=dp[j][k]*sv[l];
                }
            }
        }
        /// compute the right Cauchy-Green deformation matrix
        for (k=0;k<3;++k) {
            for (l=k;l<3;++l) {
                tetInfo->deformationTensor(k,l)=(tetInfo->m_deformationGradient(0,k)*tetInfo->m_deformationGradient(0,l)+
                                                 tetInfo->m_deformationGradient(1,k)*tetInfo->m_deformationGradient(1,l)+
                                                 tetInfo->m_deformationGradient(2,k)*tetInfo->m_deformationGradient(2,l));
            }
        }
        if(globalParameters.anisotropyDirection.size()>0)
        {
            tetInfo->m_fiberDirection=globalParameters.anisotropyDirection[0];
            Coord vectCa=tetInfo->deformationTensor*tetInfo->m_fiberDirection;
            Real aDotCDota=dot(tetInfo->m_fiberDirection,vectCa);
            tetInfo->lambda=(Real)sqrt(aDotCDota);
        }
        Coord areaVec = cross( dp[1], dp[2] );
        tetInfo->J = dot( areaVec, dp[0] ) * tetInfo->m_volScale;
        tetInfo->trC = (Real)( tetInfo->deformationTensor(0,0) + tetInfo->deformationTensor(1,1) + tetInfo->deformationTensor(2,2));
        tetInfo->m_SPKTensorGeneral.clear();
        m_myMaterial->deriveSPKTensor(tetInfo,globalParameters,tetInfo->m_SPKTensorGeneral);
        std::vector<Deriv> contrib;
        std::vector<unsigned int> indexList;
        contrib.resize(4);
        indexList.resize(4);
        for(l=0;l<4;++l)
        {
            contrib[l] =  -tetInfo->m_deformationGradient*(tetInfo->m_SPKTensorGeneral*tetInfo->m_shapeVector[l])*tetInfo->m_restVolume;
            indexList[l] = ta[l];
            if (!d_performECSW.getValue())
                f[ta[l]] += contrib[l];
            else
                f[ta[l]] += weights(i)*contrib[l];
        }
        this->template updateGie<DataTypes>(indexList, contrib, i);

    }


    this->saveGieFile(m_topology->getNbTetrahedra());
    /// indicates that the next call to addDForce will need to update the stiffness matrix
    m_updateMatrix=true;
    m_tetrahedronInfo.endEdit();

    d_f.endEdit();
}

template <class DataTypes>
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::updateTangentMatrix()
{
    unsigned int i=0,j=0,k=0,l=0;
    unsigned int nbEdges=m_topology->getNbEdges();
    const vector< Edge> &edgeArray=m_topology->getEdges() ;

    helper::vector<typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());
    helper::vector<typename TetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronRestInformation>& tetrahedronInf = *(m_tetrahedronInfo.beginEdit());

    typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation *einfo;
    typename TetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronRestInformation *tetInfo;
    unsigned int nbTetrahedra=m_topology->getNbTetrahedra();
    const std::vector< Tetrahedron> &tetrahedronArray=m_topology->getTetrahedra() ;

    for(l=0; l<nbEdges; l++ )edgeInf[l].DfDx.clear();

    if (d_performECSW.getValue())
    {
        for(unsigned int iECSW = 0 ; iECSW<m_RIDsize ;++iECSW)
        {
            i = reducedIntegrationDomain(iECSW);

            tetInfo=&tetrahedronInf[i];
            Matrix3 &df=tetInfo->m_deformationGradient;
            //			Matrix3 Tdf=df.transposed();
            BaseMeshTopology::EdgesInTetrahedron te=m_topology->getEdgesInTetrahedron(i);

            /// describe the jth vertex index of triangle no i
            const Tetrahedron &ta= tetrahedronArray[i];
            for(j=0;j<6;j++) {
                einfo= &edgeInf[te[j]];
                Edge e=m_topology->getLocalEdgesInTetrahedron(j);

                k=e[0];
                l=e[1];
                if (edgeArray[te[j]][0]!=ta[k]) {
                    k=e[1];
                    l=e[0];
                }
                Matrix3 &edgeDfDx = einfo->DfDx;


                Coord svl=tetInfo->m_shapeVector[l];
                Coord svk=tetInfo->m_shapeVector[k];

                Matrix3  M, N;
                MatrixSym outputTensor;
                N.clear();
                vector<MatrixSym> inputTensor;
                inputTensor.resize(3);
                //	MatrixSym input1,input2,input3,outputTensor;
                for(int m=0; m<3;m++){
                    for (int n=m;n<3;n++){
                        inputTensor[0](m,n)=svl[m]*df[0][n]+df[0][m]*svl[n];
                        inputTensor[1](m,n)=svl[m]*df[1][n]+df[1][m]*svl[n];
                        inputTensor[2](m,n)=svl[m]*df[2][n]+df[2][m]*svl[n];
                    }
                }

                for(int m=0; m<3; m++){

                    m_myMaterial->applyElasticityTensor(tetInfo,globalParameters,inputTensor[m],outputTensor);
                    Coord vectortemp=df*(outputTensor*svk);
                    Matrix3 Nv;
                    //Nv.clear();
                    for(int u=0; u<3;u++){
                        Nv[u][m]=vectortemp[u];
                    }
                    N+=Nv.transposed();
                }


                //Now M
                Real productSD=0;

                Coord vectSD=tetInfo->m_SPKTensorGeneral*svk;
                productSD=dot(vectSD,svl);
                M[0][1]=M[0][2]=M[1][0]=M[1][2]=M[2][0]=M[2][1]=0;
                M[0][0]=M[1][1]=M[2][2]=(Real)productSD;

                edgeDfDx += weights(i)*(M+N)*tetInfo->m_restVolume;


            }// end of for j
        }//end of for i



    }
    else
    {
        for(i=0; i<nbTetrahedra; i++ )
        {
            tetInfo=&tetrahedronInf[i];
            Matrix3 &df=tetInfo->m_deformationGradient;
            //			Matrix3 Tdf=df.transposed();
            BaseMeshTopology::EdgesInTetrahedron te=m_topology->getEdgesInTetrahedron(i);

            /// describe the jth vertex index of triangle no i
            const Tetrahedron &ta= tetrahedronArray[i];
            for(j=0;j<6;j++) {
                einfo= &edgeInf[te[j]];
                Edge e=m_topology->getLocalEdgesInTetrahedron(j);

                k=e[0];
                l=e[1];
                if (edgeArray[te[j]][0]!=ta[k]) {
                    k=e[1];
                    l=e[0];
                }
                Matrix3 &edgeDfDx = einfo->DfDx;


                Coord svl=tetInfo->m_shapeVector[l];
                Coord svk=tetInfo->m_shapeVector[k];

                Matrix3  M, N;
                MatrixSym outputTensor;
                N.clear();
                vector<MatrixSym> inputTensor;
                inputTensor.resize(3);
                //	MatrixSym input1,input2,input3,outputTensor;
                for(int m=0; m<3;m++){
                    for (int n=m;n<3;n++){
                        inputTensor[0](m,n)=svl[m]*df[0][n]+df[0][m]*svl[n];
                        inputTensor[1](m,n)=svl[m]*df[1][n]+df[1][m]*svl[n];
                        inputTensor[2](m,n)=svl[m]*df[2][n]+df[2][m]*svl[n];
                    }
                }

                for(int m=0; m<3; m++){

                    m_myMaterial->applyElasticityTensor(tetInfo,globalParameters,inputTensor[m],outputTensor);
                    Coord vectortemp=df*(outputTensor*svk);
                    Matrix3 Nv;
                    //Nv.clear();
                    for(int u=0; u<3;u++){
                        Nv[u][m]=vectortemp[u];
                    }
                    N+=Nv.transposed();
                }


                //Now M
                Real productSD=0;

                Coord vectSD=tetInfo->m_SPKTensorGeneral*svk;
                productSD=dot(vectSD,svl);
                M[0][1]=M[0][2]=M[1][0]=M[1][2]=M[2][0]=M[2][1]=0;
                M[0][0]=M[1][1]=M[2][2]=(Real)productSD;

                edgeDfDx += (M+N)*tetInfo->m_restVolume;


            }// end of for j
        }//end of for i
    }
    m_updateMatrix=false;
}

template <class DataTypes> 
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::addDForce(const core::MechanicalParams* mparams /* PARAMS FIRST */, DataVecDeriv& d_df, const DataVecDeriv& d_dx)
{
    VecDeriv& df = *d_df.beginEdit();
    const VecDeriv& dx = d_dx.getValue();
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    unsigned int l=0;
    unsigned int nbEdges=m_topology->getNbEdges();
    const vector< Edge> &edgeArray=m_topology->getEdges() ;

    helper::vector<typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());

    typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation *einfo;
    sofa::helper::system::thread::CTime *timer;

    double timeScale, time ;
    timeScale = 1000.0 / (double)sofa::helper::system::thread::CTime::getTicksPerSec();

    time = (double)timer->getTime();

    /// if the  matrix needs to be updated
    if (m_updateMatrix) {
        msg_info(this) << "Updating Matrix! from addDforce";
        this->updateTangentMatrix();
    }// end of if
    msg_info(this) <<" addDforce updateMatrix : "<<( (double)timer->getTime() - time)*timeScale<<" ms";

    /// performs matrix vector computation
    unsigned int v0,v1;
    Deriv deltax;	Deriv dv0,dv1;
    time = (double)timer->getTime();
    for(l=0; l<nbEdges; l++ )
    {
        einfo=&edgeInf[l];
        v0=edgeArray[l][0];
        v1=edgeArray[l][1];

        deltax= dx[v0] - dx[v1];
        dv0 = einfo->DfDx * deltax;
        // do the transpose multiply:
        dv1[0] = (Real)(deltax[0]*einfo->DfDx[0][0] + deltax[1]*einfo->DfDx[1][0] + deltax[2]*einfo->DfDx[2][0]);
        dv1[1] = (Real)(deltax[0]*einfo->DfDx[0][1] + deltax[1]*einfo->DfDx[1][1] + deltax[2]*einfo->DfDx[2][1]);
        dv1[2] = (Real)(deltax[0]*einfo->DfDx[0][2] + deltax[1]*einfo->DfDx[1][2] + deltax[2]*einfo->DfDx[2][2]);
        // add forces
        df[v0] += dv1 * kFactor;
        df[v1] -= dv0 * kFactor;
    }
    m_edgeInfo.endEdit();
    m_tetrahedronInfo.endEdit();
    msg_info(this) <<" addDforce actualCalc : "<<( (double)timer->getTime() - time)*timeScale<<" ms";

    d_df.endEdit();
}

template <class DataTypes>
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::addKToMatrix(sofa::defaulttype::BaseMatrix *mat, SReal k, unsigned int &offset)
{

    /// if the  matrix needs to be updated
    if (m_updateMatrix)
    {
        msg_info(this) << "Updating Matrix! from addKtoMatrix";

        this->updateTangentMatrix();
    }
    sofa::helper::system::thread::CTime *timer;

    double timeScale, time ;
    timeScale = 1000.0 / (double)sofa::helper::system::thread::CTime::getTicksPerSec();

    time = (double)timer->getTime();

    unsigned int nbEdges=m_topology->getNbEdges();
    const vector< Edge> &edgeArray=m_topology->getEdges() ;
    helper::vector<typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());
    typename TetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation *einfo;
    unsigned int i,j,N0, N1, l, lECSW;
    Index noeud0, noeud1;

    if (d_performECSW.getValue())
    {
        for(lECSW=0; lECSW<m_RIDedgeSize; lECSW++ )
        {
            l = reducedIntegrationDomainWithEdges(lECSW);
            einfo=&edgeInf[l];
            noeud0=edgeArray[l][0];
            noeud1=edgeArray[l][1];
            N0 = offset+3*noeud0;
            N1 = offset+3*noeud1;

            for (i=0; i<3; i++)
            {
                for(j=0; j<3; j++)
                {
                    mat->add(N0+i, N0+j,  einfo->DfDx[j][i]*k);
                    mat->add(N0+i, N1+j, - einfo->DfDx[j][i]*k);
                    mat->add(N1+i, N0+j, - einfo->DfDx[i][j]*k);
                    mat->add(N1+i, N1+j, + einfo->DfDx[i][j]*k);
                }
            }
        }
    }
    else
    {
        for(l=0; l<nbEdges; l++ )
        {
            einfo=&edgeInf[l];
            noeud0=edgeArray[l][0];
            noeud1=edgeArray[l][1];
            N0 = offset+3*noeud0;
            N1 = offset+3*noeud1;

            for (i=0; i<3; i++)
            {
                for(j=0; j<3; j++)
                {
                    mat->add(N0+i, N0+j,  einfo->DfDx[j][i]*k);
                    mat->add(N0+i, N1+j, - einfo->DfDx[j][i]*k);
                    mat->add(N1+i, N0+j, - einfo->DfDx[i][j]*k);
                    mat->add(N1+i, N1+j, + einfo->DfDx[i][j]*k);
                }
            }
        }
    }

    msg_info(this) <<" addKtoMatrix : "<<( (double)timer->getTime() - time)*timeScale<<" ms";

    m_edgeInfo.endEdit();
}



template<class DataTypes>
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::draw(const core::visual::VisualParams* vparams)
{
    //	unsigned int i;
    if (!vparams->displayFlags().getShowForceFields()) return;
    if (!this->mstate) return;

    const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();

    if (vparams->displayFlags().getShowWireFrame())
          vparams->drawTool()->setPolygonMode(0,true);


    std::vector< Vector3 > points[4];
    int i;
    for(unsigned int iECSW = 0 ; iECSW<m_RIDsize ;++iECSW)
    {
        i = reducedIntegrationDomain(iECSW);

//    for(int i = 0 ; i<m_topology->getNbTetrahedra();++i)
//    {
        const Tetrahedron t=m_topology->getTetrahedron(i);

        Index a = t[0];
        Index b = t[1];
        Index c = t[2];
        Index d = t[3];
        Coord center = (x[a]+x[b]+x[c]+x[d])*0.125;
        Coord pa = (x[a]+center)*(Real)0.666667;
        Coord pb = (x[b]+center)*(Real)0.666667;
        Coord pc = (x[c]+center)*(Real)0.666667;
        Coord pd = (x[d]+center)*(Real)0.666667;

        points[0].push_back(pa);
        points[0].push_back(pb);
        points[0].push_back(pc);

        points[1].push_back(pb);
        points[1].push_back(pc);
        points[1].push_back(pd);

        points[2].push_back(pc);
        points[2].push_back(pd);
        points[2].push_back(pa);

        points[3].push_back(pd);
        points[3].push_back(pa);
        points[3].push_back(pb);
    }

    Vec<4,float> color1;
    Vec<4,float> color2;
    Vec<4,float> color3;
    Vec<4,float> color4;

    std::string material = d_materialName.getValue();
    if (material=="ArrudaBoyce") {
        color1 = Vec<4,float>(0.0,1.0,0.0,1.0);
        color2 = Vec<4,float>(0.5,1.0,0.0,1.0);
        color3 = Vec<4,float>(1.0,1.0,0.0,1.0);
        color4 = Vec<4,float>(1.0,1.0,0.5,1.0);
    }
    else if (material=="StVenantKirchhoff"){
        color1 = Vec<4,float>(1.0,0.0,0.0,1.0);
        color2 = Vec<4,float>(1.0,0.0,0.5,1.0);
        color3 = Vec<4,float>(1.0,1.0,0.0,1.0);
        color4 = Vec<4,float>(1.0,0.5,1.0,1.0);
    }
    else if (material=="NeoHookean"){
        color1 = Vec<4,float>(0.0,1.0,1.0,1.0);
        color2 = Vec<4,float>(0.5,0.0,1.0,1.0);
        color3 = Vec<4,float>(1.0,0.0,1.0,1.0);
        color4 = Vec<4,float>(1.0,0.5,1.0,1.0);
    }
    else if (material=="MooneyRivlin"){
        color1 = Vec<4,float>(0.0,1.0,0.0,1.0);
        color2 = Vec<4,float>(0.0,1.0,0.5,1.0);
        color3 = Vec<4,float>(0.0,1.0,1.0,1.0);
        color4 = Vec<4,float>(0.5,1.0,1.0,1.0);
    }
    else if (material=="VerondaWestman"){
        color1 = Vec<4,float>(0.0,1.0,0.0,1.0);
        color2 = Vec<4,float>(0.5,1.0,0.0,1.0);
        color3 = Vec<4,float>(1.0,1.0,0.0,1.0);
        color4 = Vec<4,float>(1.0,1.0,0.5,1.0);
    }
    else if (material=="Costa"){
        color1 = Vec<4,float>(0.0,1.0,0.0,1.0);
        color2 = Vec<4,float>(0.5,1.0,0.0,1.0);
        color3 = Vec<4,float>(1.0,1.0,0.0,1.0);
        color4 = Vec<4,float>(1.0,1.0,0.5,1.0);
    }
    else if (material=="Ogden"){
        color1 = Vec<4,float>(0.0,1.0,0.0,1.0);
        color2 = Vec<4,float>(0.5,1.0,0.0,1.0);
        color3 = Vec<4,float>(1.0,1.0,0.0,1.0);
        color4 = Vec<4,float>(1.0,1.0,0.5,1.0);
    }
    else {
        color1 = Vec<4,float>(0.0,1.0,0.0,1.0);
        color2 = Vec<4,float>(0.5,1.0,0.0,1.0);
        color3 = Vec<4,float>(1.0,1.0,0.0,1.0);
        color4 = Vec<4,float>(1.0,1.0,0.5,1.0);
    }


    vparams->drawTool()->drawTriangles(points[0], color1);
    vparams->drawTool()->drawTriangles(points[1], color2);
    vparams->drawTool()->drawTriangles(points[2], color3);
    vparams->drawTool()->drawTriangles(points[3], color4);

    if (vparams->displayFlags().getShowWireFrame())
          vparams->drawTool()->setPolygonMode(0,false);

}

} // namespace forcefield

} // namespace component

} // namespace sofa

#endif // SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_INL
