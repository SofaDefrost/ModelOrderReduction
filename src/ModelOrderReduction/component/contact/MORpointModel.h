/******************************************************************************
*                 SOFA, Simulation Open-Framework Architecture                *
*                    (c) 2006 INRIA, USTL, UJF, CNRS, MGH                     *
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
#ifndef MOR_POINTCOLLISIONMODEL_H
#define MOR_POINTCOLLISIONMODEL_H
#include <ModelOrderReduction/config.h>

#include <sofa/component/collision/geometry/PointModel.h>
#include <sofa/component/collision/geometry/PointModel.inl>

#include <sofa/core/CollisionModel.h>
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/component/collision/geometry/fwd.h>

#include <vector>
#include <Eigen/Sparse>


namespace sofa::component::collision::geometry
{


template<class TDataTypes>
class MORPointCollisionModel : public PointCollisionModel<TDataTypes>
{
public:
    SOFA_CLASS(SOFA_TEMPLATE(MORPointCollisionModel, TDataTypes), SOFA_TEMPLATE(PointCollisionModel, TDataTypes));
protected:
    MORPointCollisionModel();

public:

protected:
    using PointCollisionModel<TDataTypes>::mstate;
    using PointCollisionModel<TDataTypes>::size;
    using PointCollisionModel<TDataTypes>::normals;
    using PointCollisionModel<TDataTypes>::m_displayFreePosition;
    void init() override;

    // -- CollisionModel interface

    void draw(const core::visual::VisualParams* vparams) override;

    Data<bool> displayContactModes;
    Data<std::string> d_lambdaModesPath;
    Data<std::string> d_lambdaModesCoeffsPath;
    Eigen::MatrixXd lambdaModes;
    Eigen::MatrixXi contactIndices;

};


#if  !defined(MOR_POINTCOLLISIONMODEL_CPP)
extern template class SOFA_MODELORDERREDUCTION_API MORPointCollisionModel<defaulttype::Vec3Types>;
#endif

} // namespace sofa::component::collision::geometry

#endif
