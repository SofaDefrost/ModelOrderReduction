/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, development version     *
*                (c) 2006-2017 INRIA, USTL, UJF, CNRS, MGH                    *
*                                                                             *
* This program is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This program is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this program. If not, see <http://www.gnu.org/licenses/>.        *
*******************************************************************************
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
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
#include <sofa/defaulttype/Vec3Types.h>
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


template< class DataTypes >
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronHandler::applyCreateFunction(unsigned int tetrahedronIndex,
                                                                                              TetrahedronRestInformation &tinfo,
                                                                                              const Tetrahedron &,
                                                                                              const sofa::helper::vector<unsigned int> &,
                                                                                              const sofa::helper::vector<double> &)
{

  if (ff) {
      const vector< Tetrahedron > &tetrahedronArray=ff->m_topology->getTetrahedra() ;
      const std::vector< Edge> &edgeArray=ff->m_topology->getEdges() ;
      unsigned int j;
//      int k;
      typename DataTypes::Real volume;
      typename DataTypes::Coord point[4];
      const typename DataTypes::VecCoord restPosition = ff->mstate->read(core::ConstVecCoordId::restPosition())->getValue();

      ///describe the indices of the 4 tetrahedron vertices
      const Tetrahedron &t= tetrahedronArray[tetrahedronIndex];
      BaseMeshTopology::EdgesInTetrahedron te=ff->m_topology->getEdgesInTetrahedron(tetrahedronIndex);

      // store the point position

      for(j=0;j<4;++j)
          point[j]=(restPosition)[t[j]];
      /// compute 6 times the rest volume
      volume=dot(cross(point[2]-point[0],point[3]-point[0]),point[1]-point[0]);
      /// store the rest volume
      tinfo.m_volScale =(Real)(1.0/volume);
      tinfo.m_restVolume = fabs(volume/6);
      // store shape vectors at the rest configuration
      for(j=0;j<4;++j) {
          if (!(j%2))
              tinfo.m_shapeVector[j]=-cross(point[(j+2)%4] - point[(j+1)%4],point[(j+3)%4] - point[(j+1)%4])/ volume;
          else
              tinfo.m_shapeVector[j]=cross(point[(j+2)%4] - point[(j+1)%4],point[(j+3)%4] - point[(j+1)%4])/ volume;;
      }


      for(j=0;j<6;++j) {
          Edge e=ff->m_topology->getLocalEdgesInTetrahedron(j);
          int k=e[0];
          //int l=e[1];
          if (edgeArray[te[j]][0]!=t[k]) {
              k=e[1];
              //l=e[0];
          }
      }


  }//end if(ff)

}

template <class DataTypes> HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::HyperReducedTetrahedronHyperelasticityFEMForceField()
    : m_topology(0)
    , m_initialPoints(0)
    , m_updateMatrix(true)
    , m_meshSaved( false)
    , d_stiffnessMatrixRegularizationWeight(initData(&d_stiffnessMatrixRegularizationWeight, (bool)false,"matrixRegularization","Regularization of the Stiffness Matrix (between true or false)"))
    , d_materialName(initData(&d_materialName,std::string("ArrudaBoyce"),"materialName","the name of the material to be used"))
    , d_parameterSet(initData(&d_parameterSet,"ParameterSet","The global parameters specifying the material"))
    , d_anisotropySet(initData(&d_anisotropySet,"AnisotropyDirections","The global directions of anisotropy of the material"))
    , m_tetrahedronInfo(initData(&m_tetrahedronInfo, "tetrahedronInfo", "Internal tetrahedron data"))
    , m_edgeInfo(initData(&m_edgeInfo, "edgeInfo", "Internal edge data"))
    , d_prepareECSW(initData(&d_prepareECSW,false,"prepareECSW","Save data necessary for the construction of the reduced model"))
    , d_nbModes(initData(&d_nbModes,unsigned(3),"nbModes","Number of modes when preparing the ECSW method only"))
    , d_nbTrainingSet(initData(&d_nbTrainingSet,unsigned(40),"nbTrainingSet","When preparing the ECSW, size of the training set"))
    , d_periodSaveGIE(initData(&d_periodSaveGIE,unsigned(5),"periodSaveGIE","When prepareECSW is true, the values of Gie are taken every periodSaveGIE timesteps."))
    , d_performECSW(initData(&d_performECSW,false,"performECSW","Use the reduced model with the ECSW method"))
    , d_modesPath(initData(&d_modesPath,std::string("modes.txt"),"modesPath","Path to the file containing the modes (useful only for preparing ECSW)"))
    , d_RIDPath(initData(&d_RIDPath,std::string("reducedIntegrationDomain.txt"),"RIDPath","Path to the Reduced Integration domain when performing the ECSW method"))
    , d_weightsPath(initData(&d_weightsPath,std::string("weights.txt"),"weightsPath","Path to the weights when performing the ECSW method"))
    , m_tetrahedronHandler(NULL)
{
    m_tetrahedronHandler = new TetrahedronHandler(this,&m_tetrahedronInfo);
}

template <class DataTypes> HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::~HyperReducedTetrahedronHyperelasticityFEMForceField()
{
    if(m_tetrahedronHandler) delete m_tetrahedronHandler;
}

template <class DataTypes> void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::init()
{
    if (this->f_printLog.getValue())
        msg_info() << "initializing HyperReducedTetrahedronHyperelasticityFEMForceField";

    this->Inherited::init();

    /** parse the parameter set */
    SetParameterArray paramSet=d_parameterSet.getValue();
    if (paramSet.size()>0) {
            globalParameters.parameterArray.resize(paramSet.size());
            copy(paramSet.begin(), paramSet.end(),globalParameters.parameterArray.begin());
    }
    /** parse the anisotropy Direction set */
    SetAnisotropyDirectionArray anisotropySet=d_anisotropySet.getValue();
    if (anisotropySet.size()>0) {
            globalParameters.anisotropyDirection.resize(anisotropySet.size());
            copy(anisotropySet.begin(), anisotropySet.end(),globalParameters.anisotropyDirection.begin());
    }

    m_topology = this->getContext()->getMeshTopology();


    /** parse the input material name */
    string material = d_materialName.getValue();
    if (material=="ArrudaBoyce")
    {
        fem::BoyceAndArruda<DataTypes> *BoyceAndArrudaMaterial = new fem::BoyceAndArruda<DataTypes>;
        m_myMaterial = BoyceAndArrudaMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }
    else if (material=="StVenantKirchhoff")
    {
        fem::STVenantKirchhoff<DataTypes> *STVenantKirchhoffMaterial = new fem::STVenantKirchhoff<DataTypes>;
        m_myMaterial = STVenantKirchhoffMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }
    else if (material=="NeoHookean")
    {
        fem::NeoHookean<DataTypes> *NeoHookeanMaterial = new fem::NeoHookean<DataTypes>;
        m_myMaterial = NeoHookeanMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }
    else if (material=="MooneyRivlin")
    {
        fem::MooneyRivlin<DataTypes> *MooneyRivlinMaterial = new fem::MooneyRivlin<DataTypes>;
        m_myMaterial = MooneyRivlinMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }
    else if (material=="VerondaWestman")
    {
        fem::VerondaWestman<DataTypes> *VerondaWestmanMaterial = new fem::VerondaWestman<DataTypes>;
        m_myMaterial = VerondaWestmanMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }

    else if (material=="Costa")
    {
        fem::Costa<DataTypes> *CostaMaterial = new fem::Costa<DataTypes>;
        m_myMaterial = CostaMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }
    else if (material=="Ogden")
    {
        fem::Ogden<DataTypes> *OgdenMaterial = new fem::Ogden<DataTypes>;
        m_myMaterial = OgdenMaterial;
        if (this->f_printLog.getValue())
            msg_info()<<"The model is "<<material;
    }
    else
    {
        msg_error() << "material name " << material << " is not valid (should be ArrudaBoyce, StVenantKirchhoff, MooneyRivlin, VerondaWestman, Costa or Ogden)";
    }


    if (!m_topology->getNbTetrahedra())
    {
        msg_error() << "ERROR(HyperReducedTetrahedronHyperelasticityFEMForceField): object must have a Tetrahedral Set Topology.\n";
        return;
    }

    helper::vector<typename HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronRestInformation>& tetrahedronInf = *(m_tetrahedronInfo.beginEdit());

    /// prepare to store info in the triangle array
    tetrahedronInf.resize(m_topology->getNbTetrahedra());

    helper::vector<typename HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());

    edgeInf.resize(m_topology->getNbEdges());
    m_edgeInfo.createTopologicalEngine(m_topology);

    m_edgeInfo.registerTopologicalData();

    m_edgeInfo.endEdit();

    // get restPosition
    if (m_initialPoints.size() == 0)
    {
    const VecCoord& p = this->mstate->read(core::ConstVecCoordId::restPosition())->getValue();
            m_initialPoints=p;
    }
    int i;

    /// initialize the data structure associated with each tetrahedron
    for (i=0;i<m_topology->getNbTetrahedra();++i)
    {
        m_tetrahedronHandler->applyCreateFunction(i, tetrahedronInf[i],
                                                m_topology->getTetrahedron(i),  (const vector< unsigned int > )0,
                                                (const vector< double >)0);
    }

    /// set the call back function upon creation of a tetrahedron
    m_tetrahedronInfo.createTopologicalEngine(m_topology,m_tetrahedronHandler);
    m_tetrahedronInfo.registerTopologicalData();

    m_tetrahedronInfo.endEdit();
    //testDerivatives();

    if (d_prepareECSW.getValue()){
        MatrixLoader<Eigen::MatrixXd>* matLoader = new MatrixLoader<Eigen::MatrixXd>();
        matLoader->setFileName(d_modesPath.getValue());
        matLoader->load();
        matLoader->getMatrix(m_modes);
        delete matLoader;
        m_modes.conservativeResize(Eigen::NoChange,d_nbModes.getValue());

        Gie.resize(d_nbTrainingSet.getValue()*d_nbModes.getValue());
        for (unsigned int i = 0; i < d_nbTrainingSet.getValue()*d_nbModes.getValue(); i++)
        {
            Gie[i].resize(m_topology->getNbTetrahedra());
            for (unsigned int j = 0; j < m_topology->getNbTetrahedra(); j++)
            {
                Gie[i][j] = 0;
            }
        }
    }

    if (d_performECSW.getValue())
    {

        MatrixLoader<Eigen::VectorXd>* weightsMatLoader = new MatrixLoader<Eigen::VectorXd>();
        weightsMatLoader->setFileName(d_weightsPath.getValue());
        weightsMatLoader->load();
        weightsMatLoader->getMatrix(weights);
        delete weightsMatLoader;

        MatrixLoader<Eigen::VectorXi>* RIDMatLoader = new MatrixLoader<Eigen::VectorXi>();
        RIDMatLoader->setFileName(d_RIDPath.getValue());
        RIDMatLoader->load();
        RIDMatLoader->getMatrix(reducedIntegrationDomain);
        delete RIDMatLoader;

        m_RIDsize = reducedIntegrationDomain.rows();

    }
    else
    {
        m_RIDsize = m_topology->getNbTetrahedra();  // the reduced integration contains all the elements in this case.
        reducedIntegrationDomain.resize(m_RIDsize);
        for (unsigned int i = 0; i<m_RIDsize; i++)
            reducedIntegrationDomain(i) = i;
    }
    msg_info(this) << "RID is: " << reducedIntegrationDomain ;
    msg_info(this) << "d_performECSW is: " << d_performECSW.getValue() ;
    msg_info(this) << "d_prepareECSW is: " << d_prepareECSW.getValue() ;

    reducedIntegrationDomainWithEdges.resize(m_topology->getNbEdges());
    int nbEdgesStored = 0;
    for (int iECSW = 0; iECSW<m_RIDsize; iECSW++)
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

    std::vector<double> GieUnit;
    if (d_prepareECSW.getValue())
    {
        GieUnit.resize(d_nbModes.getValue());
    }
    const bool printLog = this->f_printLog.getValue();
    if (printLog && !m_meshSaved)
    {
        saveMesh( "D:/Steph/sofa-result.stl" );
        printf( "Mesh saved.\n" );
        m_meshSaved = true;
    }
    unsigned int tetNum=0,i=0,j=0,k=0,l=0;
    unsigned int nbTetrahedra=m_topology->getNbTetrahedra();

    helper::vector<TetrahedronRestInformation>& tetrahedronInf = *(m_tetrahedronInfo.beginEdit());


    TetrahedronRestInformation *tetInfo;

    assert(this->mstate);

    Coord dp[3],x0,sv;

    if (d_performECSW.getValue())
    {
        for(int iECSW = 0 ; iECSW<m_RIDsize ;++iECSW)
        {
            i = reducedIntegrationDomain(iECSW);

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
            for(l=0;l<4;++l)
            {
                f[ta[l]]-=weights(i)*tetInfo->m_deformationGradient*(tetInfo->m_SPKTensorGeneral*tetInfo->m_shapeVector[l])*tetInfo->m_restVolume;
            }
        }

    }
    else
    {
        for(tetNum=0; tetNum<nbTetrahedra; tetNum++ )
        {
            tetInfo=&tetrahedronInf[tetNum];
            const Tetrahedron &ta= m_topology->getTetrahedron(tetNum);

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
            for(l=0;l<4;++l)
            {
                f[ta[l]]-=tetInfo->m_deformationGradient*(tetInfo->m_SPKTensorGeneral*tetInfo->m_shapeVector[l])*tetInfo->m_restVolume;
            }

            if (d_prepareECSW.getValue())
            {
                int numTest = this->getContext()->getTime()/this->getContext()->getDt();
                if (numTest%d_periodSaveGIE.getValue() == 0)       // Take a measure every periodSaveGIE timesteps
                {

                    numTest = numTest/d_periodSaveGIE.getValue();

                    for (unsigned int modNum = 0 ; modNum < d_nbModes.getValue() ; modNum++)
                    {

                        GieUnit[modNum] = 0;
                        for(l=0;l<4;++l)
                        {
                            GieUnit[modNum] += -(tetInfo->m_deformationGradient*(tetInfo->m_SPKTensorGeneral*tetInfo->m_shapeVector[l])*tetInfo->m_restVolume)*Deriv(m_modes(3*ta[l],modNum),m_modes(3*ta[l]+1,modNum),m_modes(3*ta[l]+2,modNum));
                        }

                    }
                    for (unsigned int i = 0 ; i < d_nbModes.getValue() ; i++)
                    {
                        if ( d_nbModes.getValue()*numTest < d_nbModes.getValue()*d_nbTrainingSet.getValue() )
                        {
                            Gie[d_nbModes.getValue()*numTest+i][tetNum] = GieUnit[i];
                        }
                    }
                }
            }
        }
    }
    if (d_prepareECSW.getValue())
    {
        int numTest = this->getContext()->getTime()/this->getContext()->getDt();
        if (numTest%d_periodSaveGIE.getValue() == 0)       // A new value was taken
        {
            numTest = numTest/d_periodSaveGIE.getValue();
            if (numTest < d_nbTrainingSet.getValue()){
                std::stringstream gieFileNameSS;
                gieFileNameSS << this->name << "_Gie.txt";
                std::string gieFileName = gieFileNameSS.str();
                std::ofstream myfileGie (gieFileName, std::fstream::app);
                msg_info(this) << "Storing case number " << numTest+1 << " in " << gieFileName << " ...";
                for (unsigned int k=numTest*d_nbModes.getValue(); k<(numTest+1)*d_nbModes.getValue();k++){
                    for (unsigned int l=0;l<m_topology->getNbTetrahedra();l++){
                        myfileGie << Gie[k][l] << " ";
                    }
                    myfileGie << std::endl;
                }
                myfileGie.close();
                msg_info(this) << "Storing Done";
            }
            else
            {
                msg_info(this) << d_nbTrainingSet.getValue() << "were already stored. Learning phase completed.";
            }
        }
    }
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

    helper::vector<EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());
    helper::vector<TetrahedronRestInformation>& tetrahedronInf = *(m_tetrahedronInfo.beginEdit());

    EdgeInformation *einfo;
    TetrahedronRestInformation *tetInfo;
    unsigned int nbTetrahedra=m_topology->getNbTetrahedra();
    const std::vector< Tetrahedron> &tetrahedronArray=m_topology->getTetrahedra() ;

    for(l=0; l<nbEdges; l++ )edgeInf[l].DfDx.clear();

    if (d_performECSW.getValue())
    {
        for(int iECSW = 0 ; iECSW<m_RIDsize ;++iECSW)
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

    helper::vector<EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());

    EdgeInformation *einfo;
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

template<class DataTypes>
SReal HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::getPotentialEnergy(const core::MechanicalParams*, const DataVecCoord&) const
{
    msg_error() << "ERROR("<<this->getClassName()<<"): getPotentialEnergy( const MechanicalParams*, const DataVecCoord& ) not implemented.";
    return 0.0;
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
    helper::vector<EdgeInformation>& edgeInf = *(m_edgeInfo.beginEdit());
    EdgeInformation *einfo;
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
Mat<3,3,double> HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::getPhi(int TetrahedronIndex)
{
    helper::vector<TetrahedronRestInformation>& tetrahedronInf = *(m_tetrahedronInfo.beginEdit());
	TetrahedronRestInformation *tetInfo;
	tetInfo=&tetrahedronInf[TetrahedronIndex];
    return tetInfo->m_deformationGradient;

}

template<class DataTypes>
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::testDerivatives()
{
    DataVecCoord d_pos;
    VecCoord &pos = *d_pos.beginEdit();
    pos =  this->mstate->read(core::ConstVecCoordId::position())->getValue();

    // perturbate original state:
    srand( 0 );
    for (unsigned int idx=0; idx<pos.size(); idx++) {
            for (unsigned int d=0; d<3; d++) pos[idx][d] += (Real)0.01 * ((Real)rand()/(Real)(RAND_MAX - 0.5));
    }

    DataVecDeriv d_force1;
    VecDeriv &force1 = *d_force1.beginEdit();
    force1.resize( pos.size() );

    DataVecDeriv d_deltaPos;
    VecDeriv &deltaPos = *d_deltaPos.beginEdit();
    deltaPos.resize( pos.size() );

    DataVecDeriv d_deltaForceCalculated;
    VecDeriv &deltaForceCalculated = *d_deltaForceCalculated.beginEdit();
    deltaForceCalculated.resize( pos.size() );

    DataVecDeriv d_force2;
    VecDeriv &force2 = *d_force2.beginEdit();
    force2.resize( pos.size() );

    Coord epsilon, zero;
    Real cs = (Real)0.00001;
    Real errorThresh = (Real)200.0*cs*cs;
    Real errorNorm;
    Real avgError=0.0;
    int count=0;

    helper::vector<TetrahedronRestInformation> &tetrahedronInf = *(m_tetrahedronInfo.beginEdit());

    for (unsigned int moveIdx=0; moveIdx<pos.size(); moveIdx++)
    {
        for (unsigned int i=0; i<pos.size(); i++)
        {
                deltaForceCalculated[i] = zero;
                force1[i] = zero;
                force2[i] = zero;
        }

        d_force1.setValue(force1);
        d_pos.setValue(pos);

        //this->addForce( force1, pos, force1 );
        this->addForce( core::MechanicalParams::defaultInstance() /* PARAMS FIRST */, d_force1, d_pos, d_force1 );

        // get current energy around
        Real energy1 = 0;
        BaseMeshTopology::TetrahedraAroundVertex vTetras = m_topology->getTetrahedraAroundVertex( moveIdx );
        for(unsigned int i = 0; i < vTetras.size(); ++i)
        {
            energy1 += tetrahedronInf[vTetras[i]].m_strainEnergy * tetrahedronInf[vTetras[i]].m_restVolume;
        }
        // generate random delta
        epsilon[0]= cs * ((Real)rand()/(Real)(RAND_MAX - 0.5));
        epsilon[1]= cs * ((Real)rand()/(Real)(RAND_MAX - 0.5));
        epsilon[2]= cs * ((Real)rand()/(Real)(RAND_MAX - 0.5));
        deltaPos[moveIdx] = epsilon;
        // calc derivative
        this->addDForce( core::MechanicalParams::defaultInstance() /* PARAMS FIRST */, d_deltaForceCalculated, d_deltaPos );
        deltaPos[moveIdx] = zero;
        // calc factual change
        pos[moveIdx] = pos[moveIdx] + epsilon;

        DataVecCoord d_force2;
        d_force2.setValue(force2);
        //this->addForce( force2, pos, force2 );
        this->addForce( core::MechanicalParams::defaultInstance() /* PARAMS FIRST */, d_force2, d_pos, d_force2 );

        pos[moveIdx] = pos[moveIdx] - epsilon;
        // check first derivative:
        Real energy2 = 0;
        for(unsigned int i = 0; i < vTetras.size(); ++i)
        {
                energy2 += tetrahedronInf[vTetras[i]].m_strainEnergy * tetrahedronInf[vTetras[i]].m_restVolume;
        }
        Coord forceAtMI = force1[moveIdx];
        Real deltaEnergyPredicted = -dot( forceAtMI, epsilon );
        Real deltaEnergyFactual = (energy2 - energy1);
        Real energyError = fabs( deltaEnergyPredicted - deltaEnergyFactual );
        if (energyError > 0.05*fabs(deltaEnergyFactual))
        { // allow up to 5% error
            printf("Error energy %i = %f%%\n", moveIdx, 100.0*energyError/fabs(deltaEnergyFactual) );
        }

        // check 2nd derivative for off-diagonal elements:
        BaseMeshTopology::EdgesAroundVertex vEdges = m_topology->getEdgesAroundVertex( moveIdx );
        for (unsigned int eIdx=0; eIdx<vEdges.size(); eIdx++)
        {
            BaseMeshTopology::Edge edge = m_topology->getEdge( vEdges[eIdx] );
            unsigned int testIdx = edge[0];
            if (testIdx==moveIdx) testIdx = edge[1];
            Coord deltaForceFactual = force2[testIdx] - force1[testIdx];
            Coord deltaForcePredicted = deltaForceCalculated[testIdx];
            Coord error = deltaForcePredicted - deltaForceFactual;
            errorNorm = error.norm();
            errorThresh = (Real) 0.05 * deltaForceFactual.norm(); // allow up to 5% error

            if (deltaForceFactual.norm() > 0.0)
            {
                    avgError += (Real)100.0*errorNorm/deltaForceFactual.norm();
                    count++;
            }
            if (errorNorm > errorThresh)
            {
                    printf("Error move %i test %i = %f%%\n", moveIdx, testIdx, 100.0*errorNorm/deltaForceFactual.norm() );
            }
        }
        // check 2nd derivative for diagonal elements:
        unsigned int testIdx = moveIdx;
        Coord deltaForceFactual = force2[testIdx] - force1[testIdx];
        Coord deltaForcePredicted = deltaForceCalculated[testIdx];
        Coord error = deltaForcePredicted - deltaForceFactual;
        errorNorm = error.norm();
        errorThresh = (Real)0.05 * deltaForceFactual.norm(); // allow up to 5% error
        if (errorNorm > errorThresh)
        {
                printf("Error move %i test %i = %f%%\n", moveIdx, testIdx, 100.0*errorNorm/deltaForceFactual.norm() );
        }
    }

    m_tetrahedronInfo.endEdit();
    printf( "testDerivatives passed!\n" );
    avgError /= (Real)count;
    printf( "Average error = %.2f%%\n", avgError );

    d_pos.endEdit();
    d_force1.endEdit();
    d_force2.endEdit();
    d_deltaPos.endEdit();
    d_deltaForceCalculated.endEdit();
}


template<class DataTypes>
void HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::saveMesh( const char *filename )
{
    VecCoord pos( this->mstate->read(core::ConstVecCoordId::position())->getValue());
    core::topology::BaseMeshTopology::SeqTriangles triangles = m_topology->getTriangles();
    FILE *file = fopen( filename, "wb" );

    if (!file) return;

    // write header
    char header[81];

    size_t errResult;
    errResult = fwrite( (void*)&(header[0]),1, 80, file );
    unsigned int numTriangles = triangles.size();
    errResult = fwrite( &numTriangles, 4, 1, file );
    // write poly data
    float vertex[3][3];
    float normal[3] = { 1,0,0 };
    short stlSeperator = 0;

    for (unsigned int triangleId=0; triangleId<triangles.size(); triangleId++)
    {
        if (m_topology->getTetrahedraAroundTriangle( triangleId ).size()==1)
        {
            // surface triangle, save it
            unsigned int p0 = m_topology->getTriangle( triangleId )[0];
            unsigned int p1 = m_topology->getTriangle( triangleId )[1];
            unsigned int p2 = m_topology->getTriangle( triangleId )[2];
            for (int d=0; d<3; d++)
            {
                    vertex[0][d] = (float)pos[p0][d];
                    vertex[1][d] = (float)pos[p1][d];
                    vertex[2][d] = (float)pos[p2][d];
            }
            errResult = fwrite( (void*)&(normal[0]), sizeof(float), 3, file );
            errResult = fwrite( (void*)&(vertex[0][0]), sizeof(float), 9, file );
            errResult = fwrite( (void*)&(stlSeperator), 2, 1, file );
        }
    }
    errResult -= errResult; // ugly trick to avoid warnings

	fclose( file );
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
    for(int iECSW = 0 ; iECSW<m_RIDsize ;++iECSW)
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
