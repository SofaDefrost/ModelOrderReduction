/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, development version     *
*                (c) 2006-2018 INRIA, USTL, UJF, CNRS, MGH                    *
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
#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_H
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_H
//#include "config.h"
#include <SofaDeformable/config.h>
#include <sofa/defaulttype/RGBAColor.h>

#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/objectmodel/Data.h>
#include <sofa/helper/vector.h>
#include <SofaEigen2Solver/EigenSparseMatrix.h>
#include "HyperReducedForceField.h"
#include <SofaDeformable/RestShapeSpringsForceField.h>
namespace sofa
{
namespace core
{
namespace behavior
{
template< class T > class MechanicalState;

} // namespace behavior
} // namespace core
} // namespace sofa

namespace sofa
{

namespace component
{

namespace forcefield
{

/**
* @brief This class describes a simple elastic springs ForceField between DOFs positions and rest positions.
*
* Springs are applied to given degrees of freedom between their current positions and their rest shape positions.
* An external MechanicalState reference can also be passed to the ForceField as rest shape position.
*/
template<class DataTypes>
class HyperReducedRestShapeSpringsForceField : public HyperReducedForceField<DataTypes>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE(HyperReducedRestShapeSpringsForceField, DataTypes), SOFA_TEMPLATE(HyperReducedForceField, DataTypes));

    typedef HyperReducedForceField<DataTypes> Inherit;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::CPos CPos;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename DataTypes::Real Real;
    typedef helper::vector< unsigned int > VecIndex;
    typedef helper::vector< Real >	 VecReal;

    typedef core::objectmodel::Data<VecCoord> DataVecCoord;
    typedef core::objectmodel::Data<VecDeriv> DataVecDeriv;

    ////////////////////////// Inherited attributes ////////////////////////////
    /// https://gcc.gnu.org/onlinedocs/gcc/Name-lookup.html
    /// Bring inherited attributes and function in the current lookup context.
    /// otherwise any access to the base::attribute would require
    /// the "this->" approach.

    using HyperReducedForceField<DataTypes>::d_prepareECSW;
    using HyperReducedForceField<DataTypes>::d_nbModes;
    using HyperReducedForceField<DataTypes>::d_modesPath;
    using HyperReducedForceField<DataTypes>::d_nbTrainingSet;
    using HyperReducedForceField<DataTypes>::d_periodSaveGIE;

    using HyperReducedForceField<DataTypes>::d_performECSW;
    using HyperReducedForceField<DataTypes>::d_RIDPath;
    using HyperReducedForceField<DataTypes>::d_weightsPath;


    Data< helper::vector< unsigned int > > points; ///< points controlled by the rest shape springs
    Data< VecReal > stiffness; ///< stiffness values between the actual position and the rest shape position
    Data< VecReal > angularStiffness; ///< angularStiffness assigned when controlling the rotation of the points
    Data< helper::vector< CPos > > pivotPoints; ///< global pivot points used when translations instead of the rigid mass centers
    Data< helper::vector< unsigned int > > external_points; ///< points from the external Mechancial State that define the rest shape springs
    Data< bool > recompute_indices; ///< Recompute indices (should be false for BBOX)
    Data< bool > drawSpring; ///< draw Spring
    Data< defaulttype::RGBAColor > springColor; ///< spring color. (default=[0.0,1.0,0.0,1.0])

    SingleLink<HyperReducedRestShapeSpringsForceField<DataTypes>, sofa::core::behavior::MechanicalState< DataTypes >, BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> restMState;
    linearsolver::EigenBaseSparseMatrix<typename DataTypes::Real> matS;

//    // Reduced order model boolean parameters
//    Data< bool > d_prepareECSW;
//    Data<unsigned int> d_nbModes;
//    Data<unsigned int> d_nbTrainingSet;
//    Data<unsigned int> d_periodSaveGIE;

//    Data< bool > d_performECSW;
//    Data<std::string> d_modesPath;
//    Data<std::string> d_RIDPath;
//    Data<std::string> d_weightsPath;


protected:
    HyperReducedRestShapeSpringsForceField();

public:
    /// BaseObject initialization method.
    void bwdInit() override ;
    virtual void parse(core::objectmodel::BaseObjectDescription *arg) override ;
    virtual void reinit() override ;
    virtual void init() override ;


    /// Add the forces.
    virtual void addForce(const core::MechanicalParams* mparams, DataVecDeriv& f, const DataVecCoord& x, const DataVecDeriv& v) override;

    virtual void addDForce(const core::MechanicalParams* mparams, DataVecDeriv& df, const DataVecDeriv& dx) override;

    virtual SReal getPotentialEnergy(const core::MechanicalParams* mparams, const DataVecCoord& x) const override
    {
        SOFA_UNUSED(mparams);
        SOFA_UNUSED(x);

        msg_error() << "Get potentialEnergy not implemented";
        return 0.0;
    }

    /// Brings ForceField contribution to the global system stiffness matrix.
    virtual void addKToMatrix(const core::MechanicalParams* mparams, const sofa::core::behavior::MultiMatrixAccessor* matrix ) override;

    virtual void addSubKToMatrix(const core::MechanicalParams* mparams, const sofa::core::behavior::MultiMatrixAccessor* matrix, const helper::vector<unsigned> & addSubIndex ) override;

    virtual void draw(const core::visual::VisualParams* vparams) override;


    const DataVecCoord* getExtPosition() const;
    const VecIndex& getIndices() const { return m_indices; }
    const VecIndex& getExtIndices() const { return (useRestMState ? m_ext_indices : m_indices); }

    virtual void updateForceMask() override;

protected :

    void recomputeIndices();

    VecIndex m_indices;
    VecReal k;
    VecIndex m_ext_indices;
    helper::vector<CPos> m_pivots;

    SReal lastUpdatedStep;

    // Reduced order model variables
    Eigen::MatrixXd m_modes;
    std::vector<std::vector<double> > Gie;
    Eigen::VectorXd weights;
    Eigen::VectorXi reducedIntegrationDomain;
    unsigned int m_RIDsize;


private :

    bool useRestMState; /// An external MechanicalState is used as rest reference.
};

#if !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGSFORCEFIELD_CPP)

#ifndef SOFA_FLOAT
extern template class SOFA_DEFORMABLE_API HyperReducedRestShapeSpringsForceField<sofa::defaulttype::Vec3dTypes>;
#endif
#ifndef SOFA_DOUBLE
extern template class SOFA_DEFORMABLE_API HyperReducedRestShapeSpringsForceField<sofa::defaulttype::Vec3fTypes>;
#endif

#endif

} // namespace forcefield

} // namespace component

} // namespace sofa

#endif // SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDRESTSHAPESPRINGFORCEFIELD_H
