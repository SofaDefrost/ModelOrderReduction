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

#ifndef MOR_POINTMODEL_INL
#define MOR_POINTMODEL_INL

#include <sofa/helper/config.h>
#include <sofa/geometry/proximity/PointTriangle.h>
#include <sofa/type/Mat.h>
#include <sofa/type/Vec.h>
#include <iostream>
#include <algorithm>

#include <ModelOrderReduction/component/contact/MORpointModel.h>
#include <sofa/core/visual/VisualParams.h>
#include <sofa/component/collision/geometry/CubeModel.h>
#include <sofa/core/ObjectFactory.h>
#include <vector>

#include <sofa/core/topology/BaseMeshTopology.h>

#include <sofa/simulation/Simulation.h>
#include <ModelOrderReduction/component/loader/MatrixLoader.h>
#include <ModelOrderReduction/component/loader/MatrixLoader.inl>

namespace sofa::component::collision::geometry
{
using sofa::component::loader::MatrixLoader;
template<class DataTypes>
MORPointCollisionModel<DataTypes>::MORPointCollisionModel()
    : PointCollisionModel<DataTypes>()
    , displayContactModes(initData(&displayContactModes, false, "displayContactModes", "display Contact Modes"))
    , d_lambdaModesPath (initData(&d_lambdaModesPath, "lambdaModesPath", "path to the file containing the lambda modes"))
    , d_lambdaModesCoeffsPath (initData(&d_lambdaModesCoeffsPath, "lambdaModesCoeffsPath", "path to the file containing the coefficients of lambda modes"))
{
}


template<class DataTypes>
void MORPointCollisionModel<DataTypes>::init()
{
    this->PointCollisionModel<DataTypes>::init();

    MatrixLoader<Eigen::MatrixXd>* matLoaderModes = new MatrixLoader<Eigen::MatrixXd>();
    matLoaderModes->setFileName(d_lambdaModesPath.getValue());
    matLoaderModes->load();
    matLoaderModes->getMatrix(lambdaModes);

    auto* matLoader = new MatrixLoader<Eigen::MatrixXi>();
    matLoader->setFileName(d_lambdaModesCoeffsPath.getValue());
    matLoader->load();
    matLoader->getMatrix(contactIndices);

}


template<class DataTypes>
void MORPointCollisionModel<DataTypes>::draw(const core::visual::VisualParams* vparams)
{
    if (vparams->displayFlags().getShowCollisionModels())
    {
        if (vparams->displayFlags().getShowWireFrame())
            vparams->drawTool()->setPolygonMode(0, true);

        // Check topological modifications
        if (mstate->getSize() != size)
            return;

        std::vector< type::Vec3 > pointsP;
        std::vector< type::Vec3 > pointsL;
        int numMode;
        double val;
        double step =  this->getContext()->getTime()/this->getContext()->getDt();
        numMode = (int) step - 1;
        for (int i = 0; i < size; i++)
        {
            TPoint<DataTypes> p(this, i);
            if (p.isActive())
            {
                pointsP.push_back(p.p());
                if (displayContactModes.getValue() && numMode >= 0 && numMode < lambdaModes.cols()){
                    if (contactIndices(i) != -1)
                        val = lambdaModes(contactIndices(i),numMode);
                    else
                        val = 0;
                    if (val != 0){
                    }
//                    pointsL.push_back(p.p());
//                    pointsL.push_back(p.p() + normals[i] * 1000.1f*val);
//                    vparams->drawTool()->drawArrow(p.p(), p.p() + normals[i] * 20.1f*val, 0.06, 0.4, 0.3, {0.25f, 0.75f, 0.75f, 1});
                    vparams->drawTool()->drawArrow(p.p(), p.p() + normals[i] * 60.1f*val, 0.4, 2.0, 1.8, type::RGBAColor(0.25f, 0.75f, 0.75f, 1));
                }
                if ((unsigned)i < normals.size())
                {
//                    pointsL.push_back(p.p());
//                    pointsL.push_back(p.p() + normals[i] * 1.1f);
                }
            }
        }

        const auto* color = this->getColor4f();
        vparams->drawTool()->drawPoints(pointsP, 3, type::RGBAColor(color[0], color[1], color[2], color[3]));
        vparams->drawTool()->drawLines(pointsL, 3, type::RGBAColor(color[0], color[1], color[2], color[3]));

        if (m_displayFreePosition.getValue())
        {
            std::vector< type::Vec3 > pointsPFree;

            for (int i = 0; i < size; i++)
            {
                TPoint<DataTypes> p(this, i);
                if (p.isActive())
                {
                    pointsPFree.push_back(p.pFree());
                }
            }

            vparams->drawTool()->drawPoints(pointsPFree, 3, type::RGBAColor(0.0f, 1.0f, 0.2f, 1.0f));
        }

        if (vparams->displayFlags().getShowWireFrame())
            vparams->drawTool()->setPolygonMode(0, false);
    }

    if (this->getPrevious() != nullptr && vparams->displayFlags().getShowBoundingCollisionModels())
        this->getPrevious()->draw(vparams);
}
} // namespace sofa::component::collision::geometry

#endif
