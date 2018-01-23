runSofa MOR_snapshotGeneration.py -g batch -n5
runSofa MOR_snapshotGeneration.py -g batch -n1355
python 1_INPUT/Script_Python/readStateFilesAndComputeModes.py
runSofa MOR_PrepareECSW.py -g batch -n1355
python 1_INPUT/Script_Python/readGieFileAndComputeRIDandWeights.py 
python 1_INPUT/Script_Python/convertRIDinActiveNodes.py
runSofa MOR_PerformECSW.py
