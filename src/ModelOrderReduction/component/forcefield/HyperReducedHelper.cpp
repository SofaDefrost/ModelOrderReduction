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
#include <ModelOrderReduction/component/forcefield/HyperReducedHelper.h>

namespace modelorderreduction
{

HyperReducedHelper::HyperReducedHelper()
: d_prepareECSW(initData(&d_prepareECSW,false,"prepareECSW","Save data necessary for the construction of the reduced model"))
, d_nbModes(initData(&d_nbModes,unsigned(3),"nbModes","Number of modes when preparing the ECSW method only"))
, d_modesPath(initData(&d_modesPath,std::string("modes.txt"),"modesPath","Path to the file containing the modes (useful only for preparing ECSW)"))
, d_nbTrainingSet(initData(&d_nbTrainingSet,unsigned(40),"nbTrainingSet","When preparing the ECSW, size of the training set"))
, d_periodSaveGIE(initData(&d_periodSaveGIE,unsigned(5),"periodSaveGIE","When prepareECSW is true, the values of Gie are taken every periodSaveGIE timesteps."))
, d_performECSW(initData(&d_performECSW,false,"performECSW","Use the reduced model with the ECSW method"))
, d_RIDPath(initData(&d_RIDPath,std::string("reducedIntegrationDomain.txt"),"RIDPath","Path to the Reduced Integration domain when performing the ECSW method"))
, d_weightsPath(initData(&d_weightsPath,std::string("weights.txt"),"weightsPath","Path to the weights when performing the ECSW method"))
{
    static const std::string groupName { "HyperReduction" };
    d_prepareECSW.setGroup(groupName);
    d_nbModes.setGroup(groupName);
    d_modesPath.setGroup(groupName);
    d_nbTrainingSet.setGroup(groupName);
    d_periodSaveGIE.setGroup(groupName);
    d_performECSW.setGroup(groupName);
    d_RIDPath.setGroup(groupName);
    d_weightsPath.setGroup(groupName);

}

void HyperReducedHelper::initMOR(unsigned nbElements, bool printLog)
{
    if (d_prepareECSW.getValue())
    {
        MatrixLoader<Eigen::MatrixXd>* matLoader = new MatrixLoader<Eigen::MatrixXd>();
        matLoader->m_printLog = printLog;
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
        weightsMatLoader->m_printLog = printLog;
        weightsMatLoader->setFileName(d_weightsPath.getValue());
        weightsMatLoader->load();
        weightsMatLoader->getMatrix(weights);
        delete weightsMatLoader;

        MatrixLoader<Eigen::VectorXi>* RIDMatLoader = new MatrixLoader<Eigen::VectorXi>();
        RIDMatLoader->m_printLog = printLog;
        RIDMatLoader->setFileName(d_RIDPath.getValue());
        RIDMatLoader->load();
        RIDMatLoader->getMatrix(reducedIntegrationDomain);
        delete RIDMatLoader;

        m_RIDsize = reducedIntegrationDomain.rows();
        if (m_RIDsize == 0) {
            msg_warning() << "RID is empty! Integrating over all the elements!";
            m_RIDsize = nbElements;  // the reduced integration contains all the elements in this case.
            reducedIntegrationDomain.resize(m_RIDsize);
            for (unsigned int i = 0; i<m_RIDsize; i++)
                reducedIntegrationDomain(i) = i;

        }

    }
    else
    {
        m_RIDsize = nbElements;  // the reduced integration contains all the elements in this case.
        reducedIntegrationDomain.resize(m_RIDsize);
        for (unsigned int i = 0; i<m_RIDsize; i++)
            reducedIntegrationDomain(i) = i;
    }

}

void HyperReducedHelper::saveGieFile(unsigned nbElements)
{
    if (d_prepareECSW.getValue())
    {
        unsigned int numTest = int(this->getContext()->getTime()/this->getContext()->getDt());
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

}
