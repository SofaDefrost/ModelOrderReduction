# MOR Library

Here we can put the results of reduction as python module 
to ease their usage inside other scene by just importing them.

## How to do 

When performing the reduction there is a option called **addToLib** set by default to `False`.
Just put it to `True` then at the end of the reduction process everything will be copied into this 
directory and the **__init__.py** file will be changed to import them properly.

## How to use 

After having doing that you can then do in your scene the following :

```
from morlib.reduced_MyModelReduced import Reduced_MyModelReduced 

def createScene(rootNode):

    Reduced_MyModelReduced(rootNode,
                    name="MyModelReduced",
                    rotation=[-90, 0.0, 0.0],
                    translation=[0, 50.0, 0.0],
                    surfaceColor=[0.5, 0.5, 0.5, 0.5])
```