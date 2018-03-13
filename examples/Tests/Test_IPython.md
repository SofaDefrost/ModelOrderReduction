
# Model Order Reduction Exemple
***


## User Paramters
***


```python
def openfile_dialog():
    from PyQt5 import QtGui
    from PyQt5 import QtGui, QtWidgets
    app = QtWidgets.QApplication([dir])
    file = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory"))
    return file
```

- **The name of the scene you want to work on :**


```python
originalScene = "originalScene"
```

- **The Node of your scene you want to animate :**


```python
toAnimate = ["nord","ouest","sud","est"]
```

- **The different parameters for the node's animation :**


```python
nbActuator = len(toAnimate)
increment = [5]*nbActuator
breathTime = [10]*nbActuator
maxPull = [40]*nbActuator
```

- **The different Tolerances :**


```python
tolModes = 0.001
tolGIE =  0.05
```

- **Where will be all the differents results and with which name**:
    
    - In which directory
    
    - stateFileName
        - *ie : blabla ...* 
    - modesFileName
        - *ie : blabla ...* 
    - gieFileName
        - *ie : blabla ...* 
    - RIDFileName
        - *ie : blabla ...* 
    - weightsFileName
        - *ie : blabla ...* 


```python
outputDir = openfile_dialog()
print("OutputDir choosed : ")
outputDir
```

    OutputDir choosed : 





    '/home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test'




```python
fileOutPutNames = {}
fileOutPutNames["stateFileName"] = "fullStates.state"
fileOutPutNames["modesFileName"] = "test_modes.txt"
fileOutPutNames["gieFileName"] = "fullGIE.txt"
fileOutPutNames["RIDFileName"] = "test_RID.txt"
fileOutPutNames["weightsFileName"] = "test_weight.txt"
print("fileOutPutNames choosed : ")
fileOutPutNames
```

    fileOutPutNames choosed : 





    {'RIDFileName': 'test_RID.txt',
     'gieFileName': 'fullGIE.txt',
     'modesFileName': 'test_modes.txt',
     'stateFileName': 'fullStates.state',
     'weightsFileName': 'test_weight.txt'}



- **Optionnal Parmeteres :**


```python
verbose = False
```

## Execution
***


We import the file containing our python script to make the reduction :


```python
from test_IPython_SofaLauncher import myMOR
```

We now initialize the script with all our previously declared variables :


```python
test = myMOR(originalScene, toAnimate, increment, breathTime , maxPull, tolModes, tolGIE, outputDir, fileOutPutNames, verbose)
```

    periodSavedGIE : 11 | nbTrainingSet : 128 | nbIterations : 88
    listSofaScene : 
    - MAXPULL : [40, 40, 40, 40]
    - ORIGINALSCENE : originalScene
    - nbIterations : 88
    - INCREMENT : [5, 5, 5, 5]
    - PHASE : [0, 0, 0, 0]
    - BREATHTIME : [10, 10, 10, 10]
    - TOANIMATE : ['nord', 'ouest', 'sud', 'est']
    - PERIODSAVEDGIE : [11, 11, 11, 11]


- **Phase 1**

   We modify the original scene to do the first step of MOR :   
   - We add animation to each actuators we want for our model 
   - And add a writeState componant to save the shaking resulting states  


```python
test.phase1()
```

    [140361149646592] processing threaded sofa task in: /tmp/sofa-launcher-FCRdYf/phase1_snapshots.py
    [140360685184768] processing threaded sofa task in: /tmp/sofa-launcher-0M7yDh/phase1_snapshots.py
    [140360693577472] processing threaded sofa task in: /tmp/sofa-launcher-O9hkLD/phase1_snapshots.py[140360701970176] processing threaded sofa task in: /tmp/sofa-launcher-AeXWPv/phase1_snapshots.py
    
    [140360685184768] processing threaded sofa task in: /tmp/sofa-launcher-3KCN5f/phase1_snapshots.py
    [140361149646592] processing threaded sofa task in: /tmp/sofa-launcher-kkWpvp/phase1_snapshots.py
    [140360701970176] processing threaded sofa task in: /tmp/sofa-launcher-IAdV0i/phase1_snapshots.py
    [140360693577472] processing threaded sofa task in: /tmp/sofa-launcher-1xixDw/phase1_snapshots.py
    [140360685184768] processing threaded sofa task in: /tmp/sofa-launcher-Uu9CKJ/phase1_snapshots.py
    [140361149646592] processing threaded sofa task in: /tmp/sofa-launcher-qqP_fG/phase1_snapshots.py
    [140360701970176] processing threaded sofa task in: /tmp/sofa-launcher-cqwyJs/phase1_snapshots.py
    [140360693577472] processing threaded sofa task in: /tmp/sofa-launcher-UgbBhT/phase1_snapshots.py
    [140360685184768] processing threaded sofa task in: /tmp/sofa-launcher-X0Lhgv/phase1_snapshots.py
    [140361149646592] processing threaded sofa task in: /tmp/sofa-launcher-NAULY1/phase1_snapshots.py
    [140360701970176] processing threaded sofa task in: /tmp/sofa-launcher-VOUgmA/phase1_snapshots.py
    [140360693577472] processing threaded sofa task in: /tmp/sofa-launcher-GhRvaB/phase1_snapshots.py
    PHASE 1 --- 16.9399449825 seconds ---


- **Phase 2**

    With the previous result we combine all the generated state files into one to be able to extract from it the different mode


```python
test.phase2()
```

    ###################################################
    Executing readStateFilesAndComputeModes.py
    
    Arguments :
    
         INPUT  :
         in stateFilePath         : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/
    			-stateFileName 			 : fullStates.state
         in initPositionFilename  : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/test_init.state
         with arguments           :
             -tolerance               : 0.001 
    
         OUTPUT :
         in modesFilePath         : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/
             -modesFileName           : test_modes.txt 
    
    ###################################################
    PHASE 2 --- 0.363211154938 seconds ---


- **Phase 3**

    We launch again a set of sofa scene with the sofa launcher with the same previous arguments but with a different scene

    This scene take the previous one and add the model order reduction component:
    - HyperReducedFEMForceField
    - MappedMatrixForceFieldAndMass
    - ModelOrderReductionMapping and produce an Hyper Reduced description of the model


```python
test.phase3()
```

    [140360421283584] processing threaded sofa task in: /tmp/sofa-launcher-uWi1Tj/phase2_prepareECSW.py[140360429676288] processing threaded sofa task in: /tmp/sofa-launcher-mDADH0/phase2_prepareECSW.py
    
     [140360412890880] processing threaded sofa task in: /tmp/sofa-launcher-pVmFTm/phase2_prepareECSW.py
    [140360202319616] processing threaded sofa task in: /tmp/sofa-launcher-gnNg4t/phase2_prepareECSW.py
    [140360429676288] processing threaded sofa task in: /tmp/sofa-launcher-4nzDq7/phase2_prepareECSW.py
    [140360202319616] processing threaded sofa task in: /tmp/sofa-launcher-5TEvL5/phase2_prepareECSW.py
    [140360412890880] processing threaded sofa task in: /tmp/sofa-launcher-GNrE8x/phase2_prepareECSW.py
     [140360421283584] processing threaded sofa task in: /tmp/sofa-launcher-CHprr_/phase2_prepareECSW.py
    [140360429676288] processing threaded sofa task in: /tmp/sofa-launcher-B4R9QC/phase2_prepareECSW.py
    [140360412890880] processing threaded sofa task in: /tmp/sofa-launcher-aKQaLE/phase2_prepareECSW.py
    [140360421283584] processing threaded sofa task in: /tmp/sofa-launcher-cOju1m/phase2_prepareECSW.py
    [140360202319616] processing threaded sofa task in: /tmp/sofa-launcher-WrOfXk/phase2_prepareECSW.py
    [140360429676288] processing threaded sofa task in: /tmp/sofa-launcher-IUyZVJ/phase2_prepareECSW.py
    [140360421283584] processing threaded sofa task in: /tmp/sofa-launcher-UIaidA/phase2_prepareECSW.py
    [140360412890880] processing threaded sofa task in: /tmp/sofa-launcher-fH5U1a/phase2_prepareECSW.py
    PHASE 3 --- 48.6978330612 seconds ---


- **Phase 4**

    Final step : we gather again all the results of the previous scenes into one and then compute the RID and Weigts with it. 
    Additionnally we also compute the Active Nodes



```python
test.phase4()
```

    ###################################################
    Executing readGieFileAndComputeRIDandWeights.py
    
    Arguments :
    
         INPUT  :
         in gieFilename    : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/fullGIE.txt
         with arguments    :
             -tolerance        : 0.05 
    
         OUTPUT :
         in pathToWeightsAndRIDdir : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/
             -RIDFileName                : test_RID.txt
             -weightsFileName            : test_weight.txt 
    
    ###################################################
    [########################################] 100.0% Compute Weight&RID
    ###################################################
    Executing convertRIDinActiveNodes.py
    
    Arguments :
    
         INPUT  :
         in pathToWeightsAndRIDdir    : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/
             -RIDFileName                : test_RID.txt
             -connectivityFileName       : saved_elements.txt
         OUTPUT :
         in pathToWeightsAndRIDdir    : /home/felix/SOFA/plugin/ModelOrderReduction/examples/Tests/2_OUTPUT/Test/
             -listActiveNodesFileName    : conectivity.txt 
    
    ###################################################
    PHASE 4 --- 39.539689064 seconds ---
    


## Results
***



```bash
%%bash
runSofa phase3_reducedModel.py
```
