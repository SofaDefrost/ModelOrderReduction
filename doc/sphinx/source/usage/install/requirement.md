# Requirement

This work is a plugin of [SOFA](https://www.sofa-framework.org/) which a simulation software.
For the moment we haven't got any pre-made SOFA version with our work so the first thing you will need to do is compile SOFA

## Step 1: Compile SOFA

For that follow these [instruction](https://www.sofa-framework.org/community/doc/getting-started/build/linux/) (here is for linux but instruction exist for MAc & Windows also)
Before compiling it you have to check in CMake-gui the option : ***SOFA_WITH_EXPERIMENTAL_FEATURES*** (will be removed in the future)


## Step 2: Install Required dependencies

### Ubuntu

- [Python 2.7.X](https://www.python.org/downloads/)


- [Cheetah](http://cheetahtemplate.org/)

```
sudo apt-get update
sudo apt-get install python-cheetah
```

- [PyQt](https://wiki.python.org/moin/PyQt)

```
sudo apt-get install python-pyqt5
```

- SOFA Plugin Dependencies

	(The best way to add plugin to SOFA is explained here <https://www.sofa-framework.org/community/doc/using-sofa/build-a-plugin/>)

	[STLIB](https://github.com/SofaDefrost/STLIB) with branch *stdlib_wrapper*

	Plugin easing the way to write SOFA scene in python

	```
	git clone -b stdlib_wrapper https://github.com/SofaDefrost/STLIB.git
	```

	*optional:*

	[SoftRobots](https://github.com/SofaDefrost/SoftRobots) with branch *Documentation*

	The different examples present in the plugin are based on scene requiring SoftRobots

	```
	git clone -b Documentation https://github.com/SofaDefrost/SoftRobots.git
	```

- Sofa Launcher

	We use a tool of SOFA named **sofa-launcher** allowing us to gain a lot of calculation time thanks to parallel execution of multiple SOFA scene.
	For that you have to add to your *.bashrc* in the end the following line:

	```
	export PYTHONPATH=/PathToYourSofaSrcFolder/tools/sofa-launcher
	```

### OSX

*TODO*

### Windows

*TODO*

### Optionnal

To learn how to reduce your own model we have done a tutorial which will make you learn step by step the process. For this interactive tutorial we use 
a [python notebook](https://ipython.org/notebook.html).

So to be able to do it please install [jupyter](http://jupyter.readthedocs.io/en/latest/install.html)

the easiest way:
```
pip install jupyter
```