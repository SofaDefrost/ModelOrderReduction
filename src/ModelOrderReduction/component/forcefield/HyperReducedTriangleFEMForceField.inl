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
#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTRIANGLEFEMFORCEFIELD_INL
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTRIANGLEFEMFORCEFIELD_INL

#include "HyperReducedTriangleFEMForceField.h"
#include <sofa/core/visual/VisualParams.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <sofa/gl/template.h>
#include <fstream> // for reading the file
#include <iostream> //for debugging
#include <vector>
#include <sofa/defaulttype/VecTypes.h>
#include "../loader/MatrixLoader.h"

//#include "config.h"

// #define DEBUG_TRIANGLEFEM

namespace sofa
{

namespace component
{

namespace forcefield
{

using sofa::component::loader::MatrixLoader;


template <class DataTypes>
HyperReducedTriangleFEMForceField<DataTypes>::
HyperReducedTriangleFEMForceField()
{}

template <class DataTypes>
HyperReducedTriangleFEMForceField<DataTypes>::~HyperReducedTriangleFEMForceField()
{
    f_poisson.setRequired(true);
    f_young.setRequired(true);
}

template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::init()
{
    TriangleFEMForceField<DataTypes>::init();
    this->initMOR(_indexedElements->size(),notMuted());
}


template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::addForce(const core::MechanicalParams* /* mparams */, DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv& /* v */)
{
    VecDeriv& f1 = *f.beginEdit();
    const VecCoord& x1 = x.getValue();

    f1.resize(x1.size());

    if(method==SMALL)
    {
        this->accumulateForceSmall( f1, x1, true );
    }
    else
    {
        accumulateForceLarge( f1, x1, true );
    }
    f.endEdit();
    this->saveGieFile(this->_indexedElements->size());
}

template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::addDForce(const core::MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx)
{
    VecDeriv& df1 = *df.beginEdit();
    const VecDeriv& dx1 = dx.getValue();
    Real kFactor = (Real)mparams->kFactorIncludingRayleighDamping(this->rayleighStiffness.getValue());

    Real h=1;
    df1.resize(dx1.size());

    if (method == SMALL)
    {
        this->applyStiffnessSmall( df1, h, dx1, kFactor );
    }
    else
    {
        applyStiffnessLarge( df1, h, dx1, kFactor );
    }

    df.endEdit();
}



//template <class DataTypes>
//void HyperReducedTriangleFEMForceField<DataTypes>::accumulateForceSmall( VecCoord &f, const VecCoord &p, bool implicit )
//{
//    typename VecElement::const_iterator it;
//    unsigned int elementIndex(0);
//    for (it = _indexedElements->begin(); it != _indexedElements->end(); ++it, ++elementIndex)
//    {
//        Index a = (*_indexedElements)[elementIndex][0];
//        Index b = (*_indexedElements)[elementIndex][1];
//        Index c = (*_indexedElements)[elementIndex][2];

//        Coord deforme_a, deforme_b, deforme_c;
//        deforme_b = p[b]-p[a];
//        deforme_c = p[c]-p[a];
//        deforme_a = Coord(0,0,0);

//        // displacements
//        Displacement D;
//        D[0] = 0;
//        D[1] = 0;
//        D[2] = (_initialPoints.getValue()[b][0]-_initialPoints.getValue()[a][0]) - deforme_b[0];
//        D[3] = 0;
//        D[4] = (_initialPoints.getValue()[c][0]-_initialPoints.getValue()[a][0]) - deforme_c[0];
//        D[5] = (_initialPoints.getValue()[c][1]-_initialPoints.getValue()[a][1]) - deforme_c[1];


//        StrainDisplacement J;
//        //this->computeStrainDisplacement(J,deforme_a,deforme_b,deforme_c);
//        this->m_triangleUtils.computeStrainDisplacementGlobal(J,deforme_a,deforme_b,deforme_c);
//        if (implicit)
//            _strainDisplacements[elementIndex] = J;

//        // compute force on element
//        Displacement F;
//        //this->computeForce( F, D, _materialsStiffnesses[elementIndex], J );
//        this->m_triangleUtils.computeForceLarge( F, J, _materialsStiffnesses[elementIndex], J );

//        f[a] += Coord( F[0], F[1], 0);
//        f[b] += Coord( F[2], F[3], 0);
//        f[c] += Coord( F[4], F[5], 0);
//    }
//}

//template <class DataTypes>
//void HyperReducedTriangleFEMForceField<DataTypes>::applyStiffnessSmall(VecCoord &v, Real h, const VecCoord &x, const SReal &kFactor)
//{

//    typename VecElement::const_iterator it;
//    unsigned int i(0);

//    for(it = _indexedElements->begin() ; it != _indexedElements->end() ; ++it, ++i)
//    {
//        Index a = (*it)[0];
//        Index b = (*it)[1];
//        Index c = (*it)[2];

//        Displacement X;

//        X[0] = x[a][0];
//        X[1] = x[a][1];

//        X[2] = x[b][0];
//        X[3] = x[b][1];

//        X[4] = x[c][0];
//        X[5] = x[c][1];

//        Displacement F;
//        this->computeForce( F, X, _materialsStiffnesses[i], _strainDisplacements[i] );

//        v[a] += Coord(-h*F[0], -h*F[1], 0)*kFactor;
//        v[b] += Coord(-h*F[2], -h*F[3], 0)*kFactor;
//        v[c] += Coord(-h*F[4], -h*F[5], 0)*kFactor;
//    }
//}


template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::accumulateForceLarge(VecCoord& f, const VecCoord& p, bool implicit)
{

    typename VecElement::const_iterator it;
    unsigned int elementIndex(0);
    if (d_performECSW.getValue()){
        for( elementIndex = 0 ; elementIndex<m_RIDsize ;++elementIndex)
        {
            // triangle vertex indices
            const Index a = (*_indexedElements)[elementIndex][0];
            const Index b = (*_indexedElements)[elementIndex][1];
            const Index c = (*_indexedElements)[elementIndex][2];

            const Coord& pA = p[a];
            const Coord& pB = p[b];
            const Coord& pC = p[c];

            // Rotation matrix (deformed and displaced Triangle/world)
            Transformation R_2_0(type::NOINIT), R_0_2(type::NOINIT);
            this->m_triangleUtils.computeRotationLarge(R_0_2, pA, pB, pC);

            // positions of the deformed points in the local frame
            const Coord deforme_b = R_0_2 * (pB - pA);
            const Coord deforme_c = R_0_2 * (pC - pA);

            // displacements in the local frame
            Displacement Depl(type::NOINIT);
            this->m_triangleUtils.computeDisplacementLarge(Depl, R_0_2, _rotatedInitialElements[elementIndex], pA, pB, pC);

            // Strain-displacement matrix
            StrainDisplacement J(type::NOINIT);
            try
            {
                this->m_triangleUtils.computeStrainDisplacementLocal(J, deforme_b, deforme_c);
            }
            catch (const std::exception& e)
            {
                msg_error() << e.what();
                sofa::core::objectmodel::BaseObject::d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
                break;
            }

            // compute strain
            type::Vec<3, Real> strain(type::NOINIT);
            this->m_triangleUtils.computeStrain(strain, J, Depl, false);

            // compute stress
            type::Vec<3, Real> stress(type::NOINIT);
            this->m_triangleUtils.computeStress(stress, _materialsStiffnesses[elementIndex], strain, false);

            // compute force on element, in local frame
            Displacement F(type::NOINIT);
            this->m_triangleUtils.computeForceLarge(F, J, stress);

            // project forces to world frame
            R_2_0.transpose(R_0_2);
            std::vector<Deriv> contrib;
            std::vector<unsigned int> indexList;
            contrib.resize(3);
            indexList.resize(3);
            contrib[0] = R_2_0 * Coord(F[0], F[1], 0);
            contrib[1] = R_2_0 * Coord(F[2], F[3], 0);
            contrib[2] = R_2_0 * Coord(F[4], F[5], 0);
            indexList[0] = a;
            indexList[1] = b;
            indexList[2] = c;
            for (auto i : {0,1,2})
                f[indexList[i]] += weights(elementIndex)*contrib[i];

            // store for re-use in matrix-vector products
            if(implicit)
            {
                _strainDisplacements[elementIndex] = J;
                _rotations[elementIndex] = R_2_0 ;
            }
        }
    }
    else
    {
        for(it = _indexedElements->begin() ; it != _indexedElements->end() ; ++it, ++elementIndex)
        {
            // triangle vertex indices
            const Index a = (*_indexedElements)[elementIndex][0];
            const Index b = (*_indexedElements)[elementIndex][1];
            const Index c = (*_indexedElements)[elementIndex][2];

            const Coord& pA = p[a];
            const Coord& pB = p[b];
            const Coord& pC = p[c];

            // Rotation matrix (deformed and displaced Triangle/world)
            Transformation R_2_0(type::NOINIT), R_0_2(type::NOINIT);
            this->m_triangleUtils.computeRotationLarge(R_0_2, pA, pB, pC);

            // positions of the deformed points in the local frame
            const Coord deforme_b = R_0_2 * (pB - pA);
            const Coord deforme_c = R_0_2 * (pC - pA);

            // displacements in the local frame
            Displacement Depl(type::NOINIT);
            this->m_triangleUtils.computeDisplacementLarge(Depl, R_0_2, _rotatedInitialElements[elementIndex], pA, pB, pC);

            // Strain-displacement matrix
            StrainDisplacement J(type::NOINIT);
            try
            {
                this->m_triangleUtils.computeStrainDisplacementLocal(J, deforme_b, deforme_c);
            }
            catch (const std::exception& e)
            {
                msg_error() << e.what();
                sofa::core::objectmodel::BaseObject::d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
                break;
            }

            // compute strain
            type::Vec<3, Real> strain(type::NOINIT);
            this->m_triangleUtils.computeStrain(strain, J, Depl, false);

            // compute stress
            type::Vec<3, Real> stress(type::NOINIT);
            this->m_triangleUtils.computeStress(stress, _materialsStiffnesses[elementIndex], strain, false);

            // compute force on element, in local frame
            Displacement F(type::NOINIT);
            this->m_triangleUtils.computeForceLarge(F, J, stress);

            // project forces to world frame
            R_2_0.transpose(R_0_2);
            std::vector<Deriv> contrib;
            std::vector<unsigned int> indexList;
            contrib.resize(3);
            indexList.resize(3);
            contrib[0] = R_2_0 * Coord(F[0], F[1], 0);
            contrib[1] = R_2_0 * Coord(F[2], F[3], 0);
            contrib[2] = R_2_0 * Coord(F[4], F[5], 0);
            indexList[0] = a;
            indexList[1] = b;
            indexList[2] = c;
            for (auto i : {0,1,2})
                f[indexList[i]] += contrib[i];

            this->template updateGie<DataTypes>(indexList, contrib, elementIndex);

            // store for re-use in matrix-vector products
            if(implicit)
            {
                _strainDisplacements[elementIndex] = J;
                _rotations[elementIndex] = R_2_0 ;
            }
        }
    }


}


template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::applyStiffnessLarge(VecCoord &v, Real h, const VecCoord &x, const SReal &kFactor)
{
    unsigned int i;
    typename VecElement::const_iterator it, it0;

    it0=_indexedElements->begin();
    unsigned int nbElementsConsidered;
    if (!d_performECSW.getValue()){
        nbElementsConsidered = _indexedElements->size();
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

        Index a = (*it)[0];
        Index b = (*it)[1];
        Index c = (*it)[2];

        Transformation R_0_2(type::NOINIT);
        R_0_2.transpose(_rotations[i]);

        Displacement dX(type::NOINIT);

        Coord x_2 = R_0_2 * x[a];
        dX[0] = x_2[0];
        dX[1] = x_2[1];

        x_2 = R_0_2 * x[b];
        dX[2] = x_2[0];
        dX[3] = x_2[1];

        x_2 = R_0_2 * x[c];
        dX[4] = x_2[0];
        dX[5] = x_2[1];

        // compute strain
        type::Vec<3, Real> strain(type::NOINIT);
        this->m_triangleUtils.computeStrain(strain, _strainDisplacements[i], dX, false);

        // compute stress
        type::Vec<3, Real> stress(type::NOINIT);
        this->m_triangleUtils.computeStress(stress, _materialsStiffnesses[i], strain, false);

        // compute force on element, in local frame
        Displacement F(type::NOINIT);
        this->m_triangleUtils.computeForceLarge(F, _strainDisplacements[i], stress);

        if (!d_performECSW.getValue()){
            v[a] += (_rotations[i] * Coord(-h * F[0], -h * F[1], 0)) * kFactor;
            v[b] += (_rotations[i] * Coord(-h * F[2], -h * F[3], 0)) * kFactor;
            v[c] += (_rotations[i] * Coord(-h * F[4], -h * F[5], 0)) * kFactor;
        }
        else
        {
            v[a] += weights(i) * (_rotations[i] * Coord(-h * F[0], -h * F[1], 0)) * kFactor;
            v[b] += weights(i) * (_rotations[i] * Coord(-h * F[2], -h * F[3], 0)) * kFactor;
            v[c] += weights(i) * (_rotations[i] * Coord(-h * F[4], -h * F[5], 0)) * kFactor;
        }
    }


}

template<class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::draw(const core::visual::VisualParams* vparams)
{
#ifndef SOFA_NO_OPENGL
    if (!vparams->displayFlags().getShowForceFields())
        return;
    //     if (!this->_object)
    //         return;

    if (vparams->displayFlags().getShowWireFrame())
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);

    const VecCoord& x = this->mstate->read(core::ConstVecCoordId::position())->getValue();

    glDisable(GL_LIGHTING);

    glBegin(GL_TRIANGLES);
    typename VecElement::const_iterator it, it0;
    it0 = _indexedElements->begin();
    for(unsigned i = 0 ; i<m_RIDsize ;++i)
    {
        it = it0 + reducedIntegrationDomain(i);
        Index a = (*it)[0];
        Index b = (*it)[1];
        Index c = (*it)[2];

        glColor4f(0,1,0,1);
        gl::glVertexT(x[a]);
        glColor4f(0,0.5,0.5,1);
        gl::glVertexT(x[b]);
        glColor4f(0,0,1,1);
        gl::glVertexT(x[c]);
    }
    glEnd();

    if (vparams->displayFlags().getShowWireFrame())
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
#endif /* SOFA_NO_OPENGL */
}


template<class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::addKToMatrix(sofa::linearalgebra::BaseMatrix *mat, SReal k, unsigned int &offset)
{
    if (d_performECSW.getValue())
    {
        int iECSW;
        for(unsigned i = 0 ; i<m_RIDsize ;++i)
        {
            iECSW = reducedIntegrationDomain(i);
            StiffnessMatrix JKJt,RJKJtRt;
            this->computeElementStiffnessMatrix(JKJt, RJKJtRt, _materialsStiffnesses[iECSW], _strainDisplacements[iECSW], _rotations[iECSW]);
            this->addToMatrix(mat,offset,(*_indexedElements)[iECSW],weights(iECSW)*RJKJtRt,-k);

        }
    }
    else
    {
        for(unsigned i=0; i< _indexedElements->size() ; i++)
        {
            StiffnessMatrix JKJt,RJKJtRt;
            this->computeElementStiffnessMatrix(JKJt, RJKJtRt, _materialsStiffnesses[i], _strainDisplacements[i], _rotations[i]);
            this->addToMatrix(mat,offset,(*_indexedElements)[i],RJKJtRt,-k);
        }
    }
}


} // namespace forcefield

} // namespace component

} // namespace sofa

#endif // #ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTRIANGLEFEMFORCEFIELD_INL
