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
#ifndef HYPERREDUCEDHELPER_H
#define HYPERREDUCEDHELPER_H
#include <ModelOrderReduction/initModelOrderReduction.h>

#include <sofa/core/behavior/BaseMechanicalState.h>
#include <sofa/core/objectmodel/Event.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/defaulttype/DataTypeInfo.h>
#include <sofa/simulation/Visitor.h>

#include <sofa/core/objectmodel/Data.h>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/helper/system/config.h>
#include <SofaDeformable/config.h>
#include <fstream> // for reading the file
#include <iostream>


#include "../loader/MatrixLoader.h"
#include <sofa/core/objectmodel/BaseContext.h>


namespace sofa
{

namespace component
{

namespace forcefield
{

using sofa::component::loader::MatrixLoader;

class HyperReducedHelper : public virtual core::objectmodel::BaseObject
{
public:

    SOFA_CLASS(HyperReducedHelper,core::objectmodel::BaseObject);
//class HyperReducedForceField
//{
public:
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
    //sofa::helper::vector<sofa::helper::vector<double>> Gie;
    std::vector<std::vector<double> > Gie;
    Eigen::VectorXd weights;
    Eigen::VectorXi reducedIntegrationDomain;
    unsigned int m_RIDsize;

public:
    HyperReducedHelper()
        : d_prepareECSW(initData(&d_prepareECSW,false,"prepareECSW","Save data necessary for the construction of the reduced model"))
        , d_nbModes(initData(&d_nbModes,unsigned(3),"nbModes","Number of modes when preparing the ECSW method only"))
        , d_modesPath(initData(&d_modesPath,std::string("modes.txt"),"modesPath","Path to the file containing the modes (useful only for preparing ECSW)"))
        , d_nbTrainingSet(initData(&d_nbTrainingSet,unsigned(40),"nbTrainingSet","When preparing the ECSW, size of the training set"))
        , d_periodSaveGIE(initData(&d_periodSaveGIE,unsigned(5),"periodSaveGIE","When prepareECSW is true, the values of Gie are taken every periodSaveGIE timesteps."))
        , d_performECSW(initData(&d_performECSW,false,"performECSW","Use the reduced model with the ECSW method"))
        , d_RIDPath(initData(&d_RIDPath,std::string("reducedIntegrationDomain.txt"),"RIDPath","Path to the Reduced Integration domain when performing the ECSW method"))
        , d_weightsPath(initData(&d_weightsPath,std::string("weights.txt"),"weightsPath","Path to the weights when performing the ECSW method"))
    {
    }


    void initMOR(unsigned int nbElements){
        if (d_prepareECSW.getValue()){
            MatrixLoader<Eigen::MatrixXd>* matLoader = new MatrixLoader<Eigen::MatrixXd>();
            matLoader->setFileName(d_modesPath.getValue());
            matLoader->load();
            matLoader->getMatrix(m_modes);
            delete matLoader;
            m_modes.conservativeResize(Eigen::NoChange,d_nbModes.getValue());

            Gie.resize(d_nbTrainingSet.getValue()*d_nbModes.getValue());

            for (unsigned int i = 0; i < d_nbTrainingSet.getValue()*d_nbModes.getValue(); i++)
            {
                Gie[i].resize(nbElements);
                for (unsigned int j = 0; j < nbElements; j++)
                {
                    Gie[i][j] = 0;
                }
            }
        }

        if (d_performECSW.getValue())
        {

            MatrixLoader<Eigen::VectorXd>* weightsMatLoader = new MatrixLoader<Eigen::VectorXd>();
            weightsMatLoader->setFileName(d_weightsPath.getValue());
            weightsMatLoader->load();
            weightsMatLoader->getMatrix(weights);
            delete weightsMatLoader;

            MatrixLoader<Eigen::VectorXi>* RIDMatLoader = new MatrixLoader<Eigen::VectorXi>();
            RIDMatLoader->setFileName(d_RIDPath.getValue());
            RIDMatLoader->load();
            RIDMatLoader->getMatrix(reducedIntegrationDomain);
            delete RIDMatLoader;

            m_RIDsize = reducedIntegrationDomain.rows();

        }
        else
        {
            m_RIDsize = nbElements;  // the reduced integration contains all the elements in this case.
            reducedIntegrationDomain.resize(m_RIDsize);
            for (unsigned int i = 0; i<m_RIDsize; i++)
                reducedIntegrationDomain(i) = i;
        }

    }

    template<class DataTypes>
    void updateGie(const std::vector<unsigned int> indexList, const std::vector<typename DataTypes::Deriv> contrib, const unsigned int numElem){
        if (d_prepareECSW.getValue())
        {
            size_t nbNodesPerElement = indexList.size();
            std::vector<double> GieUnit(d_nbModes.getValue());
            int numTest = unsigned int(this->getContext()->getTime()/this->getContext()->getDt());
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



    void saveGieFile(unsigned int nbElements){
        if (d_prepareECSW.getValue())
        {
            unsigned int numTest = unsigned int(this->getContext()->getTime()/this->getContext()->getDt());
            if (numTest%d_periodSaveGIE.getValue() == 0)       // A new value was taken
            {
                numTest = numTest/d_periodSaveGIE.getValue();
                if (numTest < d_nbTrainingSet.getValue()){
                    std::stringstream gieFileNameSS;
                    gieFileNameSS << this->name << "_Gie.txt";
                    std::string gieFileName = gieFileNameSS.str();
                    std::ofstream myfileGie (gieFileName, std::fstream::app);
                    msg_info(this) << "Storing case number " << numTest+1 << " in " << gieFileName << " ...";
                    for (unsigned int k=numTest*d_nbModes.getValue(); k<(numTest+1)*d_nbModes.getValue();k++){
                        for (unsigned int l=0;l<nbElements;l++){
                            myfileGie << Gie[k][l] << " ";
                        }
                        myfileGie << std::endl;
                    }
                    myfileGie.close();
                    msg_info(this) << "Storing Done";
                }
                else
                {
                    msg_info(this) << d_nbTrainingSet.getValue() << "were already stored. Learning phase completed.";
                }
            }
        }

    }

};



} // namespace forcefield

} // namespace component

} // namespace sofa


#endif // HYPERREDUCEDHELPER_H
