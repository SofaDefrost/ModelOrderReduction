# -*- coding: utf-8 -*-
"""
**Set of algorithmes used during reduction**

These algorithme will generates from data produced in SOFA scene during the shaking phases
the needed data to construct our reduced model : modes/RID/Weights & elements to keep

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

from mor.reduction.script.ConvertRIDinActiveNodes import convertRIDinActiveNodes
from mor.reduction.script.ReadGieFileAndComputeRIDandWeights import readGieFileAndComputeRIDandWeights
from mor.reduction.script.ReadStateFilesAndComputeModes import readStateFilesAndComputeModes

