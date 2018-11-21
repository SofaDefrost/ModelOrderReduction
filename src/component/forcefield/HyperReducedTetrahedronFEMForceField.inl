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
#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_INL
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_INL

#include "HyperReducedTetrahedronFEMForceField.h"
#include <sofa/core/visual/VisualParams.h>
#include <SofaBaseTopology/GridTopology.h>
#include <sofa/simulation/Simulation.h>
#include <sofa/helper/decompose.h>
#include <sofa/helper/gl/template.h>
#include <assert.h>
#include <fstream> // for reading the file
#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <set>
#include <SofaBaseLinearSolver/CompressedRowSparseMatrix.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/helper/AdvancedTimer.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include "../loader/MatrixLoader.h"

// verify timing
#include <sofa/helper/system/thread/CTime.h>


namespace sofa
{

namespace component
{

namespace forcefield
{

using sofa::component::loader::MatrixLoader;


//////////////////////////////////////////////////////////////////////
////////////////////  small displacements method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForceSmall( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex )
{

    const VecCoord &initialPoints=_initialPoints.getValue();
    //serr<<"HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForceSmall"<<sendl;
    Element index = *elementIt;
    Index a = index[0];
    Index b = index[1];
    Index c = index[2];
    Index d = index[3];

    // displacements
    Displacement D;
    D[0] = 0;
    D[1] = 0;
    D[2] = 0;
    D[3] =  initialPoints[b][0] - initialPoints[a][0] - p[b][0]+p[a][0];
    D[4] =  initialPoints[b][1] - initialPoints[a][1] - p[b][1]+p[a][1];
    D[5] =  initialPoints[b][2] - initialPoints[a][2] - p[b][2]+p[a][2];
    D[6] =  initialPoints[c][0] - initialPoints[a][0] - p[c][0]+p[a][0];
    D[7] =  initialPoints[c][1] - initialPoints[a][1] - p[c][1]+p[a][1];
    D[8] =  initialPoints[c][2] - initialPoints[a][2] - p[c][2]+p[a][2];
    D[9] =  initialPoints[d][0] - initialPoints[a][0] - p[d][0]+p[a][0];
    D[10] = initialPoints[d][1] - initialPoints[a][1] - p[d][1]+p[a][1];
    D[11] = initialPoints[d][2] - initialPoints[a][2] - p[d][2]+p[a][2];

    // compute force on element
    Displacement F;

    if(!_assembling.getValue())
    {
        this->computeForce( F, D, _plasticStrains[elementIndex], materialsStiffnesses[elementIndex], strainDisplacements[elementIndex] );
    }
    else if( _plasticMaxThreshold.getValue() <= 0 )
    {
        Transformation Rot;
        Rot[0][0]=Rot[1][1]=Rot[2][2]=1;
        Rot[0][1]=Rot[0][2]=0;
        Rot[1][0]=Rot[1][2]=0;
        Rot[2][0]=Rot[2][1]=0;


        StiffnessMatrix JKJt,tmp;
        this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[elementIndex], strainDisplacements[elementIndex],Rot);

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
            int row = index[i/3]*3+i%3;

            for(int j=0; j<12; ++j)
            {
                if(JKJt[i][j]!=0)
                {

                    int col = index[j/3]*3+j%3;
                    // search if the vertex is already take into account by another element
                    typename CompressedValue::iterator result = _stiffnesses[row].end();
                    for(typename CompressedValue::iterator it=_stiffnesses[row].begin(); it!=_stiffnesses[row].end()&&result==_stiffnesses[row].end(); ++it)
                    {
                        if( (*it).first == col )
                            result = it;
                    }

                    if( result==_stiffnesses[row].end() )
                        _stiffnesses[row].push_back( Col_Value(col,JKJt[i][j] )  );
                    else
                        (*result).second += JKJt[i][j];
                }
            }
        }
        F = JKJt * D;
    }
    else
    {
        msg_warning(this) << "TODO(HyperReducedTetrahedronFEMForceField): support for assembling system matrix when using plasticity.";
        return;
    }


    f[a] += Deriv( F[0], F[1], F[2] );
    f[b] += Deriv( F[3], F[4], F[5] );
    f[c] += Deriv( F[6], F[7], F[8] );
    f[d] += Deriv( F[9], F[10], F[11] );

}


template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::applyStiffnessSmall( Vector& f, const Vector& x, int i, Index a, Index b, Index c, Index d, SReal fact )
{
    Displacement X;

    X[0] = x[a][0];
    X[1] = x[a][1];
    X[2] = x[a][2];

    X[3] = x[b][0];
    X[4] = x[b][1];
    X[5] = x[b][2];

    X[6] = x[c][0];
    X[7] = x[c][1];
    X[8] = x[c][2];

    X[9] = x[d][0];
    X[10] = x[d][1];
    X[11] = x[d][2];

    Displacement F;
    this->computeForce( F, X, materialsStiffnesses[i], strainDisplacements[i], fact );

    f[a] += Deriv( -F[0], -F[1],  -F[2] );
    f[b] += Deriv( -F[3], -F[4],  -F[5] );
    f[c] += Deriv( -F[6], -F[7],  -F[8] );
    f[d] += Deriv( -F[9], -F[10], -F[11] );
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
    helper::fixed_array<Coord,4> deforme;
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
        this->updateGie<DataTypes>(indexList, contrib, elementIndex);
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
            int row = index[i/3]*3+i%3;

            for(int j=0; j<12; ++j)
            {
                int col = index[j/3]*3+j%3;

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
    Element index = *elementIt;

    Transformation A;
    A[0] = p[index[1]]-p[index[0]];
    A[1] = p[index[2]]-p[index[0]];
    A[2] = p[index[3]]-p[index[0]];

    Transformation R_0_2;
    helper::Decompose<Real>::polarDecomposition( A, R_0_2 );

    rotations[elementIndex].transpose( R_0_2 );

    // positions of the deformed and displaced Tetrahedre in its frame
    helper::fixed_array<Coord, 4>  deforme;
    for(int i=0; i<4; ++i)
        deforme[i] = R_0_2 * p[index[i]];

    // displacement
    Displacement D;
    D[0] = _rotatedInitialElements[elementIndex][0][0] - deforme[0][0];
    D[1] = _rotatedInitialElements[elementIndex][0][1] - deforme[0][1];
    D[2] = _rotatedInitialElements[elementIndex][0][2] - deforme[0][2];
    D[3] = _rotatedInitialElements[elementIndex][1][0] - deforme[1][0];
    D[4] = _rotatedInitialElements[elementIndex][1][1] - deforme[1][1];
    D[5] = _rotatedInitialElements[elementIndex][1][2] - deforme[1][2];
    D[6] = _rotatedInitialElements[elementIndex][2][0] - deforme[2][0];
    D[7] = _rotatedInitialElements[elementIndex][2][1] - deforme[2][1];
    D[8] = _rotatedInitialElements[elementIndex][2][2] - deforme[2][2];
    D[9] = _rotatedInitialElements[elementIndex][3][0] - deforme[3][0];
    D[10] = _rotatedInitialElements[elementIndex][3][1] - deforme[3][1];
    D[11] = _rotatedInitialElements[elementIndex][3][2] - deforme[3][2];



    Displacement F;
    if(_updateStiffnessMatrix.getValue())
    {
        // shape functions matrix
        this->computeStrainDisplacement( strainDisplacements[elementIndex], deforme[0],deforme[1],deforme[2],deforme[3] );
    }

    if(!_assembling.getValue())
    {
        this->computeForce( F, D, _plasticStrains[elementIndex], materialsStiffnesses[elementIndex], strainDisplacements[elementIndex] );
        for(int i=0; i<12; i+=3)
            f[index[i/3]] += rotations[elementIndex] * Deriv( F[i], F[i+1],  F[i+2] );
    }
    else
    {
        msg_warning(this) << "TODO(HyperReducedTetrahedronFEMForceField): support for assembling system matrix when using polar method.";
    }
}



//////////////////////////////////////////////////////////////////////
////////////////////  svd decomposition method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::accumulateForceSVD( Vector& f, const Vector & p, typename VecElement::const_iterator elementIt, Index elementIndex )
{
    if( _assembling.getValue() )
    {
        msg_warning(this) << "TODO(HyperReducedTetrahedronFEMForceField): support for assembling system matrix when using SVD method.";
        return;
    }

    Element index = *elementIt;

    Transformation A;
    A[0] = p[index[1]]-p[index[0]];
    A[1] = p[index[2]]-p[index[0]];
    A[2] = p[index[3]]-p[index[0]];

    defaulttype::Mat<3,3,Real> R_0_2;

    defaulttype::Mat<3,3,Real> F = A * _initialTransformation[elementIndex];

    if( determinant(F) < 1e-6 ) // inverted or too flat element -> SVD decomposition + handle degenerated cases
    {
        helper::Decompose<Real>::polarDecomposition_stable( F, R_0_2 );
        R_0_2 = R_0_2.multTransposed( _initialRotations[elementIndex] );
    }
    else // not inverted & not degenerated -> classical polar
    {
        helper::Decompose<Real>::polarDecomposition( A, R_0_2 );
    }



    rotations[elementIndex].transpose( R_0_2 );


    // positions of the deformed and displaced tetrahedron in its frame
    helper::fixed_array<Coord, 4>  deforme;
    for(int i=0; i<4; ++i)
        deforme[i] = R_0_2 * p[index[i]];

    // displacement
    Displacement D;
    D[0]  = _rotatedInitialElements[elementIndex][0][0] - deforme[0][0];
    D[1]  = _rotatedInitialElements[elementIndex][0][1] - deforme[0][1];
    D[2]  = _rotatedInitialElements[elementIndex][0][2] - deforme[0][2];
    D[3]  = _rotatedInitialElements[elementIndex][1][0] - deforme[1][0];
    D[4]  = _rotatedInitialElements[elementIndex][1][1] - deforme[1][1];
    D[5]  = _rotatedInitialElements[elementIndex][1][2] - deforme[1][2];
    D[6]  = _rotatedInitialElements[elementIndex][2][0] - deforme[2][0];
    D[7]  = _rotatedInitialElements[elementIndex][2][1] - deforme[2][1];
    D[8]  = _rotatedInitialElements[elementIndex][2][2] - deforme[2][2];
    D[9]  = _rotatedInitialElements[elementIndex][3][0] - deforme[3][0];
    D[10] = _rotatedInitialElements[elementIndex][3][1] - deforme[3][1];
    D[11] = _rotatedInitialElements[elementIndex][3][2] - deforme[3][2];

    if( _updateStiffnessMatrix.getValue() )
    {
        this->computeStrainDisplacement( strainDisplacements[elementIndex], deforme[0], deforme[1], deforme[2], deforme[3] );
    }

    Displacement Forces;
    this->computeForce( Forces, D, _plasticStrains[elementIndex], materialsStiffnesses[elementIndex], strainDisplacements[elementIndex] );
    for( int i=0 ; i<12 ; i+=3 )
    {
        f[index[i/3]] += rotations[elementIndex] * Deriv( Forces[i], Forces[i+1],  Forces[i+2] );
    }
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
    this->initMOR(_indexedElements->size());
}



template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::addForce (const core::MechanicalParams* /*mparams*/, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& /* d_v */)
{
    VecDeriv& f = *d_f.beginEdit();
    const VecCoord& p = d_x.getValue();

    sofa::helper::AdvancedTimer::stepBegin("time in AddForce");
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
    sofa::helper::AdvancedTimer::stepEnd("time in AddForce");
}

template<class DataTypes>
inline void HyperReducedTetrahedronFEMForceField<DataTypes>::addDForce(const core::MechanicalParams* mparams, DataVecDeriv& d_df, const DataVecDeriv& d_dx)
{
    VecDeriv& df = *d_df.beginEdit();
    const VecDeriv& dx = d_dx.getValue();
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    sofa::helper::AdvancedTimer::stepBegin("time in AddDDDForce");

    df.resize(dx.size());
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
    sofa::helper::AdvancedTimer::stepEnd("time in AddDDDForce");
}

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
void HyperReducedTetrahedronFEMForceField<DataTypes>::draw(const core::visual::VisualParams* vparams)
{

    if (_computeVonMisesStress.getValue() > 0) {
        if (updateVonMisesStress)
            this->computeVonMisesStress();
    }

    if (!vparams->displayFlags().getShowForceFields()) return;
    if (!this->mstate) return;

    if(needUpdateTopology)
    {
        reinit();
        needUpdateTopology = false;
    }

    const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();

    const bool edges = (drawAsEdges.getValue() || vparams->displayFlags().getShowWireFrame());
    const bool heterogeneous = (drawHeterogeneousTetra.getValue() && minYoung!=maxYoung);

    const VecReal & youngModulus = _youngModulus.getValue();

    /// vonMises stress
    Real minVM = (Real)1e20, maxVM = (Real)-1e20;
    Real minVMN = (Real)1e20, maxVMN = (Real)-1e20;
    helper::ReadAccessor<Data<helper::vector<Real> > > vM =  _vonMisesPerElement;
    helper::ReadAccessor<Data<helper::vector<Real> > > vMN =  _vonMisesPerNode;
    if (_computeVonMisesStress.getValue() > 0) {
        if (updateVonMisesStress)
            this->computeVonMisesStress();

        for (size_t i = 0; i < vM.size(); i++) {
            minVM = (vM[i] < minVM) ? vM[i] : minVM;
            maxVM = (vM[i] > maxVM) ? vM[i] : maxVM;
        }

        if (maxVM < prevMaxStress)
            maxVM = prevMaxStress;

        for (size_t i = 0; i < vMN.size(); i++) {
            minVMN = (vMN[i] < minVMN) ? vMN[i] : minVMN;
            maxVMN = (vMN[i] > maxVMN) ? vMN[i] : maxVMN;
        }

        maxVM*=_showStressAlpha.getValue();
        maxVMN*=_showStressAlpha.getValue();

    }

    vparams->drawTool()->setLightingEnabled(false);

#ifdef SIMPLEFEM_COLORMAP
    if (_showVonMisesStressPerNode.getValue()) {
        std::vector<defaulttype::Vec4f> nodeColors(x.size());
        std::vector<defaulttype::Vector3> pts(x.size());
        helper::ColorMap::evaluator<Real> evalColor = m_VonMisesColorMap.getEvaluator(minVMN, maxVMN);
        for (size_t nd = 0; nd < x.size(); nd++) {
            pts[nd] = x[nd];
            nodeColors[nd] = evalColor(vMN[nd]);
        }
        vparams->drawTool()->drawPoints(pts, 10, nodeColors);
    }
#endif

    if (edges)
    {
        std::vector< defaulttype::Vector3 > points[3];
        typename VecElement::const_iterator it, it0;
        int i;
        it0 = _indexedElements->begin();
        for( i = 0 ; i<m_RIDsize ;++i)
        {
            it = it0 + reducedIntegrationDomain(i);
            Index a = (*it)[0];
            Index b = (*it)[1];
            Index c = (*it)[2];
            Index d = (*it)[3];
            Coord pa = x[a];
            Coord pb = x[b];
            Coord pc = x[c];
            Coord pd = x[d];

            points[0].push_back(pa);
            points[0].push_back(pb);
            points[0].push_back(pc);
            points[0].push_back(pd);

            points[1].push_back(pa);
            points[1].push_back(pc);
            points[1].push_back(pb);
            points[1].push_back(pd);

            points[2].push_back(pa);
            points[2].push_back(pd);
            points[2].push_back(pb);
            points[2].push_back(pc);

            if(heterogeneous)
            {
                float col = (float)((youngModulus[i]-minYoung) / (maxYoung-minYoung));
                float fac = col * 0.5f;
                defaulttype::Vec<4,float> color2 = defaulttype::Vec<4,float>(col      , 0.5f - fac , 1.0f-col,1.0f);
                defaulttype::Vec<4,float> color3 = defaulttype::Vec<4,float>(col      , 1.0f - fac , 1.0f-col,1.0f);
                defaulttype::Vec<4,float> color4 = defaulttype::Vec<4,float>(col+0.5f , 1.0f - fac , 1.0f-col,1.0f);

                vparams->drawTool()->drawLines(points[0],1,color2 );
                vparams->drawTool()->drawLines(points[1],1,color3 );
                vparams->drawTool()->drawLines(points[2],1,color4 );

                for(unsigned int i=0 ; i<3 ; i++) points[i].clear();
            } else {
#ifdef SIMPLEFEM_COLORMAP
                if (_computeVonMisesStress.getValue() > 0) {
                    for(unsigned int i=0 ; i<3 ; i++) points[i].clear();
                }
#endif
            }
        }

        if(!heterogeneous
        #ifdef SIMPLEFEM_COLORMAP
                && _computeVonMisesStress.getValue() == 0
        #endif
                )
        {
            vparams->drawTool()->drawLines(points[0], 1, defaulttype::Vec<4,float>(0.0,0.5,1.0,1.0));
            vparams->drawTool()->drawLines(points[1], 1, defaulttype::Vec<4,float>(0.0,1.0,1.0,1.0));
            vparams->drawTool()->drawLines(points[2], 1, defaulttype::Vec<4,float>(0.5,1.0,1.0,1.0));
        }
    }
    else
    {

        std::vector< defaulttype::Vector3 > points[4];
        typename VecElement::const_iterator it, it0;
        unsigned int i;

        it0 = _indexedElements->begin();
        for( i = 0 ; i<m_RIDsize ;++i)
        {
            it = it0 + reducedIntegrationDomain(i);
            Index a = (*it)[0];
            Index b = (*it)[1];
            Index c = (*it)[2];
            Index d = (*it)[3];
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

            if(heterogeneous)
            {
                float col = (float)((youngModulus[i]-minYoung) / (maxYoung-minYoung));
                float fac = col * 0.5f;
                defaulttype::Vec<4,float> color1 = defaulttype::Vec<4,float>(col      , 0.0f - fac , 1.0f-col,1.0f);
                defaulttype::Vec<4,float> color2 = defaulttype::Vec<4,float>(col      , 0.5f - fac , 1.0f-col,1.0f);
                defaulttype::Vec<4,float> color3 = defaulttype::Vec<4,float>(col      , 1.0f - fac , 1.0f-col,1.0f);
                defaulttype::Vec<4,float> color4 = defaulttype::Vec<4,float>(col+0.5f , 1.0f - fac , 1.0f-col,1.0f);

                vparams->drawTool()->drawTriangles(points[0],color1 );
                vparams->drawTool()->drawTriangles(points[1],color2 );
                vparams->drawTool()->drawTriangles(points[2],color3 );
                vparams->drawTool()->drawTriangles(points[3],color4 );

                for(unsigned int i=0 ; i<4 ; i++) points[i].clear();
            } else {
#ifdef SIMPLEFEM_COLORMAP
                if (_computeVonMisesStress.getValue() > 0) {
                    helper::ColorMap::evaluator<Real> evalColor = m_VonMisesColorMap.getEvaluator(minVM, maxVM);
                    defaulttype::Vec4f col = evalColor(vM[i]); //*vM[i]);

                    col[3] = 1.0f;
                    vparams->drawTool()->drawTriangles(points[0],col);
                    vparams->drawTool()->drawTriangles(points[1],col);
                    vparams->drawTool()->drawTriangles(points[2],col);
                    vparams->drawTool()->drawTriangles(points[3],col);

                    for(unsigned int i=0 ; i<4 ; i++) points[i].clear();
                }
#endif
            }

        }

        if(!heterogeneous
        #ifdef SIMPLEFEM_COLORMAP
                && _computeVonMisesStress.getValue() == 0
        #endif
                )
        {
            vparams->drawTool()->drawTriangles(points[0], defaulttype::Vec<4,float>(0.0,0.0,1.0,1.0));
            vparams->drawTool()->drawTriangles(points[1], defaulttype::Vec<4,float>(0.0,0.5,1.0,1.0));
            vparams->drawTool()->drawTriangles(points[2], defaulttype::Vec<4,float>(0.0,1.0,1.0,1.0));
            vparams->drawTool()->drawTriangles(points[3], defaulttype::Vec<4,float>(0.5,1.0,1.0,1.0));
        }

    }

    ////////////// AFFICHAGE DES ROTATIONS ////////////////////////
    if (vparams->displayFlags().getShowNormals())
    {

        std::vector< defaulttype::Vector3 > points[3];

        for(unsigned ii = 0; ii<  x.size() ; ii++)
        {
            Coord a = x[ii];
            Transformation R;
            this->getRotation(R, ii);
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

        vparams->drawTool()->drawLines(points[0], 5, defaulttype::Vec<4,float>(1,0,0,1));
        vparams->drawTool()->drawLines(points[1], 5, defaulttype::Vec<4,float>(0,1,0,1));
        vparams->drawTool()->drawLines(points[2], 5, defaulttype::Vec<4,float>(0,0,1,1));

    }
}

template<class DataTypes>
void HyperReducedTetrahedronFEMForceField<DataTypes>::addKToMatrix(const core::MechanicalParams* mparams, const sofa::core::behavior::MultiMatrixAccessor* matrix )
{
    sofa::core::behavior::MultiMatrixAccessor::MatrixRef r = matrix->getMatrix(this->mstate);
    if (r)
        addKToMatrix(r.matrix, mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue()), r.offset);
    else msg_error(this) << "addKToMatrix found no valid matrix accessor." ;
}

template<class DataTypes>
void HyperReducedTetrahedronFEMForceField<DataTypes>::addKToMatrix(sofa::defaulttype::BaseMatrix *mat, SReal k, unsigned int &offset)
{
    // Build Matrix Block for this ForceField
    unsigned int i,j,n1, n2, row, column, ROW, COLUMN , IT;

    Transformation Rot;
    StiffnessMatrix JKJt,tmp;

    typename VecElement::const_iterator it, it0;

    Index noeud1, noeud2;
    int offd3 = offset/3;

    Rot[0][0]=Rot[1][1]=Rot[2][2]=1;
    Rot[0][1]=Rot[0][2]=0;
    Rot[1][0]=Rot[1][2]=0;
    Rot[2][0]=Rot[2][1]=0;


    it0=_indexedElements->begin();
    unsigned int nbElementsConsidered;
    if (!d_performECSW.getValue())
        nbElementsConsidered = _indexedElements->size();
    else
        nbElementsConsidered = m_RIDsize;
    SReal kTimesWeight;

    if (sofa::component::linearsolver::CompressedRowSparseMatrix<defaulttype::Mat<3,3,double> > * crsmat = dynamic_cast<sofa::component::linearsolver::CompressedRowSparseMatrix<defaulttype::Mat<3,3,double> > * >(mat))
    {


        for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
        {
            if (!d_performECSW.getValue()){
                IT = numElem;
            }
            else
            {
                IT = reducedIntegrationDomain(numElem);
            }
            it = it0 + IT;

            if (method == SMALL) this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[IT], strainDisplacements[IT],Rot);
            else this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[IT], strainDisplacements[IT],rotations[IT]);

            if (!d_performECSW.getValue())
                kTimesWeight = k;
            else
                kTimesWeight = k*weights(IT);

            defaulttype::Mat<3,3,double> tmpBlock[4][4];
            // find index of node 1
            for (n1=0; n1<4; n1++)
            {
                for(i=0; i<3; i++)
                {
                    for (n2=0; n2<4; n2++)
                    {
                        for (j=0; j<3; j++)
                        {
                            tmpBlock[n1][n2][i][j] = - tmp[n1*3+i][n2*3+j]*kTimesWeight;
                        }
                    }
                }
            }
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[0],true) +=  tmpBlock[0][0];
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[1],true) +=  tmpBlock[0][1];
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[2],true) +=  tmpBlock[0][2];
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[3],true) +=  tmpBlock[0][3];

            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[0],true) +=  tmpBlock[1][0];
            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[1],true) +=  tmpBlock[1][1];
            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[2],true) +=  tmpBlock[1][2];
            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[3],true) +=  tmpBlock[1][3];

            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[0],true) +=  tmpBlock[2][0];
            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[1],true) +=  tmpBlock[2][1];
            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[2],true) +=  tmpBlock[2][2];
            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[3],true) +=  tmpBlock[2][3];

            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[0],true) +=  tmpBlock[3][0];
            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[1],true) +=  tmpBlock[3][1];
            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[2],true) +=  tmpBlock[3][2];
            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[3],true) +=  tmpBlock[3][3];
        }

    }
    else if (sofa::component::linearsolver::CompressedRowSparseMatrix<defaulttype::Mat<3,3,float> > * crsmat = dynamic_cast<sofa::component::linearsolver::CompressedRowSparseMatrix<defaulttype::Mat<3,3,float> > * >(mat))
    {
        for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
        {
            if (!d_performECSW.getValue()){
                IT = numElem;
            }
            else
            {
                IT = reducedIntegrationDomain(numElem);
            }
            it = it0 + IT;

            if (method == SMALL) this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[IT], strainDisplacements[IT],Rot);
            else this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[IT], strainDisplacements[IT],rotations[IT]);


            if (!d_performECSW.getValue())
                kTimesWeight = k;
            else
                kTimesWeight = k*weights(IT);

            defaulttype::Mat<3,3,double> tmpBlock[4][4];
            // find index of node 1
            for (n1=0; n1<4; n1++)
            {
                for(i=0; i<3; i++)
                {
                    for (n2=0; n2<4; n2++)
                    {
                        for (j=0; j<3; j++)
                        {
                            tmpBlock[n1][n2][i][j] = - tmp[n1*3+i][n2*3+j]*kTimesWeight;
                        }
                    }
                }
            }

            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[0],true) += tmpBlock[0][0];
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[1],true) += tmpBlock[0][1];
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[2],true) += tmpBlock[0][2];
            *crsmat->wbloc(offd3 + (*it)[0], offd3 + (*it)[3],true) += tmpBlock[0][3];

            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[0],true) += tmpBlock[1][0];
            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[1],true) += tmpBlock[1][1];
            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[2],true) += tmpBlock[1][2];
            *crsmat->wbloc(offd3 + (*it)[1], offd3 + (*it)[3],true) += tmpBlock[1][3];

            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[0],true) += tmpBlock[2][0];
            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[1],true) += tmpBlock[2][1];
            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[2],true) += tmpBlock[2][2];
            *crsmat->wbloc(offd3 + (*it)[2], offd3 + (*it)[3],true) += tmpBlock[2][3];

            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[0],true) += tmpBlock[3][0];
            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[1],true) += tmpBlock[3][1];
            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[2],true) += tmpBlock[3][2];
            *crsmat->wbloc(offd3 + (*it)[3], offd3 + (*it)[3],true) += tmpBlock[3][3];
        }
    }
    else
    {
        for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
        {
            if (!d_performECSW.getValue()){
                IT = numElem;
            }
            else
            {
                IT = reducedIntegrationDomain(numElem);
            }
            it = it0 + IT;

            if (method == SMALL)
                this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[IT], strainDisplacements[IT],Rot);
            else
                this->computeStiffnessMatrix(JKJt,tmp,materialsStiffnesses[IT], strainDisplacements[IT],rotations[IT]);

            if (!d_performECSW.getValue())
                kTimesWeight = k;
            else
                kTimesWeight = k*weights(IT);

            // find index of node 1
            for (n1=0; n1<4; n1++)
            {
                noeud1 = (*it)[n1];

                for(i=0; i<3; i++)
                {
                    ROW = offset+3*noeud1+i;
                    row = 3*n1+i;
                    // find index of node 2
                    for (n2=0; n2<4; n2++)
                    {
                        noeud2 = (*it)[n2];


                        for (j=0; j<3; j++)
                        {
                            COLUMN = offset+3*noeud2+j;
                            column = 3*n2+j;
                            mat->add(ROW, COLUMN, -  tmp[row][column]*kTimesWeight);
                        }
                    }
                }
            }

        }
    }
}



} // namespace forcefield

} // namespace component

} // namespace sofa

#endif // SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONFEMFORCEFIELD_INL

