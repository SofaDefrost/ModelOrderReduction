# Liver With Rotation

![](https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/b473fe3f3ebccb752bace0603aa6c2fe1bdc0241/doc/sphinx/source/usage/examples/liverWithRotation/original_versus_reduced.png)

## Presentation
The liver is a highly complex organ with unique material properties and nonlinear behavior under deformation. Modeling the liver accurately requires capturing its intricate geometric characteristics and incorporating its viscoelastic properties to simulate realistic responses to external forces. This is the rationale behind our application of model order reduction in liver modeling, which enables us to reduce complexity while preserving crucial 
dynamic behaviors.

**Brief description** : 
To simulate the liver, we utilize a mesh consisting of 22,019 tetrahedra and 4,293 nodes. In this setup, the liver is represented with its full geometry, anchored at the top and rotated from the bottom during the simulation.

**Why reduce it**:
We utilize model order reduction to efficiently characterize the liver's deformations resulting from rotational movement. This approach allows us to design real-time finite element simulations of the organ at a reduced computational cost.

## Reduction Parameters
To simulate liver motion, we employ a specific animation function called 'shakingLiver,' which rotates the designated nodes from an angle of zero to 6.2 radians. 

## Results
After applying model order reduction on this fine mesh of the liver, the mesh reduces to one with 53 active nodes and only 18 tetrahedra.
**Before**
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/a3a587a8457eca9fa18dd1444a7c20a9ba0b8046/tools/test/sofa_test_scene/liverFine_test_with_visual_larg.png" alt="Alt Text">  <figcaption>1000 iterations done in 1612.79 s ( 0.620042 FPS).</figcaption>  </figure>



**After**
 <figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/58d27d84204844609252691f031a656c82427a4e/doc/sphinx/source/usage/examples/liverWithRotation/reduced_pyscn_with_visual_larg.png" alt="Alt Text">  <figcaption>1000 iterations done in 5.79132 s ( 172.672 FPS).</figcaption>  </figure>







