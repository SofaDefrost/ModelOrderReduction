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
#include <ModelOrderReduction/config.h>

#include <ModelOrderReduction/component/forcefield/HyperReducedHelper.h>
#include <sofa/component/solidmechanics/fem/elastic/HexahedronFEMForceField.h>

namespace sofa::component::forcefield
{

using namespace solidmechanics::fem::elastic;

/** This forceField is the HyperReduced version of HexahedronFEMForceField.
*   At the moment, it is only implemented for the "large" method (i.e not for small, polar or svd).
*/
template<class DataTypes>
class HyperReducedHexahedronFEMForceField : public virtual HexahedronFEMForceField<DataTypes>, public modelorderreduction::HyperReducedHelper
{
public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedHexahedronFEMForceField, DataTypes), SOFA_TEMPLATE(HexahedronFEMForceField, DataTypes), HyperReducedHelper);

    typedef typename core::behavior::ForceField<DataTypes> InheritForceField;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef VecCoord Vector;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename Coord::value_type Real;
    typedef core::objectmodel::Data<VecDeriv> DataVecDeriv;
    typedef core::objectmodel::Data<VecCoord> DataVecCoord;
    typedef helper::ReadAccessor< Data< VecCoord > > RDataRefVecCoord;
    typedef helper::WriteAccessor< Data< VecDeriv > > WDataRefVecDeriv;

    typedef sofa::Index Index;
    typedef core::topology::BaseMeshTopology::Hexa Element;
    typedef core::topology::BaseMeshTopology::SeqHexahedra VecElement;

    enum
    {
        LARGE = 0,   ///< Symbol of mean large displacements tetrahedron solver (frame = edges mean on the 3 directions)
        POLAR = 1,   ///< Symbol of polar displacements tetrahedron solver
        SMALL = 2,
    };



protected:

    typedef type::Vec<24, Real> Displacement;		///< the displacement vector

    typedef type::Mat<6, 6, Real> MaterialStiffness;	///< the matrix of material stiffness
    typedef type::vector<MaterialStiffness> VecMaterialStiffness;         ///< a vector of material stiffness matrices
    VecMaterialStiffness _materialsStiffnesses;					///< the material stiffness matrices vector

    typedef type::Mat<24, 24, Real> ElementStiffness;
    typedef type::vector<ElementStiffness> VecElementStiffness;
    using HexahedronFEMForceField<DataTypes>::_elementStiffnesses; ///< Stiffness matrices per element (K_i)

    typedef type::Mat<3, 3, Real> Mat33;


    typedef std::pair<int,Real> Col_Value;
    typedef type::vector< Col_Value > CompressedValue;
    typedef type::vector< CompressedValue > CompressedMatrix;
    using HexahedronFEMForceField<DataTypes>::_stiffnesses;
    using HexahedronFEMForceField<DataTypes>::m_potentialEnergy;


    using HexahedronFEMForceField<DataTypes>::m_topology;
    using HexahedronFEMForceField<DataTypes>::_sparseGrid;
    using HexahedronFEMForceField<DataTypes>::_initialPoints; ///< the intial positions of the points


    using HexahedronFEMForceField<DataTypes>::_coef; ///< coef of each vertices to compute the strain stress matrix
    using HexahedronFEMForceField<DataTypes>::data;

public:


    typedef Mat33 Transformation; ///< matrix for rigid transformations like rotations

    // Inherited ForceField Variables

    using HexahedronFEMForceField<DataTypes>::method;
    using HexahedronFEMForceField<DataTypes>::f_method; ///< the computation method of the displacements
    using HexahedronFEMForceField<DataTypes>::f_poissonRatio;
    using HexahedronFEMForceField<DataTypes>::f_youngModulus;
    using HexahedronFEMForceField<DataTypes>::f_updateStiffnessMatrix;
    using HexahedronFEMForceField<DataTypes>::_gatherPt; ///< use in GPU version
    using HexahedronFEMForceField<DataTypes>::_gatherBsize; ///< use in GPU version
    using HexahedronFEMForceField<DataTypes>::f_drawing; ///<  draw the forcefield if true
    using HexahedronFEMForceField<DataTypes>::f_drawPercentageOffset; ///< size of the hexa
    using HexahedronFEMForceField<DataTypes>::needUpdateTopology;

    // Reduced Order Variables

    using HyperReducedHelper::d_prepareECSW;
    using HyperReducedHelper::d_nbModes;
    using HyperReducedHelper::d_modesPath;
    using HyperReducedHelper::d_nbTrainingSet;
    using HyperReducedHelper::d_periodSaveGIE;

    using HyperReducedHelper::d_performECSW;
    using HyperReducedHelper::d_RIDPath;
    using HyperReducedHelper::d_weightsPath;

    using HyperReducedHelper::Gie;
    using HyperReducedHelper::weights;
    using HyperReducedHelper::reducedIntegrationDomain;

    using HyperReducedHelper::m_modes;
    using HyperReducedHelper::m_RIDsize;


protected:
    HyperReducedHexahedronFEMForceField()
        : HexahedronFEMForceField<DataTypes>()
    {
    }
public:
    virtual void init() override;

    virtual void addForce (const core::MechanicalParams* mparams, DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv& v) override;

    virtual void addDForce (const core::MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx) override;

    // Make other overloaded version of getPotentialEnergy() to show up in subclass.
    using InheritForceField::getPotentialEnergy;
    // getPotentialEnergy is implemented for polar method

    void buildStiffnessMatrix(core::behavior::StiffnessMatrix* /* matrix */) override;

    void draw(const core::visual::VisualParams* vparams) override;

protected:


    inline const VecElement *getIndexedElements()
    {
        return & (m_topology->getHexahedra());
    }


    ////////////// large displacements method
    using HexahedronFEMForceField<DataTypes>::_rotatedInitialElements;   ///< The initials positions in its frame
    using HexahedronFEMForceField<DataTypes>::_rotations;
    using HexahedronFEMForceField<DataTypes>::_initialrotations;
    virtual void accumulateForceLarge( WDataRefVecDeriv &f, RDataRefVecCoord &p, sofa::Index i, const Element&elem ) override;

    ////////////// polar decomposition method
    virtual void accumulateForcePolar( WDataRefVecDeriv &f, RDataRefVecCoord &p, sofa::Index i, const Element&elem ) override;

    ////////////// small decomposition method
    virtual void accumulateForceSmall( WDataRefVecDeriv &f, RDataRefVecCoord &p, sofa::Index i, const Element&elem ) override;

    using HexahedronFEMForceField<DataTypes>::_alreadyInit;
};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDHEXAHEDRONFEMFORCEFIELD_CPP)
extern template class SOFA_MODELORDERREDUCTION_API HyperReducedHexahedronFEMForceField<defaulttype::Vec3Types>;
#endif
} // namespace sofa::component::forcefield
