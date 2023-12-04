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

#include <ModelOrderReduction/component/forcefield/HyperReducedTetrahedralCorotationalFEMForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/component/topology/container/grid/GridTopology.h>
#include <sofa/simulation/Simulation.h>
#include <sofa/helper/decompose.h>
#include <sofa/core/topology/TopologyData.inl>
#include <assert.h>
#include <iostream>
#include <set>


namespace sofa::component::solidmechanics::fem::elastic
{


template< class DataTypes>
HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::HyperReducedTetrahedralCorotationalFEMForceField()
{
    this->addAlias(&_assembling, "assembling");
    _poissonRatio.setWidget("poissonRatio");

    _poissonRatio.setRequired(true);
    _youngModulus.setRequired(true);
}

template <class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::init()
{

    TetrahedralCorotationalFEMForceField<DataTypes>::init();
    this->initMOR(_topology->getNbTetrahedra(),notMuted());

}


template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::addForce(const core::MechanicalParams* /* mparams */, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& /* d_v */)
{
    VecDeriv& f = *d_f.beginEdit();
    const VecCoord& p = d_x.getValue();

    switch(method)
    {
    case SMALL :
    {
        for(unsigned int i = 0 ; i<_topology->getNbTetrahedra(); ++i)
        {
            accumulateForceSmall( f, p, i );
        }
        break;
    }
    case LARGE :
    {
        if (d_performECSW.getValue())
        {
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                accumulateForceLarge( f, p, reducedIntegrationDomain(i) );
            }
        }
        else
        {
            for(unsigned int i = 0 ; i<_topology->getNbTetrahedra(); ++i)
            {
                accumulateForceLarge( f, p, i );
            }
        }


        break;
    }
    case POLAR :
    {
        for(unsigned int i = 0 ; i<_topology->getNbTetrahedra(); ++i)
        {
            accumulateForcePolar( f, p, i );
        }
        break;
    }
    }
    this->saveGieFile(_topology->getNbTetrahedra());
    d_f.endEdit();
}

template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::addDForce(const core::MechanicalParams* mparams, DataVecDeriv& d_df, const DataVecDeriv& d_dx)
{
    VecDeriv& df = *d_df.beginEdit();
    const VecDeriv& dx = d_dx.getValue();

    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    switch(method)
    {
    case SMALL :
    {
        for(unsigned int i = 0 ; i<_topology->getNbTetrahedra(); ++i)
        {
            const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(i);
            Index a = t[0];
            Index b = t[1];
            Index c = t[2];
            Index d = t[3];

            applyStiffnessSmall( df, dx, i, a,b,c,d, kFactor );
        }
        break;
    }
    case LARGE :
    {
        if (!d_performECSW.getValue())
        {
            for(unsigned int i = 0 ; i<_topology->getNbTetrahedra(); ++i)
            {
                const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(i);
                Index a = t[0];
                Index b = t[1];
                Index c = t[2];
                Index d = t[3];

                applyStiffnessLarge( df, dx, i, a,b,c,d, kFactor );
            }
        }
        else
        {
            for(unsigned int i = 0 ; i<m_RIDsize ;++i)
            {
                const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(reducedIntegrationDomain(i));
                Index a = t[0];
                Index b = t[1];
                Index c = t[2];
                Index d = t[3];

                applyStiffnessLarge( df, dx, reducedIntegrationDomain(i), a,b,c,d, kFactor );
            }

        }
        break;
    }
    case POLAR :
    {
        for(unsigned int i = 0 ; i<_topology->getNbTetrahedra(); ++i)
        {
            const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(i);
            Index a = t[0];
            Index b = t[1];
            Index c = t[2];
            Index d = t[3];

            applyStiffnessPolar( df, dx, i, a,b,c,d, kFactor );
        }
        break;
    }
    }

    d_df.endEdit();
}


//////////////////////////////////////////////////////////////////////
////////////////////  small displacements method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::accumulateForceSmall( Vector& f, const Vector & p,Index elementIndex )
{

    const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(elementIndex);
    const VecCoord& X0=this->mstate->read(core::ConstVecCoordId::restPosition())->getValue();


    Index a = t[0];
    Index b = t[1];
    Index c = t[2];
    Index d = t[3];

    // displacements
    Displacement D;
    D[0] = 0;
    D[1] = 0;
    D[2] = 0;
    D[3] =  (X0)[b][0] - (X0)[a][0] - p[b][0]+p[a][0];
    D[4] =  (X0)[b][1] - (X0)[a][1] - p[b][1]+p[a][1];
    D[5] =  (X0)[b][2] - (X0)[a][2] - p[b][2]+p[a][2];
    D[6] =  (X0)[c][0] - (X0)[a][0] - p[c][0]+p[a][0];
    D[7] =  (X0)[c][1] - (X0)[a][1] - p[c][1]+p[a][1];
    D[8] =  (X0)[c][2] - (X0)[a][2] - p[c][2]+p[a][2];
    D[9] =  (X0)[d][0] - (X0)[a][0] - p[d][0]+p[a][0];
    D[10] = (X0)[d][1] - (X0)[a][1] - p[d][1]+p[a][1];
    D[11] = (X0)[d][2] - (X0)[a][2] - p[d][2]+p[a][2];

    // compute force on element
    Displacement F;

    const type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = tetrahedronInfo.getValue();

    if(!_assembling.getValue())
    {
        this->computeForce( F, D,tetrahedronInf[elementIndex].materialMatrix,tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix );
    }
    else
    {
        Transformation Rot;
        Rot[0][0]=Rot[1][1]=Rot[2][2]=1;
        Rot[0][1]=Rot[0][2]=0;
        Rot[1][0]=Rot[1][2]=0;
        Rot[2][0]=Rot[2][1]=0;


        StiffnessMatrix JKJt,tmp;
        this->computeStiffnessMatrix(JKJt,tmp,tetrahedronInf[elementIndex].materialMatrix,tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix,Rot);


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
            int row = t[i/3]*3+i%3;

            for(int j=0; j<12; ++j)
            {
                if(JKJt[i][j]!=0)
                {

                    int col = t[j/3]*3+j%3;

                    //typename CompressedValue::iterator result = _stiffnesses[row].find(col);


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

    f[a] += Deriv( F[0], F[1], F[2] );
    f[b] += Deriv( F[3], F[4], F[5] );
    f[c] += Deriv( F[6], F[7], F[8] );
    f[d] += Deriv( F[9], F[10], F[11] );
}

template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::applyStiffnessSmall( Vector& f, const Vector& x, int i, Index a, Index b, Index c, Index d, SReal fact )
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

    const type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = tetrahedronInfo.getValue();

    this->computeForce( F, X,tetrahedronInf[i].materialMatrix,tetrahedronInf[i].strainDisplacementTransposedMatrix, fact);

    f[a] += Deriv( -F[0], -F[1],  -F[2] );
    f[b] += Deriv( -F[3], -F[4],  -F[5] );
    f[c] += Deriv( -F[6], -F[7],  -F[8] );
    f[d] += Deriv( -F[9], -F[10], -F[11] );
}

//////////////////////////////////////////////////////////////////////
////////////////////  large displacements method  ////////////////////
//////////////////////////////////////////////////////////////////////


template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::accumulateForceLarge( Vector& f, const Vector & p, Index elementIndex )
{
    const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(elementIndex);

    type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = *(tetrahedronInfo.beginEdit());

    // Rotation matrix (deformed and displaced Tetrahedron/world)
    Transformation R_0_2;
    this->computeRotationLarge( R_0_2, p, t[0],t[1],t[2]);
    tetrahedronInf[elementIndex].rotation.transpose(R_0_2);

    // positions of the deformed and displaced Tetrahedron in its frame
    type::fixed_array<Coord,4> deforme;
    for(int i=0; i<4; ++i)
        deforme[i] = R_0_2*p[t[i]];

    deforme[1][0] -= deforme[0][0];
    deforme[2][0] -= deforme[0][0];
    deforme[2][1] -= deforme[0][1];
    deforme[3] -= deforme[0];

    // displacement
    Displacement D;
    D[0] = 0;
    D[1] = 0;
    D[2] = 0;
    D[3] = tetrahedronInf[elementIndex].rotatedInitialElements[1][0] - deforme[1][0];
    D[4] = 0;
    D[5] = 0;
    D[6] = tetrahedronInf[elementIndex].rotatedInitialElements[2][0] - deforme[2][0];
    D[7] = tetrahedronInf[elementIndex].rotatedInitialElements[2][1] - deforme[2][1];
    D[8] = 0;
    D[9] = tetrahedronInf[elementIndex].rotatedInitialElements[3][0] - deforme[3][0];
    D[10] = tetrahedronInf[elementIndex].rotatedInitialElements[3][1] - deforme[3][1];
    D[11] =tetrahedronInf[elementIndex].rotatedInitialElements[3][2] - deforme[3][2];

    //serr<<"D : "<<D<<sendl;

    Displacement F;
    if(_updateStiffnessMatrix.getValue())
    {
        StrainDisplacementTransposed& J = tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix;
        J[0][0] = J[1][3] = J[2][5]   = ( - deforme[2][1]*deforme[3][2] );
        J[1][1] = J[0][3] = J[2][4]   = ( deforme[2][0]*deforme[3][2] - deforme[1][0]*deforme[3][2] );
        J[2][2] = J[0][5] = J[1][4]   = ( deforme[2][1]*deforme[3][0] - deforme[2][0]*deforme[3][1] + deforme[1][0]*deforme[3][1] - deforme[1][0]*deforme[2][1] );

        J[3][0] = J[4][3] = J[5][5]   = ( deforme[2][1]*deforme[3][2] );
        J[4][1] = J[3][3] = J[5][4]  = ( - deforme[2][0]*deforme[3][2] );
        J[5][2] = J[3][5] = J[4][4]   = ( - deforme[2][1]*deforme[3][0] + deforme[2][0]*deforme[3][1] );

        J[7][1] = J[6][3] = J[8][4]  = ( deforme[1][0]*deforme[3][2] );
        J[8][2] = J[6][5] = J[7][4]   = ( - deforme[1][0]*deforme[3][1] );

        J[11][2] = J[9][5] = J[10][4] = ( deforme[1][0]*deforme[2][1] );
    }
    std::vector<Deriv> contrib;
    std::vector<unsigned int> indexList;
    contrib.resize(4);
    indexList.resize(4);

    if(!_assembling.getValue())
    {
        // compute force on element
        this->computeForce( F, D, tetrahedronInf[elementIndex].materialMatrix, tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix);
        for(int i=0; i<12; i+=3)
        {
            contrib[i/3] = tetrahedronInf[elementIndex].rotation * Deriv( F[i], F[i+1],  F[i+2] );
            indexList[i/3] = t[i/3];
            if (!d_performECSW.getValue())
                f[t[i/3]] += contrib[i/3];
            else
                f[t[i/3]] += weights(elementIndex)*contrib[i/3];
        }
    }
    else
    {
        tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix[6][0] = 0;
        tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix[9][0] = 0;
        tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix[10][1] = 0;

        StiffnessMatrix RJKJt, RJKJtRt;
        this->computeStiffnessMatrix(RJKJt,RJKJtRt,tetrahedronInf[elementIndex].materialMatrix, tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix,tetrahedronInf[elementIndex].rotation);


        //erase the stiffness matrix at each time step
        if(elementIndex==reducedIntegrationDomain(0))
        {
            for(unsigned int i=0; i<_stiffnesses.size(); ++i)
            {
                _stiffnesses[i].resize(0);
            }
        }

        for(int i=0; i<12; ++i)
        {
            int row = t[i/3]*3+i%3;

            for(int j=0; j<12; ++j)
            {
                int col = t[j/3]*3+j%3;

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
        {
            contrib[i/3] = Deriv( F[i], F[i+1],  F[i+2] );
            indexList[i/3] = t[i/3];
            if (!d_performECSW.getValue())
                f[t[i/3]] += Deriv( F[i], F[i+1],  F[i+2] );
            else
                f[t[i/3]] += weights(elementIndex)*contrib[i/3];
        }
    }
    this->template updateGie<DataTypes>(indexList, contrib, elementIndex);

    tetrahedronInfo.endEdit();
}

template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::applyStiffnessLarge( Vector& f, const Vector& x, int i, Index a, Index b, Index c, Index d, SReal fact)
{
    const type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = tetrahedronInfo.getValue();

    Transformation R_0_2;
    R_0_2.transpose(tetrahedronInf[i].rotation);

    Displacement X;
    Coord x_2;

    x_2 = R_0_2*x[a];
    X[0] = x_2[0];
    X[1] = x_2[1];
    X[2] = x_2[2];

    x_2 = R_0_2*x[b];
    X[3] = x_2[0];
    X[4] = x_2[1];
    X[5] = x_2[2];

    x_2 = R_0_2*x[c];
    X[6] = x_2[0];
    X[7] = x_2[1];
    X[8] = x_2[2];

    x_2 = R_0_2*x[d];
    X[9] = x_2[0];
    X[10] = x_2[1];
    X[11] = x_2[2];

    Displacement F;

    this->computeForce( F, X,tetrahedronInf[i].materialMatrix, tetrahedronInf[i].strainDisplacementTransposedMatrix, fact);

    if (!d_performECSW.getValue()){

        f[a] += tetrahedronInf[i].rotation * Deriv( -F[0], -F[1],  -F[2] );
        f[b] += tetrahedronInf[i].rotation * Deriv( -F[3], -F[4],  -F[5] );
        f[c] += tetrahedronInf[i].rotation * Deriv( -F[6], -F[7],  -F[8] );
        f[d] += tetrahedronInf[i].rotation * Deriv( -F[9], -F[10], -F[11] );
    }
    else
    {
        f[a] += weights(i)*tetrahedronInf[i].rotation * Deriv( -F[0], -F[1],  -F[2] );
        f[b] += weights(i)*tetrahedronInf[i].rotation * Deriv( -F[3], -F[4],  -F[5] );
        f[c] += weights(i)*tetrahedronInf[i].rotation * Deriv( -F[6], -F[7],  -F[8] );
        f[d] += weights(i)*tetrahedronInf[i].rotation * Deriv( -F[9], -F[10], -F[11] );
    }
}

//////////////////////////////////////////////////////////////////////
////////////////////  polar decomposition method  ////////////////////
//////////////////////////////////////////////////////////////////////

template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::accumulateForcePolar( Vector& f, const Vector & p, Index elementIndex )
{
    const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(elementIndex);

    Transformation A;
    A[0] = p[t[1]]-p[t[0]];
    A[1] = p[t[2]]-p[t[0]];
    A[2] = p[t[3]]-p[t[0]];

    Transformation R_0_2;
    type::MatNoInit<3,3,Real> S;
    helper::Decompose<Real>::polarDecomposition(A, R_0_2);

    type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = *(tetrahedronInfo.beginEdit());

    tetrahedronInf[elementIndex].rotation.transpose( R_0_2 );

    // positions of the deformed and displaced Tetrahedre in its frame
    type::fixed_array<Coord, 4>  deforme;
    for(int i=0; i<4; ++i)
        deforme[i] = R_0_2 * p[t[i]];

    // displacement
    Displacement D;
    D[0] = tetrahedronInf[elementIndex].rotatedInitialElements[0][0] - deforme[0][0];
    D[1] = tetrahedronInf[elementIndex].rotatedInitialElements[0][1] - deforme[0][1];
    D[2] = tetrahedronInf[elementIndex].rotatedInitialElements[0][2] - deforme[0][2];
    D[3] = tetrahedronInf[elementIndex].rotatedInitialElements[1][0] - deforme[1][0];
    D[4] = tetrahedronInf[elementIndex].rotatedInitialElements[1][1] - deforme[1][1];
    D[5] = tetrahedronInf[elementIndex].rotatedInitialElements[1][2] - deforme[1][2];
    D[6] = tetrahedronInf[elementIndex].rotatedInitialElements[2][0] - deforme[2][0];
    D[7] = tetrahedronInf[elementIndex].rotatedInitialElements[2][1] - deforme[2][1];
    D[8] = tetrahedronInf[elementIndex].rotatedInitialElements[2][2] - deforme[2][2];
    D[9] = tetrahedronInf[elementIndex].rotatedInitialElements[3][0] - deforme[3][0];
    D[10] = tetrahedronInf[elementIndex].rotatedInitialElements[3][1] - deforme[3][1];
    D[11] = tetrahedronInf[elementIndex].rotatedInitialElements[3][2] - deforme[3][2];
    //serr<<"D : "<<D<<sendl;

    Displacement F;
    if(_updateStiffnessMatrix.getValue())
    {
        // shape functions matrix
        this->computeStrainDisplacement( tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix, deforme[0],deforme[1],deforme[2],deforme[3]  );
    }

    if(!_assembling.getValue())
    {
        this->computeForce( F, D, tetrahedronInf[elementIndex].materialMatrix, tetrahedronInf[elementIndex].strainDisplacementTransposedMatrix );
        for(int i=0; i<12; i+=3)
            f[t[i/3]] += tetrahedronInf[elementIndex].rotation * Deriv( F[i], F[i+1],  F[i+2] );
    }
    else
    {
        // TODO: support for assembling system matrix when using polar method.
        msg_error() << this->getClassName() << " does not support assembling system matrix when using polar method.";
    }

    tetrahedronInfo.endEdit();
}

template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::applyStiffnessPolar( Vector& f, const Vector& x, int i, Index a, Index b, Index c, Index d, SReal fact )
{
    type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = *(tetrahedronInfo.beginEdit());

    Transformation R_0_2;
    R_0_2.transpose( tetrahedronInf[i].rotation );

    Displacement X;
    Coord x_2;

    x_2 = R_0_2*x[a];
    X[0] = x_2[0];
    X[1] = x_2[1];
    X[2] = x_2[2];

    x_2 = R_0_2*x[b];
    X[3] = x_2[0];
    X[4] = x_2[1];
    X[5] = x_2[2];

    x_2 = R_0_2*x[c];
    X[6] = x_2[0];
    X[7] = x_2[1];
    X[8] = x_2[2];

    x_2 = R_0_2*x[d];
    X[9] = x_2[0];
    X[10] = x_2[1];
    X[11] = x_2[2];

    Displacement F;

    //serr<<"X : "<<X<<sendl;

    this->computeForce( F, X, tetrahedronInf[i].materialMatrix, tetrahedronInf[i].strainDisplacementTransposedMatrix, fact);

    //serr<<"F : "<<F<<sendl;

    f[a] -= tetrahedronInf[i].rotation * Deriv( F[0], F[1],  F[2] );
    f[b] -= tetrahedronInf[i].rotation * Deriv( F[3], F[4],  F[5] );
    f[c] -= tetrahedronInf[i].rotation * Deriv( F[6], F[7],  F[8] );
    f[d] -= tetrahedronInf[i].rotation * Deriv( F[9], F[10], F[11] );

    tetrahedronInfo.endEdit();
}

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////


template<class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::draw(const core::visual::VisualParams* vparams)
{
    if (!vparams->displayFlags().getShowForceFields()) return;
    if (!this->mstate) return;
    if (!f_drawing.getValue()) return;

    vparams->drawTool()->saveLastState();

    const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();

    if (vparams->displayFlags().getShowWireFrame())
        vparams->drawTool()->setPolygonMode(0,true);


    std::vector< type::Vec3 > points[4];
    for(unsigned int i = 0 ; i<m_RIDsize ;++i)
    {
        const core::topology::BaseMeshTopology::Tetrahedron t=_topology->getTetrahedron(reducedIntegrationDomain(i));

        Index a = t[0];
        Index b = t[1];
        Index c = t[2];
        Index d = t[3];
        Coord center = (x[a]+x[b]+x[c]+x[d])*0.125;
        Coord pa = (x[a]+center)*(Real)0.666667;
        Coord pb = (x[b]+center)*(Real)0.666667;
        Coord pc = (x[c]+center)*(Real)0.666667;
        Coord pd = (x[d]+center)*(Real)0.666667;

// 		glColor4f(0,0,1,1);
        points[0].push_back(pa);
        points[0].push_back(pb);
        points[0].push_back(pc);

// 		glColor4f(0,0.5,1,1);
        points[1].push_back(pb);
        points[1].push_back(pc);
        points[1].push_back(pd);

// 		glColor4f(0,1,1,1);
        points[2].push_back(pc);
        points[2].push_back(pd);
        points[2].push_back(pa);

// 		glColor4f(0.5,1,1,1);
        points[3].push_back(pd);
        points[3].push_back(pa);
        points[3].push_back(pb);
    }

    vparams->drawTool()->drawTriangles(points[0], drawColor1.getValue());
    vparams->drawTool()->drawTriangles(points[1], drawColor2.getValue());
    vparams->drawTool()->drawTriangles(points[2], drawColor3.getValue());
    vparams->drawTool()->drawTriangles(points[3], drawColor4.getValue());

    if (vparams->displayFlags().getShowWireFrame())
        vparams->drawTool()->setPolygonMode(0,false);


    vparams->drawTool()->restoreLastState();
}

template <class DataTypes>
void HyperReducedTetrahedralCorotationalFEMForceField<DataTypes>::
buildStiffnessMatrix(core::behavior::StiffnessMatrix* matrix)
{
    StiffnessMatrix JKJt, RJKJtRt;
    sofa::type::Mat<3, 3, Real> localMatrix(type::NOINIT);

    const type::vector<typename TetrahedralCorotationalFEMForceField<DataTypes>::TetrahedronInformation>& tetrahedronInf = tetrahedronInfo.getValue();
    const sofa::core::topology::BaseMeshTopology::SeqTetrahedra& tetrahedra = _topology->getTetrahedra();

    unsigned int nbElementsConsidered;

    if (!d_performECSW.getValue())
        nbElementsConsidered = _topology->getNbTetrahedra();
    else
        nbElementsConsidered = m_RIDsize;


    static constexpr Transformation identity = []
    {
        Transformation i;
        i.identity();
        return i;
    }();


    auto dfdx = matrix->getForceDerivativeIn(this->mstate)
                    .withRespectToPositionsIn(this->mstate);

    std::size_t IT;
    for(std::size_t tetNum=0 ; tetNum < nbElementsConsidered ; ++tetNum)
    {
        if (!d_performECSW.getValue())
            IT = tetNum;
        else
            IT = reducedIntegrationDomain(tetNum);

        const auto& rotation = method == SMALL ? identity : tetrahedronInf[IT].rotation;
        this->computeStiffnessMatrix(JKJt, RJKJtRt, tetrahedronInf[IT].materialMatrix,
                               tetrahedronInf[IT].strainDisplacementTransposedMatrix, rotation);

        const core::topology::BaseMeshTopology::Tetrahedron tetra = tetrahedra[IT];

        static constexpr auto S = DataTypes::deriv_total_size; // size of node blocks
        for (sofa::Size n1 = 0; n1 < core::topology::BaseMeshTopology::Tetrahedron::size(); ++n1)
        {
            for (sofa::Size n2 = 0; n2 < core::topology::BaseMeshTopology::Tetrahedron::size(); ++n2)
            {
                RJKJtRt.getsub(S * n1, S * n2, localMatrix); //extract the submatrix corresponding to the coupling of nodes n1 and n2
                if (!d_performECSW.getValue())
                    dfdx(S * tetra[n1], S * tetra[n2]) += -localMatrix;
                else
                    dfdx(S * tetra[n1], S * tetra[n2]) += -localMatrix*weights(IT);
            }
        }
    }
}

} // namespace sofa::component::solidmechanics::fem::elastic
