/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, development version     *
*                (c) 2006-2015 INRIA, USTL, UJF, CNRS, MGH                    *
*                                                                             *
* This library is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This library is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this library; if not, write to the Free Software Foundation,     *
* Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.          *
*******************************************************************************
*                               SOFA :: Modules                               *
*                                                                             *
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
******************************************************************************/
#ifndef SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_H
#define SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_H
//#include "config.h"

#include <sofa/core/Mapping.h>
#include <SofaBaseLinearSolver/CompressedRowSparseMatrix.h>
#include <sofa/defaulttype/VecTypes.h>
#include <vector>
#include <sofa/core/topology/BaseMeshTopology.h>

#include <boost/scoped_ptr.hpp>

#include <SofaEigen2Solver/EigenSparseMatrix.h>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/State.h>
#include <sofa/core/objectmodel/DataFileName.h>

namespace sofa
{

namespace component
{

namespace mapping
{


/**
 *  \brief Component mapping state variables onto precomputed global basis vectors (aka: modes).
 *
 *  This maps vec1d MechanicalObjects to vec3d MechanicalObjects.
 *  Inputs:
 *      modesPath: Path to the text file containing the precomputed modes
 *      RIDpath: In case perfromECSW is true, path to the text file containing the reduced integration domain indices.
 *  The size of the "position" attribute will fix the number of modes used for the mapping
 */




template <class TIn, class TOut>
class ModelOrderReductionMapping : public core::Mapping<TIn, TOut>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE2(ModelOrderReductionMapping,TIn,TOut), SOFA_TEMPLATE2(core::Mapping,TIn,TOut));

    typedef core::Mapping<TIn, TOut> Inherit;
    typedef TIn In;
    typedef TOut Out;

    typedef typename In::Real			InReal;
    typedef typename In::VecCoord		InVecCoord;
    typedef typename In::VecDeriv		InVecDeriv;
    typedef typename In::Coord			InCoord;
    typedef typename In::Deriv			InDeriv;
    typedef typename In::MatrixDeriv	InMatrixDeriv;

    typedef typename Out::VecCoord		VecCoord;
    typedef typename Out::VecDeriv		VecDeriv;
    typedef typename Out::Coord			Coord;
    typedef typename Out::Deriv			Deriv;
    typedef typename Out::MatrixDeriv	MatrixDeriv;

    typedef Out OutDataTypes;
    typedef typename OutDataTypes::Real     OutReal;
    typedef typename OutDataTypes::VecCoord OutVecCoord;
    typedef typename OutDataTypes::VecDeriv OutVecDeriv;

    typedef typename Inherit::ForceMask ForceMask;
    typedef core::topology::BaseMeshTopology::index_type Index;
    typedef core::topology::BaseMeshTopology::Tetra Element;
    typedef core::topology::BaseMeshTopology::SeqTetrahedra VecElement;

    typedef linearsolver::EigenSparseMatrix<TIn, TOut> eigen_type;
    typedef helper::vector< defaulttype::BaseMatrix* > js_type;


    enum
    {
        N = OutDataTypes::spatial_dimensions
    };
    enum
    {
        NIn = sofa::defaulttype::DataTypeInfo<InDeriv>::Size
    };
    enum
    {
        NOut = sofa::defaulttype::DataTypeInfo<Deriv>::Size
    };

    typedef defaulttype::Mat<N, N, InReal> Mat;

protected:
    ModelOrderReductionMapping()
        : d_modesPath(initData(&d_modesPath,"modesPath","Path to the file containing the modes. REQUIRED"))
    {
        m_Js.resize( 1 );
        m_Js[0] = &m_J;
    }

    virtual ~ModelOrderReductionMapping()
    {
    }


public:
    /// Return true if the destination model has the same topology as the source model.
    ///
    /// This is the case for mapping keeping a one-to-one correspondance between
    /// input and output DOFs (mostly identity or data-conversion mappings).
    virtual bool sameTopology() const { return false; }

    void init();

    void apply(const core::MechanicalParams *mparams, Data<VecCoord>& out, const Data<InVecCoord>& in);

    void applyJ(const core::MechanicalParams *mparams, Data<VecDeriv>& out, const Data<InVecDeriv>& in);

    void applyJT(const core::MechanicalParams *mparams, Data<InVecDeriv>& out, const Data<VecDeriv>& in);

    void applyJT(const core::ConstraintParams *cparams, Data<InMatrixDeriv>& out, const Data<MatrixDeriv>& in);

    const sofa::defaulttype::BaseMatrix* getJ();



protected:

    Eigen::MatrixXd m_modesEigen;
    Eigen::MatrixXi m_listActiveNodes;

    eigen_type m_J;
    js_type m_Js;

    ////////////////////////// Inherited attributes ////////////////////////////
    /// https://gcc.gnu.org/onlinedocs/gcc/Name-lookup.html
    /// Bring inherited attributes and function in the current lookup context.
    /// otherwise any access to the base::attribute would require
    /// the "this->" approach.
    using core::Mapping<TIn, TOut>::fromModel ;
    using core::Mapping<TIn, TOut>::toModel ;

public:

    const js_type* getJs();

    sofa::core::objectmodel::DataFileName d_modesPath;

};


#if defined(SOFA_EXTERN_TEMPLATE) && !defined(SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_CPP)

#ifdef SOFA_WITH_DOUBLE
extern template class SOFA_BASE_MECHANICS_API ModelOrderReductionMapping< sofa::defaulttype::Vec1dTypes, sofa::defaulttype::Vec3dTypes >;
#endif

#ifdef SOFA_WITH_FLOAT
extern template class SOFA_BASE_MECHANICS_API ModelOrderReductionMapping< sofa::defaulttype::Vec1fTypes, sofa::defaulttype::Vec3fTypes >;
#endif


#endif

} // namespace mapping

} // namespace component


} // namespace sofa

#endif


