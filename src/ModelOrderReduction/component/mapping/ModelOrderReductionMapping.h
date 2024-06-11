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
#ifndef SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_H
#define SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_H
#include <ModelOrderReduction/config.h>

#include <vector>

#include <sofa/linearalgebra/CompressedRowSparseMatrix.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/core/topology/BaseMeshTopology.h>

#include <boost/scoped_ptr.hpp>
#include <sofa/component/mapping/linear/LinearMapping.h>

#include <sofa/linearalgebra/EigenSparseMatrix.h>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/State.h>
#include <sofa/core/objectmodel/DataFileName.h>
#include <sofa/core/Mapping.h>

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
class ModelOrderReductionMapping : public linear::LinearMapping<TIn, TOut>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE2(ModelOrderReductionMapping,TIn,TOut), SOFA_TEMPLATE2(linear::LinearMapping,TIn,TOut));

    typedef linear::LinearMapping<TIn, TOut> Inherit;
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

    typedef type::Vec3 Vector3;

    typedef sofa::Index Index;
    typedef core::topology::BaseMeshTopology::Tetra Element;
    typedef core::topology::BaseMeshTopology::SeqTetrahedra VecElement;

    typedef sofa::linearalgebra::EigenSparseMatrix<TIn, TOut> eigen_type;
    typedef type::vector< linearalgebra::BaseMatrix* > js_type;


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

    typedef type::Mat<N, N, InReal> Mat;

protected:
    ModelOrderReductionMapping()
        : d_rotation(initData(&d_rotation,"rotation","Rotation of the modes"))
        , d_modesPath(initData(&d_modesPath,"modesPath","Path to the file containing the modes. REQUIRED"))

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
    virtual bool sameTopology() const override { return false; }

    void init() override;

    void applyRotation(const SReal rx, const SReal ry, const SReal rz);

    void applyRotation(const type::Quat<SReal>& q);

    void apply(const core::MechanicalParams *mparams, Data<VecCoord>& out, const Data<InVecCoord>& in) override;

    void applyJ(const core::MechanicalParams *mparams, Data<VecDeriv>& out, const Data<InVecDeriv>& in) override;

    void applyJT(const core::MechanicalParams *mparams, Data<InVecDeriv>& out, const Data<VecDeriv>& in) override;

    void applyJT(const core::ConstraintParams *cparams, Data<InMatrixDeriv>& out, const Data<MatrixDeriv>& in) override;

    const sofa::linearalgebra::BaseMatrix* getJ() override;



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

    friend core::Mapping<TIn, TOut>;

    Data<Vector3> d_rotation;

public:

    const js_type* getJs() override;

    sofa::core::objectmodel::DataFileName d_modesPath;

};


#if !defined(SOFA_COMPONENT_MAPPING_MODELORDERREDUCTIONMAPPING_CPP)
extern template class SOFA_MODELORDERREDUCTION_API ModelOrderReductionMapping< sofa::defaulttype::Vec1Types, sofa::defaulttype::Vec3Types >;
#endif

} // namespace mapping

} // namespace component


} // namespace sofa

#endif


