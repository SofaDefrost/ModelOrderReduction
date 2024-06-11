# -*- coding: utf-8 -*-
"""
**Set of predefined function to shake our model during the reduction**

Each function has to have 3 mandatory arguments:

+--------------+---------------------------+----------------------------------------------------------------------+
| argument     | type                      | definition                                                           |
+==============+===========================+======================================================================+
| objToAnimate | :py:class:`.ObjToAnimate` | the obj containing all the information/arguments about the animation |
+--------------+---------------------------+----------------------------------------------------------------------+
| dt           | seconde (in float)        | Time step of the Sofa scene                                          |
+--------------+---------------------------+----------------------------------------------------------------------+
| factor       | float                     |  Argument given by the Animation class from STLIB.                   |
|              |                           |  It indicate where we are in the animation sequence:                 |
|              |                           |                                                                      |
|              |                           |  *  0.0 ------> beginning of sequence.                               |
|              |                           |  *  1.0 ------> end of sequence.                                     |
|              |                           |                                                                      |
|              |                           |  It is calculated as follow:                                         |
|              |                           |                                                                      |
|              |                           |  ``factor = (currentTime-startTime) / duration``                     |
+--------------+---------------------------+----------------------------------------------------------------------+

the animation implemented in :py:mod:`mor.animation` will be added
to the templated scene thanks to the :func:`stlib:splib.animation.animate`

---------------------------------

"""
__all__=["shakingAnimations"]
from mor.animation.shakingAnimations import defaultShaking
from mor.animation.shakingAnimations import doingCircle
from mor.animation.shakingAnimations import shakingInverse
from mor.animation.shakingAnimations import doingNothing