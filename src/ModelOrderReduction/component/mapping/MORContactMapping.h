/******************************************************************************
*       SOFA, Simulation Open-Framework Architecture, development version     *
*                (c) 2006-2019 INRIA, USTL, UJF, CNRS, MGH                    *
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
#ifndef SOFA_COMPONENT_MAPPING_MORCONTACTMAPPING_H
#define SOFA_COMPONENT_MAPPING_MORCONTACTMAPPING_H
#include <ModelOrderReduction/config.h>
#include <sofa/core/Mapping.h>
#include <sofa/linearalgebra/CompressedRowSparseMatrix.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <vector>
#include <memory>
#include <sofa/linearalgebra/EigenSparseMatrix.h>
#include <sofa/core/objectmodel/DataFileName.h>


namespace sofa
{

namespace component
{

namespace mapping
{

template <class TIn, class TOut>
class MORContactMapping : public core::Mapping<TIn, TOut>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE2(MORContactMapping,TIn,TOut), SOFA_TEMPLATE2(core::Mapping,TIn,TOut));

    typedef core::Mapping<TIn, TOut> Inherit;
    typedef TIn In;
    typedef TOut Out;

    typedef typename In::Real			Real;
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

    typedef type::Mat<N, N, Real> Mat;

    sofa::core::objectmodel::DataFileName d_lambdaModesPath;
    sofa::core::objectmodel::DataFileName d_contactIndices;
    sofa::core::objectmodel::DataFileName d_lambdaIndicesPath;
    Data< bool > d_storeLambda;
    int m_nbCols;

protected:
    MORContactMapping()
        : Inherit()
        , d_lambdaModesPath(initData(&d_lambdaModesPath,"modesPath","Path to the file containing the modes. REQUIRED"))
        , d_contactIndices(initData(&d_contactIndices,"contactIndicesPath","Path to the file containing the modes. REQUIRED"))
        , d_lambdaIndicesPath(initData(&d_lambdaIndicesPath,"lambdaIndicesPath","Path to the file where contact indices will be stored."))
        , d_storeLambda(initData(&d_storeLambda,"storeLambda","Boolean to say if we store lambda"))
    {
        Js.resize( 1 );
        Js[0] = &J;
    }

    virtual ~MORContactMapping()
    {
    }


public:
    /// Return true if the destination model has the same topology as the source model.
    ///
    /// This is the case for mapping keeping a one-to-one correspondance between
    /// input and output DOFs (mostly identity or data-conversion mappings).
    bool sameTopology() const override { return true; }

    void init() override;

    void apply(const core::MechanicalParams *mparams, Data<VecCoord>& out, const Data<InVecCoord>& in) override;

    void applyJ(const core::MechanicalParams *mparams, Data<VecDeriv>& out, const Data<InVecDeriv>& in) override;

    void applyJT(const core::MechanicalParams *mparams, Data<InVecDeriv>& out, const Data<VecDeriv>& in) override;

    void applyJT(const core::ConstraintParams *cparams, Data<InMatrixDeriv>& out, const Data<MatrixDeriv>& in) override;

    const sofa::linearalgebra::BaseMatrix* getJ() override;

    void handleTopologyChange() override;


protected:

    typedef sofa::linearalgebra::EigenSparseMatrix<TIn, TOut> eigen_type;
    eigen_type J;

    typedef type::vector< linearalgebra::BaseMatrix* > js_type;
    js_type Js;

    Eigen::MatrixXd m_matrix;
    Eigen::MatrixXi contactIndices;

public:

    const js_type* getJs() override;

};

template <int N, int M, class Real>
struct MORContactMappingMatrixHelper;

#if  !defined(SOFA_COMPONENT_MAPPING_MORCONTACTMAPPING_CPP)

extern template class  MORContactMapping< defaulttype::Vec3dTypes, defaulttype::Vec3dTypes >;
extern template class  MORContactMapping< defaulttype::Vec2Types, defaulttype::Vec2Types >;
extern template class  MORContactMapping< defaulttype::Vec1Types, defaulttype::Vec1Types >;
extern template class  MORContactMapping< defaulttype::Vec6Types, defaulttype::Vec6Types >;
extern template class  MORContactMapping< defaulttype::Vec6Types, defaulttype::Vec3dTypes >;
extern template class  MORContactMapping< defaulttype::Vec3dTypes, defaulttype::ExtVec3Types >;
extern template class  MORContactMapping< defaulttype::Vec6Types, defaulttype::ExtVec3Types >;
extern template class  MORContactMapping< defaulttype::Rigid3Types, defaulttype::Rigid3Types >;
extern template class  MORContactMapping< defaulttype::Rigid2Types, defaulttype::Rigid2Types >;
extern template class  MORContactMapping< defaulttype::Rigid3Types, defaulttype::Vec3dTypes >;
extern template class  MORContactMapping< defaulttype::Rigid3Types, defaulttype::ExtVec3Types >;
extern template class  MORContactMapping< defaulttype::Rigid2Types, defaulttype::Vec2Types >;




#endif

} // namespace mapping

} // namespace component


namespace helper
{
    // should certainly be somewhere else
    // but at least it is accessible to other components


    template<class T1, class T2>
    static inline void eq(T1& dest, const T2& src)
    {
        dest = src;
    }

    template<class T1, class T2>
    static inline void peq(T1& dest, const T2& src)
    {
        dest += src;
    }

    // float <-> double (to remove warnings)

    //template<>
    static inline void eq(float& dest, const double& src)
    {
        dest = (float)src;
    }

    //template<>
    static inline void peq(float& dest, const double& src)
    {
        dest += (float)src;
    }

    // Vec <-> Vec

    template<int N1, int N2, class T1, class T2>
    static inline void eq(type::Vec<N1,T1>& dest, const type::Vec<N2,T2>& src)
    {
        dest = src;
    }

    template<int N1, int N2, class T1, class T2>
    static inline void peq(type::Vec<N1,T1>& dest, const type::Vec<N2,T2>& src)
    {
        for (unsigned int i=0; i<(N1>N2?N2:N1); i++)
            dest[i] += (T1)src[i];
    }

    // RigidDeriv <-> RigidDeriv

    template<int N, class T1, class T2>
    static inline void eq(defaulttype::RigidDeriv<N,T1>& dest, const defaulttype::RigidDeriv<N,T2>& src)
    {
        dest.getVCenter() = src.getVCenter();
        dest.getVOrientation() = (typename defaulttype::RigidDeriv<N,T1>::Rot)src.getVOrientation();
    }

    template<int N, class T1, class T2>
    static inline void peq(defaulttype::RigidDeriv<N,T1>& dest, const defaulttype::RigidDeriv<N,T2>& src)
    {
        dest.getVCenter() += src.getVCenter();
        dest.getVOrientation() += (typename defaulttype::RigidDeriv<N,T1>::Rot)src.getVOrientation();
    }

    // RigidCoord <-> RigidCoord

    template<int N, class T1, class T2>
    static inline void eq(defaulttype::RigidCoord<N,T1>& dest, const defaulttype::RigidCoord<N,T2>& src)
    {
        dest.getCenter() = src.getCenter();
        dest.getOrientation() = (typename defaulttype::RigidCoord<N,T1>::Rot)src.getOrientation();
    }

    template<int N, class T1, class T2>
    static inline void peq(defaulttype::RigidCoord<N,T1>& dest, const defaulttype::RigidCoord<N,T2>& src)
    {
        dest.getCenter() += src.getCenter();
        dest.getOrientation() += src.getOrientation();
    }

    // RigidDeriv <-> Vec

    template<int N, class T1, class T2>
    static inline void eq(type::Vec<N,T1>& dest, const defaulttype::RigidDeriv<N,T2>& src)
    {
        dest = src.getVCenter();
    }

    template<int N, class T1, class T2>
    static inline void peq(type::Vec<N,T1>& dest, const defaulttype::RigidDeriv<N,T2>& src)
    {
        dest += src.getVCenter();
    }

    template<int N, class T1, class T2>
    static inline void eq(defaulttype::RigidDeriv<N,T1>& dest, const type::Vec<N,T2>& src)
    {
        dest.getVCenter() = src;
    }

    template<int N, class T1, class T2>
    static inline void peq(defaulttype::RigidDeriv<N,T1>& dest, const type::Vec<N,T2>& src)
    {
        dest.getVCenter() += src;
    }

    // RigidCoord <-> Vec
    template<int N, class T1, class T2>
    static inline void eq(type::Vec<N,T1>& dest, const defaulttype::RigidCoord<N,T2>& src)
    {
        dest = src.getCenter();
    }

    template<int N, class T1, class T2>
    static inline void peq(type::Vec<N,T1>& dest, const defaulttype::RigidCoord<N,T2>& src)
    {
        dest += src.getCenter();
    }

    template<int N, class T1, class T2>
    static inline void eq(defaulttype::RigidCoord<N,T1>& dest, const type::Vec<N,T2>& src)
    {
        dest.getCenter() = src;
    }

    template<int N, class T1, class T2>
    static inline void peq(defaulttype::RigidCoord<N,T1>& dest, const type::Vec<N,T2>& src)
    {
        dest.getCenter() += src;
    }
}

} // namespace sofa

#endif
