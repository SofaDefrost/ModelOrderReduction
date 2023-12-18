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
#include <ModelOrderReduction/component/forcefield/HyperReducedHexahedronFEMForceField.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/simulation/Simulation.h>
#include <sofa/core/behavior/MultiMatrixAccessor.h>
#include <sofa/helper/decompose.h>
#include <assert.h>
#include <iostream>
#include <set>





// WARNING: indices ordering is different than in topology node
//
// 	   Y  7---------6
//     ^ /	       /|
//     |/	 Z    / |
//     3----^----2  |
//     |   /	 |  |
//     |  4------|--5
//     | / 	     | /
//     |/	     |/
//     0---------1-->X

namespace sofa::component::forcefield
{

using std::set;
using namespace sofa::defaulttype;


template <class DataTypes>
void HyperReducedHexahedronFEMForceField<DataTypes>::init()
{
    solidmechanics::fem::elastic::HexahedronFEMForceField<DataTypes>::init();
    this->initMOR(this->getIndexedElements()->size(),notMuted());
}

template<class DataTypes>
void HyperReducedHexahedronFEMForceField<DataTypes>::addForce (const core::MechanicalParams* /*mparams*/, DataVecDeriv& f, const DataVecCoord& p, const DataVecDeriv& /*v*/)
{
    WDataRefVecDeriv _f = f;
    RDataRefVecCoord _p = p;

    _f.resize(_p.size());

    if (needUpdateTopology)
    {
        reinit();
        needUpdateTopology = false;
    }

    unsigned int i=0;
    typename VecElement::const_iterator it, it0;

    switch(method)
    {
    case LARGE :
    {
        m_potentialEnergy = 0;

        if (!d_performECSW.getValue()){
            for(it=this->getIndexedElements()->begin(); it!=this->getIndexedElements()->end(); ++it,++i)
            {
                accumulateForceLarge( _f, _p, i, *it );
            }
        }
        else
        {
            it0=this->getIndexedElements()->begin();
            for( i = 0 ; i<m_RIDsize ;++i)
            {
                it = it0 + reducedIntegrationDomain(i);
                accumulateForceLarge( _f, _p, reducedIntegrationDomain(i), *it );
            }
        }
        m_potentialEnergy/=-2.0;
        break;
    }
    case POLAR :
    {
        m_potentialEnergy = 0;
        for(it=this->getIndexedElements()->begin(); it!=this->getIndexedElements()->end(); ++it,++i)
        {
            accumulateForcePolar( _f, _p, i, *it );
        }
        m_potentialEnergy/=-2.0;
        break;
    }
    case SMALL :
    {
        m_potentialEnergy = 0;
        for(it=this->getIndexedElements()->begin(); it!=this->getIndexedElements()->end(); ++it,++i)
        {
            accumulateForceSmall( _f, _p, i, *it );
        }
        m_potentialEnergy/=-2.0;
        break;
    }
    }
    this->saveGieFile(this->getIndexedElements()->size());


}

template<class DataTypes>
void HyperReducedHexahedronFEMForceField<DataTypes>::addDForce (const core::MechanicalParams *mparams, DataVecDeriv& v, const DataVecDeriv& x)
{
    WDataRefVecDeriv _df = v;
    RDataRefVecCoord _dx = x;
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    if (_df.size() != _dx.size())
        _df.resize(_dx.size());

    unsigned int i;
    typename VecElement::const_iterator it, it0;


    it0=this->getIndexedElements()->begin();
    size_t nbElementsConsidered;
    if (!d_performECSW.getValue()){
        nbElementsConsidered = this->getIndexedElements()->size();
    }
    else
    {
        nbElementsConsidered = m_RIDsize;
    }

    for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
    {
        if (!d_performECSW.getValue()){
            i = numElem;
        }
        else
        {
            i = reducedIntegrationDomain(numElem);
        }
        it = it0 + i;

        Displacement X;

        for(int w=0; w<8; ++w)
        {
            Coord x_2;
            x_2 = _rotations[i] * _dx[(*it)[w]];

            X[w*3] = x_2[0];
            X[w*3+1] = x_2[1];
            X[w*3+2] = x_2[2];
        }

        Displacement F;
        this->computeForce( F, X, _elementStiffnesses.getValue()[i] );
        for(int w=0; w<8; ++w)
        {
            Deriv contrib = _rotations[i].multTranspose(Deriv(F[w*3], F[w*3+1], F[w*3+2])) * kFactor;
            if (!d_performECSW.getValue())
            {
                _df[(*it)[w]] -= contrib;
            }
            else
            {
                _df[(*it)[w]] -= weights(i)*contrib;
            }
        }
    }
}





/////////////////////////////////////////////////
/////////////////////////////////////////////////
/////////////////////////////////////////////////
////////////// small displacements method

template<class DataTypes>
        void HyperReducedHexahedronFEMForceField<DataTypes>::accumulateForceSmall ( WDataRefVecDeriv &f, RDataRefVecCoord &p, sofa::Index i, const Element&elem )
{
    type::Vec<8,Coord> nodes;
    for(int w=0; w<8; ++w)
        nodes[w] = p[elem[w]];

    // positions of the deformed and displaced Tetrahedron in its frame
    type::Vec<8,Coord> deformed;
    for(int w=0; w<8; ++w)
        deformed[w] = nodes[w];

    // displacement
    Displacement D;
    for(int k=0 ; k<8 ; ++k )
    {
        int indice = k*3;
        for(int j=0 ; j<3 ; ++j )
            D[indice+j] = _rotatedInitialElements[i][k][j] - nodes[k][j];
    }


    if(f_updateStiffnessMatrix.getValue())
        this->computeElementStiffness( (*_elementStiffnesses.beginEdit())[i], _materialsStiffnesses[i], deformed, i, _sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0 );


    Displacement F; //forces
    this->computeForce( F, D, _elementStiffnesses.getValue()[i] ); // compute force on element

    for(int w=0; w<8; ++w)
        f[elem[w]] += Deriv( F[w*3],  F[w*3+1],   F[w*3+2]  ) ;

    m_potentialEnergy += dot(Deriv( F[0], F[1], F[2] ) ,-Deriv( D[0], D[1], D[2]));
    m_potentialEnergy += dot(Deriv( F[3], F[4], F[5] ) ,-Deriv( D[3], D[4], D[5] ));
    m_potentialEnergy += dot(Deriv( F[6], F[7], F[8] ) ,-Deriv( D[6], D[7], D[8] ));
    m_potentialEnergy += dot(Deriv( F[9], F[10], F[11]),-Deriv( D[9], D[10], D[11] ));
    m_potentialEnergy += dot(Deriv( F[12], F[13], F[14]),-Deriv( D[12], D[13], D[14] ));
    m_potentialEnergy += dot(Deriv( F[15], F[16], F[17]),-Deriv( D[15], D[16], D[17] ));
    m_potentialEnergy += dot(Deriv( F[18], F[19], F[20]),-Deriv( D[18], D[19], D[20] ));
    m_potentialEnergy += dot(Deriv( F[21], F[22], F[23]),-Deriv( D[21], D[22], D[23] ));
}


/////////////////////////////////////////////////
/////////////////////////////////////////////////
/////////////////////////////////////////////////
////////////// large displacements method


template<class DataTypes>
        void HyperReducedHexahedronFEMForceField<DataTypes>::accumulateForceLarge( WDataRefVecDeriv &f, RDataRefVecCoord &p, sofa::Index i, const Element&elem )
{
    type::Vec<8,Coord> nodes;

    for(int w=0; w<8; ++w)
        nodes[w] = p[elem[w]];

    Coord horizontal;
    horizontal = (nodes[1]-nodes[0] + nodes[2]-nodes[3] + nodes[5]-nodes[4] + nodes[6]-nodes[7])*.25;

    Coord vertical;
    vertical = (nodes[3]-nodes[0] + nodes[2]-nodes[1] + nodes[7]-nodes[4] + nodes[6]-nodes[5])*.25;
    this->computeRotationLarge( _rotations[i], horizontal,vertical);

// 	_rotations[i].transpose(R_0_2);

    // positions of the deformed and displaced Tetrahedron in its frame
    type::Vec<8,Coord> deformed;
    for(int w=0; w<8; ++w)
        deformed[w] = _rotations[i] * nodes[w];


    // displacement
    Displacement D;
    for(int k=0 ; k<8 ; ++k )
    {
        int indice = k*3;
        for(int j=0 ; j<3 ; ++j )
            D[indice+j] = _rotatedInitialElements[i][k][j] - deformed[k][j];
    }


    if(f_updateStiffnessMatrix.getValue())
        this->computeElementStiffness( (*_elementStiffnesses.beginEdit())[i], _materialsStiffnesses[i], deformed, i, _sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0 );


    Displacement F; //forces
    this->computeForce( F, D, _elementStiffnesses.getValue()[i] ); // compute force on element
    std::vector<Deriv> contrib;
    std::vector<unsigned int> indexList;
    contrib.resize(8);
    indexList.resize(8);
    for(int w=0; w<8; ++w){
        contrib[w] = _rotations[i].multTranspose( Deriv( F[w*3],  F[w*3+1],   F[w*3+2]  ) );
        indexList[w] = elem[w];
        if (!d_performECSW.getValue())
        {
            f[indexList[w]] += contrib[w];
        }
        else
        {
            f[indexList[w]] += weights(i)*contrib[w];
        }
    }
    this->template updateGie<DataTypes>(indexList, contrib, i);



    m_potentialEnergy += dot(Deriv( F[0], F[1], F[2] ) ,-Deriv( D[0], D[1], D[2]));
    m_potentialEnergy += dot(Deriv( F[3], F[4], F[5] ) ,-Deriv( D[3], D[4], D[5] ));
    m_potentialEnergy += dot(Deriv( F[6], F[7], F[8] ) ,-Deriv( D[6], D[7], D[8] ));
    m_potentialEnergy += dot(Deriv( F[9], F[10], F[11]),-Deriv( D[9], D[10], D[11] ));
    m_potentialEnergy += dot(Deriv( F[12], F[13], F[14]),-Deriv( D[12], D[13], D[14] ));
    m_potentialEnergy += dot(Deriv( F[15], F[16], F[17]),-Deriv( D[15], D[16], D[17] ));
    m_potentialEnergy += dot(Deriv( F[18], F[19], F[20]),-Deriv( D[18], D[19], D[20] ));
    m_potentialEnergy += dot(Deriv( F[21], F[22], F[23]),-Deriv( D[21], D[22], D[23] ));
}







/////////////////////////////////////////////////
/////////////////////////////////////////////////
/////////////////////////////////////////////////
////////////// polar decomposition method


template<class DataTypes>
        void HyperReducedHexahedronFEMForceField<DataTypes>::accumulateForcePolar( WDataRefVecDeriv &f, RDataRefVecCoord &p, sofa::Index i, const Element&elem )
{
    type::Vec<8,Coord> nodes;
    for(int j=0; j<8; ++j)
        nodes[j] = p[elem[j]];

// 	Transformation R_0_2; // Rotation matrix (deformed and displaced Tetrahedron/world)
    this->computeRotationPolar( _rotations[i], nodes );

// 	_rotations[i].transpose( R_0_2 );


    // positions of the deformed and displaced Tetrahedre in its frame
    type::Vec<8,Coord> deformed;
    for(int j=0; j<8; ++j)
        deformed[j] = _rotations[i] * nodes[j];



    // displacement
    Displacement D;
    for(int k=0 ; k<8 ; ++k )
    {
        int indice = k*3;
        for(int j=0 ; j<3 ; ++j )
            D[indice+j] = _rotatedInitialElements[i][k][j] - deformed[k][j];
    }

    //forces
    Displacement F;

    if(f_updateStiffnessMatrix.getValue())
// 		this->computeElementStiffness( _elementStiffnesses[i], _materialsStiffnesses[i], deformed );
        this->computeElementStiffness( (*_elementStiffnesses.beginEdit())[i], _materialsStiffnesses[i], deformed, i, _sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0);


    // compute force on element
    this->computeForce( F, D, _elementStiffnesses.getValue()[i] );


    for(int j=0; j<8; ++j)
            f[elem[j]] += _rotations[i].multTranspose( Deriv( F[j*3],  F[j*3+1],   F[j*3+2]  ) );

    m_potentialEnergy += dot(Deriv( F[0], F[1], F[2] ) ,-Deriv( D[0], D[1], D[2]));
    m_potentialEnergy += dot(Deriv( F[3], F[4], F[5] ) ,-Deriv( D[3], D[4], D[5] ));
    m_potentialEnergy += dot(Deriv( F[6], F[7], F[8] ) ,-Deriv( D[6], D[7], D[8] ));
    m_potentialEnergy += dot(Deriv( F[9], F[10], F[11]),-Deriv( D[9], D[10], D[11] ));
    m_potentialEnergy += dot(Deriv( F[12], F[13], F[14]),-Deriv( D[12], D[13], D[14] ));
    m_potentialEnergy += dot(Deriv( F[15], F[16], F[17]),-Deriv( D[15], D[16], D[17] ));
    m_potentialEnergy += dot(Deriv( F[18], F[19], F[20]),-Deriv( D[18], D[19], D[20] ));
    m_potentialEnergy += dot(Deriv( F[21], F[22], F[23]),-Deriv( D[21], D[22], D[23] ));
}



/////////////////////////////////////////////////
/////////////////////////////////////////////////
/////////////////////////////////////////////////


template <class DataTypes>
void HyperReducedHexahedronFEMForceField<DataTypes>::buildStiffnessMatrix(
    core::behavior::StiffnessMatrix* matrix)
{    
    sofa::Index e { 0 }; //index of the element in the topology

    constexpr auto S = DataTypes::deriv_total_size; // size of node blocks
    constexpr auto N = Element::size();

    const auto& stiffnesses = _elementStiffnesses.getValue();
    const auto* indexedElements = this->getIndexedElements();
    sofa::type::Mat<3, 3, Real> localMatrix(type::NOINIT);

    auto dfdx = matrix->getForceDerivativeIn(this->mstate)
                       .withRespectToPositionsIn(this->mstate);


    typename VecElement::const_iterator it, it0;

    it0 = indexedElements->begin();
    std::size_t nbElementsConsidered;

    if (!d_performECSW.getValue())
        nbElementsConsidered = indexedElements->size();
    else
        nbElementsConsidered = m_RIDsize;

    for(std::size_t numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
    {
        if (!d_performECSW.getValue()){
            e = numElem;
        }
        else
        {
            e = reducedIntegrationDomain(numElem);
        }


        it = it0 + e;
        const ElementStiffness &Ke = stiffnesses[e];
        const Transformation& Rot = this->getElementRotation(e);


        for ( Element::size_type n1=0; n1<N; n1++)
        {
            for (Element::size_type n2=0; n2<N; n2++)
            {
                localMatrix = Rot.multTranspose( Mat33(Coord(Ke[3*n1+0][3*n2+0],Ke[3*n1+0][3*n2+1],Ke[3*n1+0][3*n2+2]),
                        Coord(Ke[3*n1+1][3*n2+0],Ke[3*n1+1][3*n2+1],Ke[3*n1+1][3*n2+2]),
                        Coord(Ke[3*n1+2][3*n2+0],Ke[3*n1+2][3*n2+1],Ke[3*n1+2][3*n2+2])) ) * Rot;
                if (!d_performECSW.getValue())
                    dfdx((*it)[n1] * S, (*it)[n2] * S) += -localMatrix;
                else
                    dfdx((*it)[n1] * S, (*it)[n2] * S) += -localMatrix*weights(e);
            }
        }
    }
}


template<class DataTypes>
void HyperReducedHexahedronFEMForceField<DataTypes>::draw(const core::visual::VisualParams* vparams)
{
    if (!vparams->displayFlags().getShowForceFields()) return;
    if (!this->mstate) return;
    if (!f_drawing.getValue()) return;


    const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();

    if (vparams->displayFlags().getShowWireFrame())
        vparams->drawTool()->setPolygonMode(0,true);



    typename VecElement::const_iterator it, it0;
    int i;

    it0=this->getIndexedElements()->begin();
    size_t nbElementsConsidered;
    if (!d_performECSW.getValue())
        nbElementsConsidered = this->getIndexedElements()->size();
    else
        nbElementsConsidered = m_RIDsize;
    for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
    {
        if (!d_performECSW.getValue()){
            i = numElem;
        }
        else
        {
            i = reducedIntegrationDomain(numElem);
        }
        it = it0 + i;

        std::vector< type::Vec3 > points[6];

        Index a = (*it)[0];
        Index b = (*it)[1];
        Index d = (*it)[3];
        Index c = (*it)[2];
        Index e = (*it)[4];
        Index f = (*it)[5];
        Index h = (*it)[7];
        Index g = (*it)[6];

        Coord center = (x[a]+x[b]+x[c]+x[d]+x[e]+x[g]+x[f]+x[h])*0.125;
        Real percentage = f_drawPercentageOffset.getValue();
        Coord pa = x[a]-(x[a]-center)*percentage;
        Coord pb = x[b]-(x[b]-center)*percentage;
        Coord pc = x[c]-(x[c]-center)*percentage;
        Coord pd = x[d]-(x[d]-center)*percentage;
        Coord pe = x[e]-(x[e]-center)*percentage;
        Coord pf = x[f]-(x[f]-center)*percentage;
        Coord pg = x[g]-(x[g]-center)*percentage;
        Coord ph = x[h]-(x[h]-center)*percentage;


        if(_sparseGrid )
        {
            vparams->drawTool()->enableBlending();
        }

        points[0].push_back(pa);
        points[0].push_back(pb);
        points[0].push_back(pc);
        points[0].push_back(pa);
        points[0].push_back(pc);
        points[0].push_back(pd);

        points[1].push_back(pe);
        points[1].push_back(pf);
        points[1].push_back(pg);
        points[1].push_back(pe);
        points[1].push_back(pg);
        points[1].push_back(ph);

        points[2].push_back(pc);
        points[2].push_back(pd);
        points[2].push_back(ph);
        points[2].push_back(pc);
        points[2].push_back(ph);
        points[2].push_back(pg);

        points[3].push_back(pa);
        points[3].push_back(pb);
        points[3].push_back(pf);
        points[3].push_back(pa);
        points[3].push_back(pf);
        points[3].push_back(pe);

        points[4].push_back(pa);
        points[4].push_back(pd);
        points[4].push_back(ph);
        points[4].push_back(pa);
        points[4].push_back(ph);
        points[4].push_back(pe);

        points[5].push_back(pb);
        points[5].push_back(pc);
        points[5].push_back(pg);
        points[5].push_back(pb);
        points[5].push_back(pg);
        points[5].push_back(pf);


        vparams->drawTool()->setLightingEnabled(false);
        vparams->drawTool()->drawTriangles(points[0], type::RGBAColor(0.7f,0.7f,0.1f,(_sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0f)));
        vparams->drawTool()->drawTriangles(points[1], type::RGBAColor(0.7f,0.0f,0.0f,(_sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0f)));
        vparams->drawTool()->drawTriangles(points[2], type::RGBAColor(0.0f,0.7f,0.0f,(_sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0f)));
        vparams->drawTool()->drawTriangles(points[3], type::RGBAColor(0.0f,0.0f,0.7f,(_sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0f)));
        vparams->drawTool()->drawTriangles(points[4], type::RGBAColor(0.1f,0.7f,0.7f,(_sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0f)));
        vparams->drawTool()->drawTriangles(points[5], type::RGBAColor(0.7f,0.1f,0.7f,(_sparseGrid?_sparseGrid->getStiffnessCoef(i):1.0f)));

    }


    if (vparams->displayFlags().getShowWireFrame())
        vparams->drawTool()->setPolygonMode(0,false);

    if(_sparseGrid )
       vparams->drawTool()->disableBlending();
}


} // namespace sofa::component::forcefield
