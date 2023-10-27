# Setup & Get Sarted

::::::{card}
**SOFA setup**
^^^
Card content

You can either build it from sources:

::::{grid} 2

:::{grid-item-card}
:columns: auto
:shadow: none
:class-card: sd-border-0
```{button-link} https://github.com/sofa-framework/sofa
:color: primary
:outline:
:tooltip: github-repo
{octicon}`mark-github;1em;github-repo`
```
:::
:::{grid-item-card}
:columns: auto
:shadow: none
:class-card: sd-border-0
```{button-link} https://www.sofa-framework.org/community/doc/getting-started/build/linux/
:color: primary
:outline:
:tooltip: doc-how-to
{octicon}`book;1em;doc-how-to`
```
:::
::::

:::::

Or download the binaries:

::::{grid} 1

:::{grid-item-card}
:columns: auto
:shadow: none
:class-card: sd-border-0
```{button-link} https://www.sofa-framework.org/download/
:color: primary
:outline:
:tooltip: binaries-download
{octicon}`download;1em;download`
```
:::
::::

::::::

:::::::{card}
**ModelOrderReduction setup**
^^^
Card content

You can either build it from the [source](https://github.com/SofaDefrost/ModelOrderReduction) as explained [here](https://www.sofa-framework.org/community/doc/plugins/build-a-plugin-from-sources/) with SOFA.
Or take the binaries generated [here](https://github.com/SofaDefrost/ModelOrderReduction/releases/tag/release-master) and link them to your SOFA build/binaries.

::::::{tab-set}

:::::{tab-item} Ubuntu
<br>

::::{card}
*Python install*
^^^

::::{tab-set}

:::{tab-item} minimal

```console
  sudo apt-get install python-cheetah python-yaml
```
:::

:::{tab-item} all

```console
  sudo apt-get install python-cheetah python-yaml python-pyqt5 notebook
```
:::
::::
::::

::::{card}
*PythonPath*
^^^

Then don't forget to add into your pythonPath the sofa launcher.
To do that in a definitive way add this line at the end of your shell configuration file (usually *.bashrc*)

```console
export PYTHONPATH=$PYTHONPATH:/PathToYourSofaSrcFolder/tools/sofa-launcher
```
::::
:::::

:::::{tab-item} Windows
🚧 
:::::

:::::{tab-item} Mac
🚧
:::::

::::::

:::::::

## Try some exemples

To confirm all the previous steps and verify that the plugin is working properly you can launch the *test_component.py* SOFA scene situated in:

```
/ModelOrderReduction/tools
```

This example show that after the reduction of a model (here the 2 examples {doc}`Diamond Robot </usage/examples/Diamond/diamond>`,
{doc}`Starfish robot </usage/examples/Starfish/starfish>`), you can re-use it easily as a python object with different arguments 
allowing positionning of the model in the SOFA scene.