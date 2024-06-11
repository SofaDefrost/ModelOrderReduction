# Liver 

<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/master/doc/sphinx/source/usage/examples/Liver/full_versus_reduced_gravity.png" alt="Alt Text">  <figcaption> From left to right: fine mesh with 4293 nodes; reduced mesh: 40 active nodes and only 10 tetrahedra. </figcaption>  </figure>
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/master/doc/sphinx/source/usage/examples/Liver/full_versus_reduced_rotation.png" alt="Alt Text">  <figcaption> From left to right: fine mesh with 4293 nodes; reduced mesh: with 53 active nodes and only 18 tetrahedra. </figcaption>  </figure>


## Presentation
The liver is a highly complex organ with unique material properties and nonlinear behavior under deformation. Modeling the liver accurately requires capturing its intricate geometric characteristics and incorporating its viscoelastic properties to simulate realistic responses to external forces. This is the rationale behind our application of model order reduction in liver modeling, which enables us to reduce complexity while preserving crucial 
dynamic behaviors.

**Brief description**:  

For simulating the liver, we employ a mesh that has 22019 tetrahedra with 4293 nodes.  We are conducting experiments with two scenarios of liver deformation: one induced by gravity and the other by rotational actuation. In both cases, the liver is fully represented and fixed from the top. Under these conditions, the liver undergoes deformation either due to the force of gravity or manual actuation.

**Why reduce it**:

We employ our model order reduction to effectively characterize the liver's deformations. As a result, this will enable us to design real-time finite element-based simulations with the organ at less cost.

## Reduction Parameters
To apply actuation, we utilize a specialized animation function called 'shakingLiver,' which rotates designated nodes from 0 to 6.2 radians. Conversely, in another experiment, no deliberate actuation is applied, and the liver's motion is solely the result of gravity acting upon it within the initial scene.

 ## Results
 In both examples, we use the following mesh with 22019 tetrahedra and 4293 nodes:

 **Original Model**
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/master/doc/sphinx/source/usage/examples/Liver/fullModel.png" alt="Alt Text">  <figcaption>1000 iterations done in 1612.79 s ( 0.620042 FPS).</figcaption>  </figure>

 ### Liver Under Gravity
After applying model order reduction on this fine mesh of the liver, the mesh reduces to one with 40 active nodes and only 10 tetrahedra.


**Reduced Model**
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/master/doc/sphinx/source/usage/examples/Liver/reducedModel_gravity.png" alt="Alt Text">  <figcaption> 1000 iterations done in 3.80876 s ( 262.553 FPS).</figcaption>  </figure>

### Liver With Rotational Actuation
After applying model order reduction on the fine mesh of the liver, the mesh reduces to one with 53 active nodes and only 18 tetrahedra.

**Reduced Model**
 <figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/master/doc/sphinx/source/usage/examples/Liver/reducedModel_rotation.png" alt="Alt Text">  <figcaption>1000 iterations done in 5.79132 s ( 172.672 FPS).</figcaption>  </figure>
