# ModelOrderReduction

This Sofa package contains c++ components with python utilitaries allowing
to perform model reduction and use these reduced model in Sofa scene.

Our complete documentation is hosted [here](https://modelorderreduction.readthedocs.io/en/latest/index.html) using [readthedocs](https://readthedocs.org/) services.

You can also explore the *examples* directory in the repository *doc/examples/* where there are complete robot you can control which are completely or partially reduced.

## AUTHOR :

 - [Team DEFROST (INRIA/CRISTAL), Lille](https://team.inria.fr/defrost/)


## LICENCE :

 - [GPL 2](LICENSE)

## Prerequisite

- SOFA Plugin Dependencies

	- [STLIB](https://github.com/SofaDefrost/STLIB)


	- *optional:*

	 	- [SoftRobots](https://github.com/SofaDefrost/SoftRobots)

- Package dependencies

	- [Python 2.7.X](https://www.python.org/downloads/)

	- For the GUI:

		- [PyQt4](https://wiki.python.org/moin/PyQt) *(optional)*

		- [yaml](https://pypi.org/project/PyYAML/)

	- Sofa Launcher (to reduce) :

		- [Cheetah](http://cheetahtemplate.org/)

		```
		export PYTHONPATH=/PathToYourSofaSrcFolder/tools/sofa-launcher
		```

More informations in **[requirement](https://modelorderreduction.readthedocs.io/en/latest/usage/install/requirement.html)** section of our doc
