# Model Order Reduction NoteBook

## Introduction <a name="introduction"></a>

In this python notebook exemple we will see with 2 real examples how to reduce a model from one of your sofa scene thanks to the **Model Order Reduction** plugin done by the INRIA research team **Defrost**.

the two examples will be :

- **[A cable-driven silicone robot](https://modelorderreduction.readthedocs.io/en/latest/usage/examples/Diamond/diamond.html)** (*paper link : [C. Duriez, ICRA, 2013](https://hal.archives-ouvertes.fr/hal-00823766/document)*).

![Diamond robot](../examples/Diamond/diamondReal.png)

- **[A pneumatic Soft Robot](https://modelorderreduction.readthedocs.io/en/latest/usage/examples/Starfish/starfish.html)** (*paper link : Multigait soft Robot [R.F. Shepherd et al, PNAS, 2011](http://www.pnas.org/content/108/51/20400)*).

![Starfish robot](../examples/Starfish/Starfish_Real.png)

After these expample presentation we can now proceed to the reduction.
First we have to prepare it by setting a bunch of parameters while explaining there purpose (here the parameters will be set twice, one for the diamond and one for the starfish so you will be able to switch easily between each example)

## User Paramters <a name="User Paramters"></a>

Before defining the reduction parameters, here are some "import" commands that will be useful for this python notebook:


```python
# Import
import os
import sys

sys.path.append(os.getcwd()+'/../python')

# MOR IMPORT
from mor.gui import utility
from mor.reduction import ReduceModel
from mor.reduction.container import ObjToAnimate
```

### 1.  Paths to the SOFA scene, mesh and outputs: <a name="Important Path"></a>
- The scene you want to work on
- The folder where you want the results to be put in


```python
# Select Output Dir and original scene name & path
from PyQt5 import QtWidgets
app = QtWidgets.QApplication(sys.argv)

originalScene = utility.openFileName('Select the SOFA scene you want to reduce')
outputDir = utility.openDirName('Select the directory that will contain all the results')

# If you haven't installed PyQt the previous function won't work
# As an alternative you can enter the absolute path to the corresponding files directly:
# originalScene = /PathToMy/Original/Scene
```

### 2.  The different reduction parameters <a name="Reduction Parameters"></a>

#### nodeToReduce <a name="nodesToReduce"></a>

   
   contains the SOFA path from the rootnode to the model you want to reduce.


```python
nodesToReduce_DIAMOND = ['/modelNode']
nodesToReduce_STARFISH =['/model']
```

#### listObjToAnimate <a name="listObjToAnimate"></a>
   
Contains a list of objects from the class [ObjToAnimate](https://modelorderreduction.readthedocs.io/en/latest/_autosummary/_autosummary/_autosummary/mor.reduction.reduceModel.ObjToAnimate.html).
        
An ObjToAnimate will define an object to "animate" during the shaking.

There are 3 main parameters to this object :
- location: Path to obj/node we want to animate.
- animFct: the animation function we will use (here we use [defaultShaking](https://modelorderreduction.readthedocs.io/en/latest/_autosummary/_autosummary/mor.animation.defaultShaking.html)).
- all the arguments that will be passed to the animFct we have chosen.
        
For example, here we want to animate the node named "north", but we won't specify the animFct so the default animation function will be used and applied to the first default object it will find. The default function will need 3 additional parameters :
- incrPeriod (float):	Period between each increment
- incr (float):    Value of each increment
- rangeOfAction (float):	Until which value the data will increase
            
north = ObjToAnimate("north", incr=5,incrPeriod=10,rangeOfAction=40)


```python
# animation parameters

### CABLE-DRIVEN PARALLEL ROBOT PARAMETERS
north = ObjToAnimate("modelNode/north", incr=5,incrPeriod=10,rangeOfAction=40)
south = ObjToAnimate("modelNode/south", incr=5,incrPeriod=10,rangeOfAction=40)
east = ObjToAnimate("modelNode/east", incr=5,incrPeriod=10,rangeOfAction=40)
west = ObjToAnimate("modelNode/west", incr=5,incrPeriod=10,rangeOfAction=40)
listObjToAnimate_DIAMOND = [north,south,east,west]

### MULTIGAIT SOFT ROBOT PARAMETERS
centerCavity = ObjToAnimate("model/centerCavity", incr=350,incrPeriod=2,rangeOfAction=3500)
rearLeftCavity = ObjToAnimate("model/rearLeftCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
rearRightCavity = ObjToAnimate("model/rearRightCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
frontLeftCavity = ObjToAnimate("model/frontLeftCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
frontRightCavity = ObjToAnimate("model/frontRightCavity", incr=200,incrPeriod=2,rangeOfAction=2000)
listObjToAnimate_STARFISH = [centerCavity,rearLeftCavity,rearRightCavity,frontLeftCavity,frontRightCavity]
```

#### Modes parameters <a name="Modes parameters"></a>

- addRigidBodyModes (Defines if our reduce model will be able to translate along the x, y , z directions)
- tolModes ( Defines the level of accuracy we want to select the reduced basis modes)


```python
addRigidBodyModes_DIAMOND = [0,0,0]
addRigidBodyModes_STARFISH = [1,1,1]

tolModes = 0.001
```

- tolGIE

   tolerance used in the greedy algorithm selecting the reduced integration domain(RID). Values are between 0 and 0.1 . High values will lead to RIDs with very few elements, while values approaching 0 will lead to large RIDs.  Typically set to 0.05.


```python
# Tolerance
tolGIE =  0.05
```

### 3 -- Optional parameters <a name="Optionnal Parameters"></a>


```python
# Optionnal
verbose = False
nbrCPU = 4
packageName = 'test'
addToLib = False
```

- verbose

   can bring more useful log while doing a reduction.

- nbrCPU

   depending on the number of ObjToAnimate you have previously declared, the reduction process will need to launch many sofa scenes with different animation patterns. To do that faster we can parallelise this process by indicating a number of CPU and doing so the number of scenes that will be run simultaneously.

- addToLib & packageName

   These 2 variables are to be used if you want at the end of the reduction to create a reusable python module of the result that will be placed in `/python/morlib` to import and use it easily in your scene.


We can now execute one of the reductions we choose with all these parameters

## Execution <a name="Execution"></a>


### Initialization

The execution is done with an object from the class {py:class}`.ReduceModel`.
we initialize it with all the previous argument either for the Diamond or Starfish example


```python
# Initialization of our script
nodesToReduce = nodesToReduce_DIAMOND # nodesToReduce_STARFISH
listObjToAnimate = listObjToAnimate_DIAMOND # listObjToAnimate_STARFISH
addRigidBodyModes = addRigidBodyModes_DIAMOND # addRigidBodyModes_STARFISH

reduceMyModel = ReduceModel(    originalScene,  
                                nodesToReduce,
                                listObjToAnimate,
                                tolModes,tolGIE,
                                outputDir,
                                packageName = packageName,
                                addToLib = addToLib,
                                verbose = verbose,
                                addRigidBodyModes = addRigidBodyModes)
```

We can finally perform the actual reduction.

### {py:meth}`.phase1`

We modify the original scene to do the first step of MOR :
- We add animation to each actuators we want for our model
- And add a writeState componant to save the shaking resulting states


```python
reduceMyModel.phase1()
```

### {py:meth}`.phase2`

With the previous result we combine all the generated state files into one to be able to extract from it the different mode


```python
reduceMyModel.phase2()
```

```python
print("Maximum number of Modes : ")
reduceMyModel.reductionParam.nbrOfModes
```

### {py:meth}`.phase3`

We launch again a set of sofa scene with the sofa launcher with the same previous arguments but with a different scene

This scene take the previous one and add the model order reduction component:
- HyperReducedFEMForceField
- MechanicalMatrixMapperMOR
- ModelOrderReductionMapping and produce an Hyper Reduced description of the model


```python
reduceMyModel.phase3()
```

### {py:meth}`.phase4`

Final step : we gather again all the results of the previous scenes into one and then compute the RID and Weigts with it. Additionnally we also compute the Active Nodes



```python
reducedScene = reduceMyModel.phase4()
```

End of example you can now go test the results in the folder you have designed at the beginning of this tutorial

## To go Further <a name="To go Further"></a>

Links to additional information about the plugin:

**[Publication in IEEE Transactions On Robotics](https://hal.inria.fr/hal-01834483)**

**[Plugin website](https://project.inria.fr/modelorderreduction/)**

**[Plugin doc](https://modelorderreduction.readthedocs.io/en/latest/index.html)**
