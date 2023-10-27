# Dependencies

Model order reduction dependencies required and optional and what they are used for.

::::::{dropdown} REQUIRED
:open:
:animate: fade-in-slide-down
:color: warning
:icon: alert-fill
:margin: 0

:::::{grid} 2
:gutter: 1
:margin: 0

::::{grid-item-card}
:margin: 0

SOFA

:::{dropdown} <a href="https://www.sofa-framework.org/" target="_blank"><b>SOFA itself</b></a>
:animate: fade-in-slide-down
:icon: info

This work is a plugin of [SOFA](https://www.sofa-framework.org/) which a simulation software. 
For the moment we haven't got any pre-made SOFA version with our work so the first thing you will need to do is compile SOFA
:::

:::{dropdown} <a href="https://github.com/sofa-framework/sofa/tree/master/tools/sofa-launcher" target="_blank"><b>Sofa Launcher</b></a>
:animate: fade-in-slide-down
:icon: info

We use a tool of SOFA named **sofa-launcher** allowing us to gain a lot of calculation time thanks to parallel execution of multiple SOFA scene.
:::

:::{dropdown} <a href="https://github.com/SofaDefrost/STLIB" target="_blank"><b>STLIB</b></a>
:animate: fade-in-slide-down
:icon: info

Plugin easing the way to write SOFA scene in python.
We use some utilities of this plugin to reduce our model, especially the {class}`stlib:stlib.scene.Wrapper`  feature.
:::

::::

::::{grid-item-card}
:margin: 0

PYTHON

:::{dropdown} <a href="https://www.python.org/downloads/" target="_blank"><b>Python 3.X</b></a>
:animate: fade-in-slide-down
:icon: info

python3 version
:::

:::{dropdown} <a href="http://cheetahtemplate.org/" target="_blank"><b>Cheetah</b></a>
:animate: fade-in-slide-down
:icon: info

Cheetah is needed in order to use the **sofa-launcher** of SOFA.
:::

:::{dropdown} <a href="https://pypi.org/project/PyYAML/" target="_blank"><b>yaml</b></a>
:animate: fade-in-slide-down
:icon: info

python3 version
:::

::::
:::::

::::::

<br>

--------------------------------------------------------------------------

<br>

::::{dropdown} OPTIONAL
:open:
:animate: fade-in-slide-down
:color: light
:icon: plus-circle


:::{dropdown} <a href="https://github.com/SofaDefrost/SoftRobot" target="_blank"><b>SoftRobot</b></a>
:animate: fade-in-slide-down
:icon: info

Plugin easing the way to write SOFA scene in python.
We use some utilities of this plugin to reduce our model, especially the {doc}`constraints component  <softrobotscomponents:_autosummary/component.constraint>` feature.
:::

:::{dropdown} <a href="https://pypi.org/project/PyQt5/" target="_blank"><b>PyQt5</b></a>
:animate: fade-in-slide-down
:icon: info

We use pyqt5 for our interface
:::

:::{dropdown} <a href="http://jupyter.readthedocs.io/en/latest/install.html" target="_blank"><b>Jupyter</b></a>
:animate: fade-in-slide-down
:icon: info

To learn how to reduce your own model we have done a tutorial which will make you learn step by step the process. For this interactive tutorial we use
a [python notebook](https://ipython.org/notebook.html).
:::

::::

