# -*- coding: utf-8 -*-
"""
Set of predefined function to shake our model during the reduction

Each function has to have 3 mandatory arguments:

+--------------+--------------+----------------------------------------------------------------------+
| argument     | type         | definition                                                           |
+==============+==============+======================================================================+
| objToAnimate | ObjToAniamte | the obj containing all the information/arguments about the animation |
+--------------+--------------+----------------------------------------------------------------------+
| dt           | sc           | Time sept of the Sofa scene                                          |
+--------------+--------------+----------------------------------------------------------------------+
| factor       | float        ||  Argument given by the Animation class from STLIB.                  |
|              |              ||  It indicate where we are in the animation sequence:                |
|              |              |-  0.0 ------> beginning of sequence                                  |
|              |              |-  1.0 ------> end of sequence                                        |
|              |              ||  It is calculated as follow:                                        |
|              |              ||  ``factor = (currentTime-startTime) / duration``                    |
+--------------+--------------+----------------------------------------------------------------------+

**Content:**

.. autosummary::
    :toctree: _autosummary

    mor.animation.defaultShaking
    mor.animation.shakingSofia
    mor.animation.shakingInverse

"""
__all__=["shakingAnimations"]
from shakingAnimations import defaultShaking
from shakingAnimations import shakingSofia
from shakingAnimations import shakingInverse