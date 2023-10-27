# 6-legged Robot

![sofia robot](sofia_robot.jpeg)

## Presentation

**Brief description :**

This robot has 6 legs actuated independently by 6 motors, which allows it to have various kind of movements.
 
*presentation video of the simulation showing it in action:*

<iframe width="560" height="315" src="https://www.youtube.com/embed/iQbSaFNWkAE" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
	
---

*video of the realisation based on the previous simulation:*

<iframe width="560" height="315" src="https://www.youtube.com/embed/ZoPqL80fZ10" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>


**Why reduce it :**

To show that we can easily reduce parts of a soft robot and re-use it in the full robot.
Here we only reduce the leg of our robot not its core. 

## Reduction Parameters

To make a reduced model of one leg of this robot, we had to create a new special function to explore its workspace.
To create the rotation mouvement we see on the different previous videos we rotate a point that will be followed by the model creating the rotation.

:meth:`mor.animation.defaultShaking` how it was implemented

We have only one actuator here, so our *listObjToAnimate* contains only one object:

	ObjToAnimate("actuator","shakingSofia",'MechanicalObject',incr=0.05,incrPeriod=3,rangeOfAction=6.4,dataToWorkOn="position",angle=0,rodRadius=0.7)

With these different parameters we will after perform the reduction like explained {doc}`here </usage/tutorial/modelOrderReduction>`


## Results 

**With coarse mesh**

![reduction_coarseMesh](reduction_coarseMesh.png)

.. raw:: html

    <table style="width:100%">
        <tr>
        <td>\</td>
        <td>not reduced</td> 
        <td>reduced</td>
      </tr>
      <tr>
        <td>Fps</td>
        <td>90</td>
        <td>300</td>
      </tr>
    </table>

---


**With fine mesh**

![reduction_fineMesh](reduction_fineMesh.png)

.. raw:: html

    <table style="width:100%">
      <tr>
        <td>\</td>
        <td>not reduced</td> 
        <td>reduced</td>
      </tr>
      <tr>
        <td>Fps</td>
        <td>3.8</td>
        <td>190</td>
      </tr>
    </table>
