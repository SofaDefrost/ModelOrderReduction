# -*- coding: utf-8 -*-
"""
**Set of algorithmes used during reduction**

These algorithme will generates from data produced in SOFA scene during the shaking phases
the needed data to construct our reduced model : modes/RID/Weights & elements to keep

**Content:**

"""
__all__=[	"ConvertRIDinActiveNodes",
            "ReadGieFileAndComputeRIDandWeights",
            "ReadMechanicalMatricesAndComputeVibrationModes",
            "ReadStateFilesAndComputeModes",
            "prepareStateFiletoDisplayModes"]

from mor.reduction.script.ConvertRIDinActiveNodes import convertRIDinActiveNodes
from mor.reduction.script.ReadGieFileAndComputeRIDandWeights import readGieFileAndComputeRIDandWeights
from mor.reduction.script.ReadStateFilesAndComputeModes import readStateFilesAndComputeModes
from mor.reduction.script.ReadMechanicalMatricesAndComputeVibrationModes import readMechanicalMatricesAndComputeVibrationModes
from mor.reduction.script.ReadLambdaFilesAndComputeNNMF import readLambdaFilesAndComputeNNMF
