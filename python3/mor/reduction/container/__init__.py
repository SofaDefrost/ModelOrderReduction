# -*- coding: utf-8 -*-
"""
**Set of Function/Class to perform Model Reduction**

**Content:**

.. autosummary::
    :toctree: _autosummary

    mor.reduction.container.objToAnimate
    mor.reduction.container.reductionAnimations
    mor.reduction.container.packageBuilder
    mor.reduction.container.reductionParam

"""
__all__=["objToAnimate","reductionAnimations","packageBuilder","reductionParam"]

from mor.reduction.container.objToAnimate import ObjToAnimate
from mor.reduction.container.reductionAnimations import ReductionAnimations
from mor.reduction.container.packageBuilder import PackageBuilder
from mor.reduction.container.reductionParam import ReductionParam