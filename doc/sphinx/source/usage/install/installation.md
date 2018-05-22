# Install & Get Sarted
***

## Download

Now that you have a compiled & working SOFA, we can add our plugin.

- Create a directory where you will put it
- Move into it and clone our last working version: 

```
git clone https://github.com/SofaDefrost/ModelOrderReduction
```

## Install

- Add it to SOFA

    - With CMake-gui add to the key **SOFA_EXTERNAL_DIRECTORIES** the path to your folder
    - Then Configure, Generate and verify that it has been added (normally a message will pass in the console of CMake-gui)


- Re-compile SOFA 

## Launch test

To confirm all the previous steps and verify that the plugin is working properly you can launch the *test_component.py* SOFA scene situated in:
```
/ModelOrderReduction/tools
```

This example show that after the reduction of a model (here the 2 examples [Diamond robot](../examples/Diamond/diamond.html#diamond),
[Starfish robot](../examples/Starfish/starfish.html#starfish)), you can re-use it easily as a python object with different arguments 
allowing positionning of the model in the SOFA scene.