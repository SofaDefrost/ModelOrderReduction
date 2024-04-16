# Liver Under Gravity
<!-- The image of the original liver versus its reduced one.-->
![Alt text](https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/3c96518c488043997fecb5cb6abaf66a4468bdc4/tools/test/sofa_test_scene/originsl_versus_reduced.png)

## Presentation
The liver is a highly complex organ with unique material properties and nonlinear behavior under deformation. Modeling the liver accurately requires capturing its intricate geometric characteristics and incorporating its viscoelastic properties to simulate realistic responses to external forces. This is the rationale behind our application of model order reduction in liver modeling, which enables us to reduce complexity while preserving crucial 
dynamic behaviors.

**Brief description** : 
For simulating the liver, we employ a mesh that has 22019 tetrahedra with 4293 nodes under the gravitational force. In particular, the liver with its full representation, is fixed from the top and deforms as a result of gravity.

**Why reduce it**:
We employ our model order reduction to effectively characterize the liver's deformations caused by external forces. As a result, this will enable us to design real-time finite element-based simulations with the organ at less cost.

## Reduction Parameters
Unlike the case of soft robots, in this setting of the liver, there is no actuator. Therefore, all the deformations happen due to the gravity force.

## Results
After applying model order reduction on this fine mesh of the liver, the mesh reduces to one with 40 active nodes and only 10 tetrahedra.
**Before**
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/a3a587a8457eca9fa18dd1444a7c20a9ba0b8046/tools/test/sofa_test_scene/liverFine_test_with_visual_larg.png" alt="Alt Text">  <figcaption>1000 iterations done in 1612.79 s ( 0.620042 FPS)</figcaption>  </figure>



**After**
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/3a52e852afaff9ac71ebf7602353f369410086d2/tools/test/sofa_test_scene/reduced_test_with_visual_large.png" alt="Alt Text">  <figcaption> 1000 iterations done in 3.80876 s ( 262.553 FPS).</figcaption>  </figure>


