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

#include <sofa/core/behavior/BaseMechanicalState.h>
#include <sofa/core/objectmodel/Event.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/defaulttype/DataTypeInfo.h>
#include <sofa/simulation/Visitor.h>

#include <sofa/core/objectmodel/Data.h>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/ForceField.h>
#include <fstream> // for reading the file
#include <iostream>
#include <Eigen/Sparse>

#include <ModelOrderReduction/component/loader/MatrixLoader.h>
#include <sofa/core/objectmodel/BaseContext.h>


namespace modelorderreduction
{

using namespace sofa;
using sofa::component::loader::MatrixLoader;

class SOFA_MODELORDERREDUCTION_API HyperReducedHelper : public virtual sofa::core::objectmodel::BaseObject
{
public:

    SOFA_CLASS(HyperReducedHelper, sofa::core::objectmodel::BaseObject);

    // Reduced order model SOFA Data parameters
    Data< bool > d_prepareECSW;
    Data<unsigned int> d_nbModes;
    Data<std::string> d_modesPath;
    Data<unsigned int> d_nbTrainingSet;
    Data<unsigned int> d_periodSaveGIE;

    Data< bool > d_performECSW;
    Data<std::string> d_RIDPath;
    Data<std::string> d_weightsPath;

    // Reduced order model variables
    Eigen::MatrixXd m_modes;
    //sofa::type::vector<sofa::type::vector<double>> Gie;
    std::vector<std::vector<double> > Gie;
    Eigen::VectorXd weights;
    Eigen::VectorXi reducedIntegrationDomain;
    unsigned int m_RIDsize;

    HyperReducedHelper();

    void initMOR(unsigned int nbElements, bool printLog = false);

    template<class DataTypes>
    void updateGie(const std::vector<unsigned int> indexList, const std::vector<typename DataTypes::Deriv> contrib, const unsigned int numElem);


    void saveGieFile(unsigned int nbElements);
};


template <class DataTypes>
void HyperReducedHelper::updateGie(const std::vector<unsigned> indexList,
    const std::vector<typename DataTypes::Deriv> contrib, const unsigned numElem)
{
    if (d_prepareECSW.getValue())
    {
        size_t nbNodesPerElement = indexList.size();
        std::vector<double> GieUnit(d_nbModes.getValue());
        int numTest = int(this->getContext()->getTime()/this->getContext()->getDt());
        if (numTest%d_periodSaveGIE.getValue() == 0)       // Take a measure every periodSaveGIE timesteps
        {
            numTest = numTest/d_periodSaveGIE.getValue();
            for (unsigned int modNum = 0 ; modNum < d_nbModes.getValue() ; modNum++)
            {
                GieUnit[modNum] = 0;
                for (unsigned int i=0; i<nbNodesPerElement; i++){
                    GieUnit[modNum] += contrib[i]*typename DataTypes::Deriv(m_modes(3*indexList[i],modNum),m_modes(3*indexList[i]+1,modNum),m_modes(3*indexList[i]+2,modNum));
                }
            }
            for (unsigned int i = 0 ; i < d_nbModes.getValue() ; i++)
            {
                if ( d_nbModes.getValue()*numTest < d_nbModes.getValue()*d_nbTrainingSet.getValue() )
                {
                    Gie[d_nbModes.getValue()*numTest+i][numElem] = GieUnit[i];
                }
            }
        }
    }

}
} // namespace modelorderreduction

