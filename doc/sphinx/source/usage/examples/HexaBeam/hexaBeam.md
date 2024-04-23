# HexaBeam 
![](https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/269971953c647ca45858ae26512ed17c3f613142/doc/sphinx/source/usage/examples/HexaBeamWithGravity/original_versus_reudced.png)
## Presentation
HexaBeam structures are highly effective at accurately representing the deformations of complex geometries within finite element-based simulations. In this context, we demonstrate model order reduction using a straightforward scenario involving a single beam subjected to gravitational force.

**Brief description** : 

For this simulation, we use a mesh consisting of 171 hexahedra with 320 nodes, subjected to gravitational forces. Specifically, one end of the beam is fixed, and deformation occurs due to gravitational loading.

**Why reduce it**:

We employ our model order reduction to effectively characterize the beam's deformation caused by external forces. This approach allows us to simulate HexaBeam meshes with reduced computational cost and improved efficiency.

## Reduction Parameters
 In this setting of the HexaBeam, there is no actuator. Therefore, all the deformations happen due to the gravity force.
 ## Results
After applying model order reduction on this scene, the model reduces to one with 24 active nodes and only 3 hexahedra.

**Before**
<figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/93f264e3edad6e0b4552c2ac9cf4796469c3e16e/doc/sphinx/source/usage/examples/HexaBeamWithGravity/hexaBeam_test_with_boxROI_original.png" alt="Alt Text">  <figcaption> 1000 iterations done in 4.31962 s ( 231.502 FPS).</figcaption>  </figure>


 
 **After**
 <figure>  <img src="https://raw.githubusercontent.com/SofaDefrost/ModelOrderReduction/93f264e3edad6e0b4552c2ac9cf4796469c3e16e/doc/sphinx/source/usage/examples/HexaBeamWithGravity/reduced_test_with_boxROI.png" alt="Alt Text">  <figcaption>1000 iterations done in 0.270993 s ( 3690.13 FPS).</figcaption>  </figure>





