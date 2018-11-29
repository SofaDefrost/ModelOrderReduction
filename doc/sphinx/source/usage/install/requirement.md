# Requirement

This work is a plugin of [SOFA](https://www.sofa-framework.org/) which a simulation software.
For the moment we haven't got any pre-made SOFA version with our work so the first thing you will need to do is compile SOFA

## Step 1: Compile SOFA

For that follow these [instructions](https://www.sofa-framework.org/community/doc/getting-started/build/linux/) (here is for linux but instruction exist for Mac & Windows also)

## Step 2: Install Required dependencies

### Ubuntu

------------------------------------------------------------------------------------------------
**SOFA Plugin Dependencies**

(The best way to add plugin to SOFA is explained [here](https://www.sofa-framework.org/community/doc/using-sofa/build-a-plugin/))

- [STLIB](https://github.com/SofaDefrost/STLIB)

	Plugin easing the way to write SOFA scene in python.
	We use some utilities of this plugin to reduce our model, especially the [wrapper](linkTodoc) feature.

	```
	git clone https://github.com/SofaDefrost/STLIB.git
	```

	<span style="color:orange">*optional* </span>

	- [SoftRobots](https://github.com/SofaDefrost/SoftRobots)

		The different examples present in the plugin are based on scene requiring SoftRobots

		```
		git clone https://github.com/SofaDefrost/SoftRobots.git
		```

------------------------------------------------------------------------------------------------
**Package dependencies**

<span style="color:red">*version of python used* </span>

- [Python 2.7.X](https://www.python.org/downloads/)

<span style="color:red">*Install all* </span>

```
sudo apt-get install python-cheetah python-pyqt4 python-yaml
```

<span style="color:red">*then add to your .bashrc* </span>

```
export PYTHONPATH=/PathToYourSofaSrcFolder/tools/sofa-launcher
```

------------------------------------------------------------------------------------------------
**If you don't want to install all the dependencies, here a description of them separately:**

*to reduce model*

- Sofa Launcher

	We use a tool of SOFA named **sofa-launcher** allowing us to gain a lot of calculation time thanks to parallel execution of multiple SOFA scene.
	For that you have to add to your *.bashrc* in the end the following line:

	```
	export PYTHONPATH=/PathToYourSofaSrcFolder/tools/sofa-launcher
	```

	- [Cheetah](http://cheetahtemplate.org/)

		Cheetah is needed in order to use the **sofa-launcher** of SOFA.

		```
		sudo apt-get install python-cheetah
		```

*To use the gui*

- [PyQt](https://wiki.python.org/moin/PyQt)

	We use pyqt4 for our interface

	```
	sudo apt-get install python-pyqt4
	```

- yaml

	```
	sudo apt-get install python-yaml
	```

*To test our notebook*

To learn how to reduce your own model we have done a tutorial which will make you learn step by step the process. For this interactive tutorial we use 
a [python notebook](https://ipython.org/notebook.html).

So to be able to do it please install [jupyter](http://jupyter.readthedocs.io/en/latest/install.html)

the easiest way:
```
pip install jupyter
```
------------------------------------------------------------------------------------------------

### OSX

*TODO*

### Windows

*TODO*