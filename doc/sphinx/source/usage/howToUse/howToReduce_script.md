# Using script 

## Python: modelOrderReduction.py

In the root of the */tools* folder there is a python file called **modelOrderReduction.py**.
In it, there are already several parameters allowing to reduce, if un-commented, the different 
examples that are present in */examples* by giving the path to the corresponding SOFA scene with the variable `originalScene`.

To understand and know how to use the different parameters you can refer to the following section 
that is just a copy/paste of what you can find in the noteBook.

The noteBook is great to understand what's happening by performing reduction on the given examples 
but after that it is much more practical to use **modelOrderReduction.py** to do your own reduction.

To proceed you need to add and fill the following variable according to the scene you want to reduce:
```python
nodeToReduce = '/PathToNodeToReduce'
myAnim1 = ObjToAnimate("pathToComponentToAnimate","animationFctYouWillAnimateWith",
                       incr=1,incrPeriod=2,rangeOfAction=10,dataToWorkOn="onWhichDataFieldYouWillWork",
                       kwargs=...) #additionalArgumentSpecificToTheAnimationFct
myAnim2 = ...
.
.
listObjToAnimate = [myAnim1,myAnim2,...]
addRigidBodyModes = [0,0,0] # add translation dof in your reduce model in the different axis if put to 1 if not will stay fixed
```

Then we recommend if it's the first time you reducing a particular model, to proceed step by step by uncommenting the different phase instead 
of using `reduceMyModel.performReduction()` which will do them all in one go.

```python
reduceMyModel.phase1()
#reduceMyModel.phase2()
#reduceMyModel.phase3()
#reduceMyModel.phase4()
```

This way you will be able to check any issue along the way. Particularly after `phase1` & `phase3` where we launch SOFA 
with the animation parameters you've given. In the batch you will have the following display: 

```batch
periodSaveGIE : 6 | nbTrainingSet : 8 | nbIterations : 89
##################################################
[133985141249600] processing threaded sofa task in: /tmp/sofa-launcher-6a70jp_x/phase1_snapshots.py
[133983935379008] processing threaded sofa task in: /tmp/sofa-launcher-ma1p72bd/phase1_snapshots.py
.
.
```

This means that it's creating multiple instance of your scene with different animation configuration and playing 
them in parallel to get out of it data to construct the reduced model.
So if at the end of `phase1` & `phase3` you have error don't hesitate to go into these temporary folders to see directly what's happening really.
Most probably the animation is not well configured or the modification of your intial scene went wrong.
If `phase1` & `phase3` went well `phase2` & `phase4` should to.

After `phase4`, in the folder you have chosen to put the reduction results, you should now have a file named **reduced_packageName.py**.
This python file try to create a function allowing you to instantiate easily the reduce model into your previous scene:

```python
def Reduced_test(
                  attachedTo=None,
                  name="Reduced_test",
                  rotation=[0.0, 0.0, 0.0],
                  translation=[0.0, 0.0, 0.0],
                  scale=[1.0, 1.0, 1.0],
                  surfaceMeshFileName=False,
                  surfaceColor=[1.0, 1.0, 1.0],
                  nbrOfModes=32,
                  hyperReduction=True):
    modelRoot = attachedTo.addChild(name)
    .
    .
    .
    return modelNode
```

:::{warning}
The creation of this function is a complicated process and is prone to errors. 
This is just a tool to help you but keep in mind that the real reduced model is contained 
in the **/data** folder produced after the reduction, you "just" need to give the data files to the MOR component.
To the **hyperreduced forcefield** the *modes*, *RID* and *weights* files. To the **ModelOrderReductionMapping** the *modes* file only.  
```python
modelNode.addObject('HyperReducedTetrahedronFEMForceField' ,
                       nbModes = nbrOfModes, performECSW = True, 
                       modesPath = path + '/data/modes.txt', 
                       RIDPath = path + '/data/reducedFF_modelNode_0_RID.txt', 
                       weightsPath = path + '/data/reducedFF_modelNode_0_weight.txt')
modelNode.addObject('ModelOrderReductionMapping' , 
                       input = '@../MechanicalObject', output = '@./dofs',
                       modesPath = path + '/data/modes.txt')
```
:::

At the end of this file there is a generic scene that is created to test it:

```python
def createScene(rootNode):
    surfaceMeshFileName = False

    MainHeader(rootNode,plugins=["SoftRobots","ModelOrderReduction"],
                        dt=1.0,
                        gravity=[0.0, 0.0, -9810.0])
    rootNode.VisualStyle.displayFlags="showForceFields"
    
    Reduced_test(rootNode,
                        name="Reduced_test",
                        surfaceMeshFileName=surfaceMeshFileName)
```

:::{warning}
The behavior is generic so it can be normal that you have a different behavior compared to your original scene, this one is just for testing.
:::

You can now `import Reduced_test` anywhere to use it either into your original scene or some new ones.

## NoteBook: modelOrderReduction.ipynb

```{note} 	
The following tutorial comes from a python-notebook.
If you want to make the tutorial interactively go directly to:

``/ModelOrderReduction/tools/notebook``

then, if you have installed jupyter like explained in the requirement, open a terminal there and launch a session:

``jupyter notebook``

It will open in your web-browser a tab displaying the current files in the directory. Normally you should have one called **modelOrderReduction.ipynb**

You can click on it and follow the tutorial
```

```{toctree}
:maxdepth: 2

noteBook

```

## Manually 

The 2 methods presented previously and the API used can help you create your reduced model but depending on 
your situation it may not be suited.

Instead you still have the possibility to perform all of this manually.
- Launch your scene put the component **writeState** in it, run it and stimulate your model as you want (with script or mouse interaction).
- Get the resulting state file, give it to the script {py:meth}`mor.reduction.script.readStateFilesAndComputeModes` to compute the modes
- Then with these modes re-launch your scene after changing it to have a mapping with **modelorderreductionmapping** between 
your full model and the modes and change your forcefield for an hyperreduced one specifying `prepareECSW=True` run it, and try stimulating preferably the same way as before.
It will this time generate a **GIE** file.
- Give it to the script {py:meth}`mor.reduction.script.readGieFileAndComputeRIDandWeights` to compute the RID & weights.

You now have all you need for your reduce model ! Change your original scene with MOR component and give them the different data produced. 
