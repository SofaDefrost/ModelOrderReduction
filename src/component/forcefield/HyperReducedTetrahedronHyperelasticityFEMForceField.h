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

#ifndef SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_H
#define SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_H

#if !defined(__GNUC__) || (__GNUC__ > 3 || (_GNUC__ == 3 && __GNUC_MINOR__ > 3))
#pragma once
#endif
#include <SofaMiscFem/HyperelasticMaterial.h>
#include <SofaMiscFem/initMiscFEM.h>
#include <sofa/core/behavior/ForceField.h>
#include <SofaBaseMechanics/MechanicalObject.h>
#include <sofa/defaulttype/Vec.h>
#include <sofa/defaulttype/Mat.h>
#include <sofa/defaulttype/MatSym.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <SofaBaseTopology/TopologyData.h>
#include <string>
#include <map>

namespace sofa
{

namespace component
{

namespace forcefield
{
using namespace std;
using namespace sofa::defaulttype;
using namespace sofa::component::topology;
using namespace sofa::core::topology;

//***************** Tetrahedron FEM code for several elastic models: TotalLagrangianForceField************************//

/** Compute Finite Element forces based on tetrahedral elements.
*/
template<class DataTypes>
class HyperReducedTetrahedronHyperelasticityFEMForceField : public core::behavior::ForceField<DataTypes>
{
  public:
    SOFA_CLASS(SOFA_TEMPLATE(HyperReducedTetrahedronHyperelasticityFEMForceField, DataTypes), SOFA_TEMPLATE(core::behavior::ForceField, DataTypes));

    typedef core::behavior::ForceField<DataTypes> Inherited;
    typedef typename DataTypes::VecCoord VecCoord;
    typedef typename DataTypes::VecDeriv VecDeriv;
    typedef typename DataTypes::Coord Coord;
    typedef typename DataTypes::Deriv Deriv;
    typedef typename Coord::value_type Real;

    typedef core::objectmodel::Data<VecDeriv>    DataVecDeriv;
    typedef core::objectmodel::Data<VecCoord>    DataVecCoord;

    typedef Mat<3,3,Real> Matrix3;
    typedef MatSym<3,Real> MatrixSym;
    typedef std::pair<MatrixSym,MatrixSym> MatrixPair;
    typedef std::pair<Real,MatrixSym> MatrixCoeffPair;


    typedef helper::vector<Real> SetParameterArray;
    typedef helper::vector<Coord> SetAnisotropyDirectionArray;


    typedef core::topology::BaseMeshTopology::index_type Index;
    typedef core::topology::BaseMeshTopology::Tetra Element;
    typedef core::topology::BaseMeshTopology::SeqTetrahedra VecElement;
    typedef sofa::core::topology::Topology::Tetrahedron Tetrahedron;
    typedef sofa::core::topology::Topology::TetraID TetraID;
    typedef sofa::core::topology::Topology::Tetra Tetra;
    typedef sofa::core::topology::Topology::Edge Edge;
    typedef sofa::core::topology::BaseMeshTopology::EdgesInTriangle EdgesInTriangle;
    typedef sofa::core::topology::BaseMeshTopology::EdgesInTetrahedron EdgesInTetrahedron;
    typedef sofa::core::topology::BaseMeshTopology::TrianglesInTetrahedron TrianglesInTetrahedron;


public :
	
	typename sofa::component::fem::MaterialParameters<DataTypes> globalParameters;

	
	class MatrixList
	{
	public:
		Matrix3 data[6];
	};


    /// data structure stored for each tetrahedron
	class TetrahedronRestInformation : public fem::StrainInformation<DataTypes>
    {
    public:
        /// shape vector at the rest configuration
        Coord m_shapeVector[4];
        /// fiber direction in rest configuration
        Coord m_fiberDirection;
        /// rest volume
        Real m_restVolume;
        /// current tetrahedron volume
        Real m_volScale;
        Real m_volume;
        /// volume/ restVolume
        MatrixSym m_SPKTensorGeneral;
        /// deformation gradient = gradPhi
        Matrix3 m_deformationGradient;
        /// right Cauchy-Green deformation tensor C (gradPhi^T gradPhi)
        Real m_strainEnergy;

        /// Output stream
        inline friend ostream& operator<< ( ostream& os, const TetrahedronRestInformation& /*eri*/ ) {  return os;  }
        /// Input stream
        inline friend istream& operator>> ( istream& in, TetrahedronRestInformation& /*eri*/ ) { return in; }

        TetrahedronRestInformation() {}
    };
	
    /// data structure stored for each edge
    class EdgeInformation
    {
    public:
        /// store the stiffness edge matrix
        Matrix3 DfDx;

        /// Output stream
        inline friend ostream& operator<< ( ostream& os, const EdgeInformation& /*eri*/ ) {  return os;  }
        /// Input stream
        inline friend istream& operator>> ( istream& in, EdgeInformation& /*eri*/ ) { return in; }

        EdgeInformation() {}
    };

 protected :
    core::topology::BaseMeshTopology* m_topology;
    VecCoord  m_initialPoints;	/// the intial positions of the points
    bool m_updateMatrix;
    bool  m_meshSaved ;

    Data<bool> d_stiffnessMatrixRegularizationWeight;
    Data<string> d_materialName; /// the name of the material
    Data<SetParameterArray> d_parameterSet;
    Data<SetAnisotropyDirectionArray> d_anisotropySet;

    // Reduced order model boolean parameters
    Data< bool > d_prepareECSW;
    Data<unsigned int> d_nbModes;
    Data<unsigned int> d_nbTrainingSet;
    Data<unsigned int> d_periodSaveGIE;

    Data< bool > d_performECSW;
    Data<std::string> d_modesPath;
    Data<std::string> d_RIDPath;
    Data<std::string> d_weightsPath;

    // Reduced order model variables
    Eigen::MatrixXd m_modes;
    std::vector<std::vector<double> > Gie;
    Eigen::VectorXd weights;
    Eigen::VectorXi reducedIntegrationDomain;
    Eigen::VectorXi reducedIntegrationDomainWithEdges;

    unsigned int m_RIDsize;
    unsigned int m_RIDedgeSize;

    TetrahedronData<sofa::helper::vector<TetrahedronRestInformation> > m_tetrahedronInfo;
    EdgeData<sofa::helper::vector<EdgeInformation> > m_edgeInfo;
   
public:

    void setMaterialName(const string name) {
        d_materialName.setValue(name);
    }
    void setparameter(const vector<Real> param) {
        d_parameterSet.setValue(param);
    }
    void setdirection(const vector<Coord> direction) {
        d_anisotropySet.setValue(direction);
    }

    class TetrahedronHandler : public TopologyDataHandler<Tetrahedron,sofa::helper::vector<TetrahedronRestInformation> >
    {
    public:
      typedef typename HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>::TetrahedronRestInformation TetrahedronRestInformation;
      TetrahedronHandler(HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>* ff,
                         TetrahedronData<sofa::helper::vector<TetrahedronRestInformation> >* data )
        :TopologyDataHandler<Tetrahedron,sofa::helper::vector<TetrahedronRestInformation> >(data)
        ,ff(ff)
      {

      }

      void applyCreateFunction(unsigned int, TetrahedronRestInformation &t, const Tetrahedron &,
                               const sofa::helper::vector<unsigned int> &, const sofa::helper::vector<double> &);

    protected:
      HyperReducedTetrahedronHyperelasticityFEMForceField<DataTypes>* ff;
    };

protected:
   HyperReducedTetrahedronHyperelasticityFEMForceField();
   
   virtual   ~HyperReducedTetrahedronHyperelasticityFEMForceField();
public:

  //  virtual void parse(core::objectmodel::BaseObjectDescription* arg);

    virtual void init();
    
    virtual void addForce(const core::MechanicalParams* mparams /* PARAMS FIRST */, DataVecDeriv& d_f, const DataVecCoord& d_x, const DataVecDeriv& d_v);
    virtual void addDForce(const core::MechanicalParams* mparams /* PARAMS FIRST */, DataVecDeriv& d_df, const DataVecDeriv& d_dx);
    virtual SReal getPotentialEnergy(const core::MechanicalParams*, const DataVecCoord&) const;
    virtual void addKToMatrix(sofa::defaulttype::BaseMatrix *mat, SReal k, unsigned int &offset);

    void draw(const core::visual::VisualParams* vparams);

    Mat<3,3,double> getPhi( int tetrahedronIndex);


  protected:

    /// the array that describes the complete material energy and its derivatives

    fem::HyperelasticMaterial<DataTypes> *m_myMaterial;
    TetrahedronHandler* m_tetrahedronHandler;

    void testDerivatives();
    void saveMesh( const char *filename );

    void updateTangentMatrix();
};

using sofa::defaulttype::Vec3dTypes;
using sofa::defaulttype::Vec3fTypes;

#if defined(SOFA_EXTERN_TEMPLATE) && !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_CPP)

#ifndef SOFA_FLOAT
extern template class SOFA_MISC_FEM_API HyperReducedTetrahedronHyperelasticityFEMForceField<Vec3dTypes>;
#endif
#ifndef SOFA_DOUBLE
extern template class SOFA_MISC_FEM_API HyperReducedTetrahedronHyperelasticityFEMForceField<Vec3fTypes>;
#endif

#endif // defined(SOFA_EXTERN_TEMPLATE) && !defined(SOFA_COMPONENT_FORCEFIELD_HYPERREDUCEDTETRAHEDRONHYPERELASTICITYFEMFORCEFIELD_CPP)

} // namespace forcefield

} // namespace component

} // namespace sofa

#endif
