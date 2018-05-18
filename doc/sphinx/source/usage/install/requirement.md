# Requirement

This work is a plugin of [SOFA](https://www.sofa-framework.org/) which a simulation software.
For the moment we haven't got any pre-made SOFA version with our work so the first thing you will need to do is compile SOFA

## Step 1: Compile SOFA

For that follow these [instruction](https://www.sofa-framework.org/community/doc/getting-started/build/linux/) (here is for linux but instruction exist for MAc & Windows also)
Before compiling it you have to check in CMake-gui the option : ***SOFA_WITH_EXPERIMENTAL_FEATURES*** (will be removed in the future)


## Step 2: Install Required dependencies

### Ubuntu

- [Cheetah](http://cheetahtemplate.org/)

```
sudo apt-get update
sudo apt-get install python-cheetah
```

- [PyQt](https://wiki.python.org/moin/PyQt)

```
sudo apt-get install python-pyqt5
```

### OSX

*TODO*

### Windows

*TODO*

### Optionnal

To learn how to reduce your own model we have done a tutorial which will make you learn step by step the process. For this interactive tutorial we use 
a [python notebook](https://ipython.org/notebook.html).

So to be able to do it please install [jupyter](http://jupyter.readthedocs.io/en/latest/install.html)