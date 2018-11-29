# -*- coding: utf-8 -*-
"""
**Set of class simplifying and allowing to perform ModelReduction**

**Content:**

.. autosummary::
    :toctree: _autosummary

	mor.reduction.script.ConvertRIDinActiveNodes
	mor.reduction.script.ReadGieFileAndComputeRIDandWeights
	mor.reduction.script.ReadStateFilesAndComputeModes
	mor.reduction.script.prepareStateFiletoDisplayModes
	mor.reduction.script.ReadMechanicalMatricesAndComputeVibrationModes

"""
__all__=[	"ConvertRIDinActiveNodes",
            "ReadGieFileAndComputeRIDandWeights",
            "ReadMechanicalMatricesAndComputeVibrationModes",
            "ReadStateFilesAndComputeModes"]

from ConvertRIDinActiveNodes import convertRIDinActiveNodes
from ReadGieFileAndComputeRIDandWeights import readGieFileAndComputeRIDandWeights
from ReadStateFilesAndComputeModes import readStateFilesAndComputeModes
