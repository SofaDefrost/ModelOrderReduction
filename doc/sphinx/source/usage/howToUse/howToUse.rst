How to use
===========

Reduce a model
-----------------

As explained in the principle section there are 2 main phase to produce the reduced model :

- First reduction to have a reduce basis thanks to modes
- Second do a hyper-reduction on first reduction

Using SOFA we will do this in 4 step as described with the following figure :

.. image:: ../images/MOR_plugin_execution_v2.png

This different step will alternate between using SOFA to generate data from a given shaking and external python script to extract from this data modes then RID & weights.
We have developed several ways to do this arduous process in a more user friendly ways :

.. toctree::
    :maxdepth: 1

    howToReduce_script
    howToReduce_gui

Tutorial video how to
----------------------

.. raw:: html

	<iframe width="560" height="315" src="https://www.youtube.com/embed/0IhF03w6m0M?si=C2Q5cBb5Vd-bNiGv" frameborder="0"  allowfullscreen="allowfullscreen"></iframe><br/><br/>