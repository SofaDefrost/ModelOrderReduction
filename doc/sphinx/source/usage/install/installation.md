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

to confirm all the previous steps verify with *this example* the proper functioning of the plugin