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
#include <sofa/component/solidmechanics/fem/elastic/TriangleFEMForceField.h>


// corotational triangle from
// @InProceedings{NPF05,
//   author       = "Nesme, Matthieu and Payan, Yohan and Faure, Fran\c{c}ois",
//   title        = "Efficient, Physically Plausible Finite Elements",
//   booktitle    = "Eurographics (short papers)",
//   month        = "august",
//   year         = "2005",
//   editor       = "J. Dingliana and F. Ganovelli",
//   keywords     = "animation, physical model, elasticity, finite elements",
//   url          = "http://www-evasion.imag.fr/Publications/2005/NPF05"
// }


namespace sofa::component::solidmechanics::fem::elastic
{


/** Triangle FEM force field using the QR decomposition of the deformation gradient, inspired from http://www-evasion.imag.fr/Publications/2005/NPF05 , to handle large displacements.
  The material properties are uniform across the domain.
  Two methods are proposed, one for small displacements and one for large displacements.
  The method for small displacements has not been validated and we suspect that it is broke. Use it very carefully, and compare with the method for large displacements.
  */
template<class DataTypes>
class HyperReducedTriangleFEMForceField : public virtual TriangleFEMForceField<DataTypes>, public modelorderreduction::HyperReducedHelper
{
public:
    SOFA_CLASS2(SOFA_TEMPLATE(HyperReducedTriangleFEMForceField, DataTypes), SOFA_TEMPLATE(TriangleFEMForceField, DataTypes),HyperReducedHelper);

    typedef core::behavior::ForceField<DataTypes> Inherited;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::Coord    Coord   ;
    typedef typename DataTypes::Deriv    Deriv   ;
    typedef typename Coord::value_type   Real    ;

    typedef core::objectmodel::Data<VecCoord> DataVecCoord;
    typedef core::objectmodel::Data<VecDeriv> DataVecDeriv;

    typedef sofa::Index Index;
    typedef sofa::core::topology::BaseMeshTopology::Triangle Element;
    typedef sofa::core::topology::BaseMeshTopology::SeqTriangles VecElement;

    static const int SMALL = 1;										///< Symbol of small displacements triangle solver
    static const int LARGE = 0;										///< Symbol of large displacements triangle solver

protected:
    typedef type::Vec<6, Real> Displacement;								///< the displacement vector

    typedef type::Mat<3, 3, Real> MaterialStiffness;						///< the matrix of material stiffness
    typedef sofa::type::vector<MaterialStiffness> VecMaterialStiffness;    ///< a vector of material stiffness matrices
    using TriangleFEMForceField<DataTypes>::_materialsStiffnesses;						///< the material stiffness matrices vector

    typedef type::Mat<6, 3, Real> StrainDisplacement;						///< the strain-displacement matrix (the transpose, actually)
    typedef sofa::type::vector<StrainDisplacement> VecStrainDisplacement;	///< a vector of strain-displacement matrices
    using TriangleFEMForceField<DataTypes>::_strainDisplacements;						///< the strain-displacement matrices vector

    typedef type::Mat<3, 3, Real > Transformation;						///< matrix for rigid transformations like rotations

    /// Stiffness matrix ( = RJKJtRt  with K the Material stiffness matrix, J the strain-displacement matrix, and R the transformation matrix if any )
    typedef type::Mat<9, 9, Real> StiffnessMatrix;


    using TriangleFEMForceField<DataTypes>::m_topology;
    using TriangleFEMForceField<DataTypes>::_indexedElements;
    using TriangleFEMForceField<DataTypes>::_initialPoints; ///< the intial positions of the points
    using TriangleFEMForceField<DataTypes>::_rotatedInitialElements;   ///< The initials positions in its frame
    using TriangleFEMForceField<DataTypes>::_rotations;


    HyperReducedTriangleFEMForceField();
    virtual ~HyperReducedTriangleFEMForceField();


public:

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


    void init() override;
    void addForce(const core::MechanicalParams* mparams, DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv& v) override;
    void addDForce(const core::MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx) override;
    SReal getPotentialEnergy(const core::MechanicalParams* /*mparams*/, const DataVecCoord&  /* x */) const override
    {
        msg_error() << "Get potentialEnergy not implemented";
        return 0.0;
    }

    void draw(const core::visual::VisualParams* vparams) override;

    using TriangleFEMForceField<DataTypes>::method;
    using TriangleFEMForceField<DataTypes>::f_method; ///< Choice of method: 0 for small, 1 for large displacements
    using TriangleFEMForceField<DataTypes>::f_poisson;       ///< Poisson ratio of the material
    using TriangleFEMForceField<DataTypes>::f_young;         ///< Young modulus of the material
    using TriangleFEMForceField<DataTypes>::f_thickness;     ///< Thickness of the elements
    using TriangleFEMForceField<DataTypes>::f_planeStrain; ///< compute material stiffness corresponding to the plane strain assumption, or to the plane stress otherwise.

protected :

    ////////////// large displacements method
    void hyperReducedAccumulateForceLarge( VecCoord& f, const VecCoord & p, bool implicit=false );
    void hyperReducedApplyStiffnessLarge( VecCoord& f, Real h, const VecCoord& x, const SReal &kFactor );

    //// stiffness matrix assembly
    void buildStiffnessMatrix(core::behavior::StiffnessMatrix* matrix) override;

};


#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTRIANGLEFEMFORCEFIELD_CPP)
extern template class SOFA_MODELORDERREDUCTION_API HyperReducedTriangleFEMForceField<sofa::defaulttype::Vec3Types>;
#endif // !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTRIANGLEFEMFORCEFIELD_CPP)
} // namespace sofa::component::solidmechanics::fem::elastic
