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
#pragma once

#include "sofa/core/behavior/BaseLocalForceFieldMatrix.h"
#include <ModelOrderReduction/component/forcefield/HyperReducedTetrahedronFEMForceField.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/component/topology/container/grid/GridTopology.h>
#include <sofa/simulation/Simulation.h>
#include <sofa/core/behavior/MultiMatrixAccessor.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/helper/decompose.h>
#include <sofa/gl/template.h>
#include <cassert>
#include <fstream> // for reading the file
#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <set>
#include <sofa/linearalgebra/CompressedRowSparseMatrix.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/helper/AdvancedTimer.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <ModelOrderReduction/component/loader/MatrixLoader.h>

// verify timing
#include <sofa/helper/ScopedAdvancedTimer.h>
#include <sofa/helper/system/thread/CTime.h>


namespace sofa::component::forcefield
{

using sofa::component::loader::MatrixLoader;
using sofa::core::objectmodel::ComponentState ;



//////////////////////////////////////////////////////////////////////
////////////////////  small displacements method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForceSmall( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex )
{
    TetrahedronFEMForceField<DataTypes>::accumulateForceSmall( f,  p, elementIt, elementIndex );
}


template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::applyStiffnessSmall( Vector& f, const Vector& x, int i, Index a, Index b, Index c, Index d, SReal fact )
{
    TetrahedronFEMForceField<DataTypes>::applyStiffnessSmall(  f,  x,  i,  a,  b,  c,  d,  fact );
}

//////////////////////////////////////////////////////////////////////
////////////////////  large displacements method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForceLarge( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex )
{
    Element index = *elementIt;

    // Rotation matrix (deformed and displaced Tetrahedron/world)
    Transformation R_0_2;
    this->computeRotationLarge( R_0_2, p, index[0],index[1],index[2]);

    rotations[elementIndex].transpose(R_0_2);

    // positions of the deformed and displaced Tetrahedron in its frame
    type::fixed_array<Coord,4> deforme;
    for(int i=0; i<4; ++i)
        deforme[i] = R_0_2*p[index[i]];

    deforme[1][0] -= deforme[0][0];
    deforme[2][0] -= deforme[0][0];
    deforme[2][1] -= deforme[0][1];
    deforme[3] -= deforme[0];

    // displacement
    Displacement D;
    D[0] = 0;
    D[1] = 0;
    D[2] = 0;
    D[3] = _rotatedInitialElements[elementIndex][1][0] - deforme[1][0];
    D[4] = 0;
    D[5] = 0;
    D[6] = _rotatedInitialElements[elementIndex][2][0] - deforme[2][0];
    D[7] = _rotatedInitialElements[elementIndex][2][1] - deforme[2][1];
    D[8] = 0;
    D[9] = _rotatedInitialElements[elementIndex][3][0] - deforme[3][0];
    D[10] = _rotatedInitialElements[elementIndex][3][1] - deforme[3][1];
    D[11] =_rotatedInitialElements[elementIndex][3][2] - deforme[3][2];

    Displacement F;
    if(_updateStiffnessMatrix.getValue())
    {
        strainDisplacements[elementIndex][0][0]   = ( - deforme[2][1]*deforme[3][2] );
        strainDisplacements[elementIndex][1][1] = ( deforme[2][0]*deforme[3][2] - deforme[1][0]*deforme[3][2] );
        strainDisplacements[elementIndex][2][2]   = ( deforme[2][1]*deforme[3][0] - deforme[2][0]*deforme[3][1] + deforme[1][0]*deforme[3][1] - deforme[1][0]*deforme[2][1] );

        strainDisplacements[elementIndex][3][0]   = ( deforme[2][1]*deforme[3][2] );
        strainDisplacements[elementIndex][4][1]  = ( - deforme[2][0]*deforme[3][2] );
        strainDisplacements[elementIndex][5][2]   = ( - deforme[2][1]*deforme[3][0] + deforme[2][0]*deforme[3][1] );

        strainDisplacements[elementIndex][7][1]  = ( deforme[1][0]*deforme[3][2] );
        strainDisplacements[elementIndex][8][2]   = ( - deforme[1][0]*deforme[3][1] );

        strainDisplacements[elementIndex][11][2] = ( deforme[1][0]*deforme[2][1] );
    }

    if(!_assembling.getValue())
    {
        // compute force on element
        this->computeForce( F, D, _plasticStrains[elementIndex], materialsStiffnesses[elementIndex], strainDisplacements[elementIndex] );
        std::vector<Deriv> contrib;
        std::vector<unsigned int> indexList;
        contrib.resize(4);
        indexList.resize(4);
        for(int i=0; i<12; i+=3){
            contrib[i/3] = rotations[elementIndex] * Deriv( F[i], F[i+1],  F[i+2] );
            indexList[i/3] = index[i/3];
            if (!d_performECSW.getValue())
                f[indexList[i/3]] +=  contrib[i/3];
            else
                f[indexList[i/3]] +=  weights(elementIndex)*contrib[i/3];
        }
        this->template updateGie<DataTypes>(indexList, contrib, elementIndex);
    }
    else if( _plasticMaxThreshold.getValue() <= 0 )
    {
        strainDisplacements[elementIndex][6][0] = 0;
        strainDisplacements[elementIndex][9][0] = 0;
        strainDisplacements[elementIndex][10][1] = 0;

        StiffnessMatrix RJKJt, RJKJtRt;
        this->computeStiffnessMatrix(RJKJt,RJKJtRt,materialsStiffnesses[elementIndex], strainDisplacements[elementIndex],rotations[elementIndex]);


        //erase the stiffness matrix at each time step
        if(elementIndex==0)
        {
            for(unsigned int i=0; i<_stiffnesses.size(); ++i)
            {
                _stiffnesses[i].resize(0);
            }
        }

        for(int i=0; i<12; ++i)
        {
            index_type row = index[i/3]*3+i%3;
            for(int j=0; j<12; ++j)
            {
                index_type col = index[j/3]*3+j%3;

                // search if the vertex is already take into account by another element
                typename CompressedValue::iterator result = _stiffnesses[row].end();
                for(typename CompressedValue::iterator it=_stiffnesses[row].begin(); it!=_stiffnesses[row].end()&&result==_stiffnesses[row].end(); ++it)
                {
                    if( (*it).first == col )
                    {
                        result = it;
                    }
                }

                if( result==_stiffnesses[row].end() )
                {
                    _stiffnesses[row].push_back( Col_Value(col,RJKJtRt[i][j] )  );
                }
                else
                {
                    (*result).second += RJKJtRt[i][j];
                }
            }
        }
        F = RJKJt*D;

        for(int i=0; i<12; i+=3)
            f[index[i/3]] += Deriv( F[i], F[i+1],  F[i+2] );
    }
    else
    {
        msg_warning(this) << "TODO(HyperReducedTetrahedronFEMForceField): support for assembling system matrix when using plasticity.";
    }
}

//////////////////////////////////////////////////////////////////////
////////////////////  polar decomposition method  ////////////////////
//////////////////////////////////////////////////////////////////////


template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForcePolar( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex )
{
    TetrahedronFEMForceField<DataTypes>::accumulateForcePolar(  f,  p,   elementIt,  elementIndex );
}



//////////////////////////////////////////////////////////////////////
////////////////////  svd decomposition method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForceSVD( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex )
{
   TetrahedronFEMForceField<DataTypes>::accumulateForceSVD(  f,  p,  elementIt,  elementIndex );
}



///////////////////////////////////////////////////////////////////////////////////////
////////////////  specific methods for corotational large, polar, svd  ////////////////
///////////////////////////////////////////////////////////////////////////////////////

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::applyStiffnessCorotational( Vector& f, const Vector& x, int i, Index a, Index b, Index c, Index d, SReal fact )
{
    Displacement X;

    // rotate by rotations[i] transposed
    X[0]  = rotations[i][0][0] * x[a][0] + rotations[i][1][0] * x[a][1] + rotations[i][2][0] * x[a][2];
    X[1]  = rotations[i][0][1] * x[a][0] + rotations[i][1][1] * x[a][1] + rotations[i][2][1] * x[a][2];
    X[2]  = rotations[i][0][2] * x[a][0] + rotations[i][1][2] * x[a][1] + rotations[i][2][2] * x[a][2];

    X[3]  = rotations[i][0][0] * x[b][0] + rotations[i][1][0] * x[b][1] + rotations[i][2][0] * x[b][2];
    X[4]  = rotations[i][0][1] * x[b][0] + rotations[i][1][1] * x[b][1] + rotations[i][2][1] * x[b][2];
    X[5]  = rotations[i][0][2] * x[b][0] + rotations[i][1][2] * x[b][1] + rotations[i][2][2] * x[b][2];

    X[6]  = rotations[i][0][0] * x[c][0] + rotations[i][1][0] * x[c][1] + rotations[i][2][0] * x[c][2];
    X[7]  = rotations[i][0][1] * x[c][0] + rotations[i][1][1] * x[c][1] + rotations[i][2][1] * x[c][2];
    X[8]  = rotations[i][0][2] * x[c][0] + rotations[i][1][2] * x[c][1] + rotations[i][2][2] * x[c][2];

    X[9]  = rotations[i][0][0] * x[d][0] + rotations[i][1][0] * x[d][1] + rotations[i][2][0] * x[d][2];
    X[10] = rotations[i][0][1] * x[d][0] + rotations[i][1][1] * x[d][1] + rotations[i][2][1] * x[d][2];
    X[11] = rotations[i][0][2] * x[d][0] + rotations[i][1][2] * x[d][1] + rotations[i][2][2] * x[d][2];

    Displacement F;

    this->computeForce( F, X, materialsStiffnesses[i], strainDisplacements[i], fact );

    if (d_performECSW.getValue()){
        // rotate by rotations[i]
        f[a][0] -=  weights(i)*(rotations[i][0][0] *  F[0] +  rotations[i][0][1] * F[1]  + rotations[i][0][2] * F[2]);
        f[a][1] -=  weights(i)*(rotations[i][1][0] *  F[0] +  rotations[i][1][1] * F[1]  + rotations[i][1][2] * F[2]);
        f[a][2] -=  weights(i)*(rotations[i][2][0] *  F[0] +  rotations[i][2][1] * F[1]  + rotations[i][2][2] * F[2]);

        f[b][0] -=  weights(i)*(rotations[i][0][0] *  F[3] +  rotations[i][0][1] * F[4]  + rotations[i][0][2] * F[5]);
        f[b][1] -=  weights(i)*(rotations[i][1][0] *  F[3] +  rotations[i][1][1] * F[4]  + rotations[i][1][2] * F[5]);
        f[b][2] -=  weights(i)*(rotations[i][2][0] *  F[3] +  rotations[i][2][1] * F[4]  + rotations[i][2][2] * F[5]);

        f[c][0] -=  weights(i)*(rotations[i][0][0] *  F[6] +  rotations[i][0][1] * F[7]  + rotations[i][0][2] * F[8]);
        f[c][1] -=  weights(i)*(rotations[i][1][0] *  F[6] +  rotations[i][1][1] * F[7]  + rotations[i][1][2] * F[8]);
        f[c][2] -=  weights(i)*(rotations[i][2][0] *  F[6] +  rotations[i][2][1] * F[7]  + rotations[i][2][2] * F[8]);

        f[d][0] -=  weights(i)*(rotations[i][0][0] *  F[9] +  rotations[i][0][1] * F[10] + rotations[i][0][2] * F[11]);
        f[d][1]	-=  weights(i)*(rotations[i][1][0] *  F[9] +  rotations[i][1][1] * F[10] + rotations[i][1][2] * F[11]);
        f[d][2]	-=  weights(i)*(rotations[i][2][0] *  F[9] +  rotations[i][2][1] * F[10] + rotations[i][2][2] * F[11]);
    }
    else
    {
        // rotate by rotations[i]
        f[a][0] -= rotations[i][0][0] *  F[0] +  rotations[i][0][1] * F[1]  + rotations[i][0][2] * F[2];
        f[a][1] -= rotations[i][1][0] *  F[0] +  rotations[i][1][1] * F[1]  + rotations[i][1][2] * F[2];
        f[a][2] -= rotations[i][2][0] *  F[0] +  rotations[i][2][1] * F[1]  + rotations[i][2][2] * F[2];

        f[b][0] -= rotations[i][0][0] *  F[3] +  rotations[i][0][1] * F[4]  + rotations[i][0][2] * F[5];
        f[b][1] -= rotations[i][1][0] *  F[3] +  rotations[i][1][1] * F[4]  + rotations[i][1][2] * F[5];
        f[b][2] -= rotations[i][2][0] *  F[3] +  rotations[i][2][1] * F[4]  + rotations[i][2][2] * F[5];

        f[c][0] -= rotations[i][0][0] *  F[6] +  rotations[i][0][1] * F[7]  + rotations[i][0][2] * F[8];
        f[c][1] -= rotations[i][1][0] *  F[6] +  rotations[i][1][1] * F[7]  + rotations[i][1][2] * F[8];
        f[c][2] -= rotations[i][2][0] *  F[6] +  rotations[i][2][1] * F[7]  + rotations[i][2][2] * F[8];

        f[d][0] -= rotations[i][0][0] *  F[9] +  rotations[i][0][1] * F[10] + rotations[i][0][2] * F[11];
        f[d][1]	-= rotations[i][1][0] *  F[9] +  rotations[i][1][1] * F[10] + rotations[i][1][2] * F[11];
        f[d][2]	-= rotations[i][2][0] *  F[9] +  rotations[i][2][1] * F[10] + rotations[i][2][2] * F[11];
    }

}


//////////////////////////////////////////////////////////////////////
////////////////  generic main computations methods  /////////////////
//////////////////////////////////////////////////////////////////////

template <class DataTypes>
void HyperReducedTetrahedronFEMForceField<DataTypes>::init()
{
    TetrahedronFEMForceField<DataTypes>::init();
    this->initMOR(_indexedElements->size(),notMuted());
}



template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::addForce (const core::MechanicalParams* /*mparams*/, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& /* d_v */)
{
    VecDeriv& f = *d_f.beginEdit();
    const VecCoord& p = d_x.getValue();

    SCOPED_TIMER("MORTetra::addForce");
    f.resize(p.size());

    if (needUpdateTopology)
    {
        reinit();
        needUpdateTopology = false;
    }

    unsigned int i;
    typename VecElement::const_iterator it, it0;
    switch(method)
    {
    case SMALL :
    {
        for(it=_indexedElements->begin(), i = 0 ; it!=_indexedElements->end(); ++it,++i)
        {
            accumulateForceSmall( f, p, it, i );
        }
        break;
    }
    case LARGE :
    {
        if (d_performECSW.getValue()){
            it0=_indexedElements->begin();
            for( i = 0 ; i<m_RIDsize ;++i)
            {
                it = it0 + reducedIntegrationDomain(i);
                accumulateForceLarge( f, p, it, reducedIntegrationDomain(i) );
            }
        }
        else
        {
            for(it=_indexedElements->begin(), i = 0 ; it!=_indexedElements->end(); ++it,++i)
            {
                accumulateForceLarge( f, p, it, i );
            }
        }
        break;
    }
    case POLAR :
    {
        for(it=_indexedElements->begin(), i = 0 ; it!=_indexedElements->end(); ++it,++i)
        {
            accumulateForcePolar( f, p, it, i );
        }
        break;
    }
    case SVD :
    {
        for(it=_indexedElements->begin(), i = 0 ; it!=_indexedElements->end(); ++it,++i)
        {
            accumulateForceSVD( f, p, it, i );
        }
        break;
    }
    }
    d_f.endEdit();

    updateVonMisesStress = true;
    this->saveGieFile(_indexedElements->size());
}

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::addDForce(const core::MechanicalParams* mparams, DataVecDeriv& d_df, const DataVecDeriv& d_dx)
{
    auto dfAccessor = sofa::helper::getWriteAccessor(d_df);
    VecDeriv& df = dfAccessor.wref();

    const VecDeriv& dx = d_dx.getValue();
    df.resize(dx.size());

    const Real kFactor = (Real)sofa::core::mechanicalparams::kFactorIncludingRayleighDamping(mparams, this->rayleighStiffness.getValue());

    unsigned int i;
    typename VecElement::const_iterator it,it0;
    if( method == SMALL )
    {
        for(it = _indexedElements->begin(), i = 0 ; it != _indexedElements->end() ; ++it, ++i)
        {
            Index a = (*it)[0];
            Index b = (*it)[1];
            Index c = (*it)[2];
            Index d = (*it)[3];

            applyStiffnessSmall( df,dx, i, a,b,c,d, kFactor );
        }
    }
    else
    {
        if (d_performECSW.getValue())
        {
            it0=_indexedElements->begin();
            for( i = 0 ; i<m_RIDsize ;++i)
            {
                it = it0 + reducedIntegrationDomain(i);
                Index a = (*it)[0];
                Index b = (*it)[1];
                Index c = (*it)[2];
                Index d = (*it)[3];
                applyStiffnessCorotational( df,dx, reducedIntegrationDomain(i), a,b,c,d, kFactor );
            }
        }
        else
        {
            for(it = _indexedElements->begin(), i = 0 ; it != _indexedElements->end() ; ++it, ++i)
            {
                Index a = (*it)[0];
                Index b = (*it)[1];
                Index c = (*it)[2];
                Index d = (*it)[3];

                applyStiffnessCorotational( df,dx, i, a,b,c,d, kFactor );
            }
        }
    }

    d_df.endEdit();
}

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
void HyperReducedTetrahedronFEMForceField<DataTypes>::draw(const core::visual::VisualParams* vparams)
{

        if(this->d_componentState.getValue() == ComponentState::Invalid)
            return ;

        if (!vparams->displayFlags().getShowForceFields()) return;
        if (!this->mstate) return;

        if(needUpdateTopology)
        {
            reinit();
            needUpdateTopology = false;
        }

        bool drawVonMisesStress = (_showVonMisesStressPerNode.getValue() || _showVonMisesStressPerElement.getValue()) && TetrahedronFEMForceField<DataTypes>::isComputeVonMisesStressMethodSet();

        vparams->drawTool()->saveLastState();

        if (vparams->displayFlags().getShowWireFrame())
        {
            vparams->drawTool()->setPolygonMode(0, true);
        }

        vparams->drawTool()->disableLighting();

        const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();
        const VecReal& youngModulus = _youngModulus.getValue();

        bool heterogeneous = false;
        if (drawHeterogeneousTetra.getValue() && drawVonMisesStress)
        {
            minYoung=youngModulus[0];
            maxYoung=youngModulus[0];
            for (unsigned i=0; i<youngModulus.size(); i++)
            {
                if (youngModulus[i]<minYoung) minYoung=youngModulus[i];
                if (youngModulus[i]>maxYoung) maxYoung=youngModulus[i];
            }
            heterogeneous = (fabs(minYoung-maxYoung) > 1e-8);
        }


        Real minVM = (Real)1e20, maxVM = (Real)-1e20;
        Real minVMN = (Real)1e20, maxVMN = (Real)-1e20;
        helper::ReadAccessor<Data<type::vector<Real> > > vM =  _vonMisesPerElement;
        helper::ReadAccessor<Data<type::vector<Real> > > vMN =  _vonMisesPerNode;

        // vonMises stress
        if (drawVonMisesStress)
        {
            for (size_t i = 0; i < vM.size(); i++)
            {
                minVM = (vM[i] < minVM) ? vM[i] : minVM;
                maxVM = (vM[i] > maxVM) ? vM[i] : maxVM;
            }
            if (maxVM < prevMaxStress)
            {
                maxVM = prevMaxStress;
            }
            for (size_t i = 0; i < vMN.size(); i++)
            {
                minVMN = (vMN[i] < minVMN) ? vMN[i] : minVMN;
                maxVMN = (vMN[i] > maxVMN) ? vMN[i] : maxVMN;
            }
            maxVM *= _showStressAlpha.getValue();
            maxVMN *= _showStressAlpha.getValue();


            if (_showVonMisesStressPerNode.getValue())
            {
                // Draw nodes (if node option enabled)
                std::vector<sofa::type::RGBAColor> nodeColors(x.size());
                std::vector<type::Vec3> pts(x.size());
                helper::ColorMap::evaluator<Real> evalColor = m_VonMisesColorMap->getEvaluator(minVMN, maxVMN);
                for (size_t nd = 0; nd < x.size(); nd++) {
                    pts[nd] = x[nd];
                    nodeColors[nd] = evalColor(vMN[nd]);
                }
                vparams->drawTool()->drawPoints(pts, 10, nodeColors);
            }
        }


        // Draw elements (if not "node only")
        std::vector< type::Vec3 > points;
        std::vector< sofa::type::RGBAColor > colorVector;
        typename VecElement::const_iterator it, it0;

        it0=_indexedElements->begin();
        for(int i = 0 ; i<m_RIDsize ;++i)
        {
            it = it0 + reducedIntegrationDomain(i);

            Index a = (*it)[0];
            Index b = (*it)[1];
            Index c = (*it)[2];
            Index d = (*it)[3];
            Coord center = (x[a] + x[b] + x[c] + x[d]) * 0.125;

            Coord pa = x[a];
            Coord pb = x[b];
            Coord pc = x[c];
            Coord pd = x[d];

            if ( ! vparams->displayFlags().getShowWireFrame() )
            {
                pa = (pa + center) * Real(0.6667);
                pb = (pb + center) * Real(0.6667);
                pc = (pc + center) * Real(0.6667);
                pd = (pd + center) * Real(0.6667);
            }

            // create corresponding colors
            sofa::type::RGBAColor color[4];
            if (drawVonMisesStress && _showVonMisesStressPerElement.getValue())
            {
                if(heterogeneous)
                {
                    float col = (float)((youngModulus[reducedIntegrationDomain(i)] - minYoung) / (maxYoung - minYoung));
                    float fac = col * 0.5f;
                    color[0] = sofa::type::RGBAColor(col       , 0.0f - fac, 1.0f - col, 1.0f);
                    color[1] = sofa::type::RGBAColor(col       , 0.5f - fac, 1.0f - col, 1.0f);
                    color[2] = sofa::type::RGBAColor(col       , 1.0f - fac, 1.0f - col, 1.0f);
                    color[3] = sofa::type::RGBAColor(col + 0.5f, 1.0f - fac, 1.0f - col, 1.0f);
                }
                else
                {
                    helper::ColorMap::evaluator<Real> evalColor = m_VonMisesColorMap->getEvaluator(minVM, maxVM);
                    sofa::type::RGBAColor col = evalColor(vM[reducedIntegrationDomain(i)]);
                    col[3] = 1.0f;
                    color[0] = col;
                    color[1] = col;
                    color[2] = col;
                    color[3] = col;
                }
            }
            else if (!drawVonMisesStress)
            {
                color[0] = sofa::type::RGBAColor(0.0, 0.0, 1.0, 1.0);
                color[1] = sofa::type::RGBAColor(0.0, 0.5, 1.0, 1.0);
                color[2] = sofa::type::RGBAColor(0.0, 1.0, 1.0, 1.0);
                color[3] = sofa::type::RGBAColor(0.5, 1.0, 1.0, 1.0);
            }

            // create 4 triangles per tetrahedron with corresponding colors
            points.insert(points.end(), { pa, pb, pc });
            colorVector.insert(colorVector.end(), { color[0], color[0], color[0] });

            points.insert(points.end(), { pb, pc, pd });
            colorVector.insert(colorVector.end(), { color[1], color[1], color[1] });

            points.insert(points.end(), { pc, pd, pa });
            colorVector.insert(colorVector.end(), { color[2], color[2], color[2] });

            points.insert(points.end(), { pd, pa, pb });
            colorVector.insert(colorVector.end(), { color[3], color[3], color[3] });
        }
        vparams->drawTool()->drawTriangles(points, colorVector);


        ////////////// DRAW ROTATIONS //////////////
        if (vparams->displayFlags().getShowNormals())
        {
            const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();
            std::vector< type::Vec3 > points[3];
            for(unsigned ii = 0; ii<  x.size() ; ii++)
            {
                Coord a = x[ii];
                Transformation R;
                TetrahedronFEMForceField<DataTypes>::getRotation(R, ii);
                Deriv v;
                // x
                v.x() =1.0; v.y()=0.0; v.z()=0.0;
                Coord b = a + R*v;
                points[0].push_back(a);
                points[0].push_back(b);
                // y
                v.x() =0.0; v.y()=1.0; v.z()=0.0;
                b = a + R*v;
                points[1].push_back(a);
                points[1].push_back(b);
                // z
                v.x() =0.0; v.y()=0.0; v.z()=1.0;
                b = a + R*v;
                points[2].push_back(a);
                points[2].push_back(b);
            }

            vparams->drawTool()->drawLines(points[0], 5, sofa::type::RGBAColor::red());
            vparams->drawTool()->drawLines(points[1], 5, sofa::type::RGBAColor::green());
            vparams->drawTool()->drawLines(points[2], 5, sofa::type::RGBAColor::blue());
        }

        vparams->drawTool()->restoreLastState();

}

template <class DataTypes>
void HyperReducedTetrahedronFEMForceField<DataTypes>::buildStiffnessMatrix(core::behavior::StiffnessMatrix* matrix)
{
    StiffnessMatrix JKJt, RJKJtRt;
    sofa::type::Mat<3, 3, Real> localMatrix(type::NOINIT);

    static constexpr Transformation identity = []
    {
        Transformation i;
        i.identity();
        return i;
    }();

    constexpr auto S = DataTypes::deriv_total_size; // size of node blocks
    constexpr auto N = Element::size();

    auto dfdx = matrix->getForceDerivativeIn(this->mstate)
                       .withRespectToPositionsIn(this->mstate);

    sofa::Size tetraId = 0;

    typename VecElement::const_iterator it;
    auto it0=_indexedElements->begin();
    int nbElementsConsidered;
    if (!d_performECSW.getValue())
        nbElementsConsidered = _indexedElements->size();
    else
        nbElementsConsidered = m_RIDsize;

    for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
    {
        if (!d_performECSW.getValue()){
            tetraId = numElem;
        }
        else
        {
            tetraId = reducedIntegrationDomain(numElem);
        }
        it = it0 + tetraId;

        const auto& rotation = method == SMALL ? identity : rotations[tetraId];
        this->computeStiffnessMatrix(JKJt, RJKJtRt, materialsStiffnesses[tetraId], strainDisplacements[tetraId], rotation);

        for (sofa::Index n1 = 0; n1 < N; n1++)
        {
            for (sofa::Index n2 = 0; n2 < N; n2++)
            {
                RJKJtRt.getsub(S * n1, S * n2, localMatrix); //extract the submatrix corresponding to the coupling of nodes n1 and n2
                if (!d_performECSW.getValue())
                    dfdx((*it)[n1] * S, (*it)[n2] * S) += -localMatrix;
                else
                    dfdx((*it)[n1] * S, (*it)[n2] * S) += -localMatrix*weights(tetraId);

            }
        }
    }
}


} // namespace sofa::component::forcefield
