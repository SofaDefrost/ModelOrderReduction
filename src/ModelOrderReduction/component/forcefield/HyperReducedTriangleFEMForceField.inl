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

#include <ModelOrderReduction/component/forcefield/HyperReducedTriangleFEMForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <sofa/gl/template.h>
#include <fstream> // for reading the file
#include <iostream> //for debugging
#include <vector>
#include <sofa/defaulttype/VecTypes.h>
#include <ModelOrderReduction/component/loader/MatrixLoader.h>

namespace sofa::component::solidmechanics::fem::elastic
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
        hyperReducedAccumulateForceLarge( f1, x1, true );
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
        hyperReducedApplyStiffnessLarge( df1, h, dx1, kFactor );
    }

    df.endEdit();
}


template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::hyperReducedAccumulateForceLarge(VecCoord& f, const VecCoord& p, bool implicit)
{
    typename VecElement::const_iterator it;
    unsigned int elementIndex(0);
    if (d_performECSW.getValue())
    {
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
void HyperReducedTriangleFEMForceField<DataTypes>::hyperReducedApplyStiffnessLarge(VecCoord &v, Real h, const VecCoord &x, const SReal &kFactor)
{
    unsigned int i;
    typename VecElement::const_iterator it, it0;

    it0=_indexedElements->begin();
    unsigned int nbElementsConsidered;
    const bool performECSW = d_performECSW.getValue();
    if (!performECSW)
    {
        nbElementsConsidered = _indexedElements->size();
    }
    else
    {
        nbElementsConsidered = m_RIDsize;
    }

    for( unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
    {
        if (!performECSW)
        {
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

        if (!performECSW)
        {
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

template <class DataTypes>
void HyperReducedTriangleFEMForceField<DataTypes>::buildStiffnessMatrix(core::behavior::StiffnessMatrix* matrix)
{
    StiffnessMatrix JKJt, RJKJtRt;
    sofa::type::Mat<3, 3, Real> localMatrix(type::NOINIT);

    constexpr auto S = DataTypes::deriv_total_size; // size of node blocks
    constexpr auto N = Element::size();

    auto dfdx = matrix->getForceDerivativeIn(this->mstate)
                    .withRespectToPositionsIn(this->mstate);

    sofa::Size triangleId = 0;

    typename VecElement::const_iterator it;
    auto it0=_indexedElements->begin();
    int nbElementsConsidered;

    const bool performECSW = d_performECSW.getValue();
    if (!performECSW)
        nbElementsConsidered = _indexedElements->size();
    else
        nbElementsConsidered = m_RIDsize;

    for(unsigned int numElem = 0 ; numElem<nbElementsConsidered ;++numElem)
    {
        if (!performECSW)
        {
            triangleId = numElem;
        }
        else
        {
            triangleId = reducedIntegrationDomain(numElem);
        }
        it = it0 + triangleId;

        this->computeElementStiffnessMatrix(JKJt, RJKJtRt, _materialsStiffnesses[triangleId], _strainDisplacements[triangleId], _rotations[triangleId]);

        for (sofa::Index n1 = 0; n1 < N; n1++)
        {
            for (sofa::Index n2 = 0; n2 < N; n2++)
            {
                RJKJtRt.getsub(S * n1, S * n2, localMatrix); //extract the submatrix corresponding to the coupling of nodes n1 and n2
                if (!performECSW)
                  dfdx((*it)[n1] * S, (*it)[n2] * S) += -localMatrix;
                else
                  dfdx((*it)[n1] * S, (*it)[n2] * S) += -localMatrix*weights(triangleId);

            }
        }
    }
}

} // namespace sofa::component::solidmechanics::fem::elastic
