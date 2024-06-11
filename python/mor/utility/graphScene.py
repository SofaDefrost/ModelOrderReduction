# -*- coding: utf-8 -*-
'''
**Set of functions to extract the graph a scene**

The extracted results will be put into 2 dictionnary as follow

.. code-block:: python

    tree:
        node1:
            child1:
        node2:
            child2:

    obj:
        node1:
            obj1:
        child1:
            obj2
        node2:
            obj3

-------------------------------------

'''

import os
import yaml

try:
    from launcher import SerialLauncher, startSofa
except:
    raise ImportError("You need to give to PYTHONPATH the path to sofa-launcher in order to use this tool\n"\
                     +"Enter this command in your terminal (for temporary use) or in your .bashrc to resolve this:\n"\
                     +"export PYTHONPATH=/PathToYourSofaSrcFolder/tools/sofa-launcher")

def getGraphScene(node,getObj=False):
    '''
    **This function will iterate over the SOFA graph scene from a node
    and build from there 2 dictionnaries containing its content**

    +----------+-----------+-------------------------------------------------------------------+
    | argument | type      | definition                                                        |
    +==========+===========+===================================================================+
    | node     | Sofa.node | From which node we want the graph                                 |
    +----------+-----------+-------------------------------------------------------------------+
    | getObj   | bool      | Boolean to choose if we want the node/obj as key or just its name |
    +----------+-----------+-------------------------------------------------------------------+
    '''

    class Namespace(object):
        pass
    tmp = Namespace()
    tmp.results = {}
    tmp.results["tree"] = {}
    tmp.results["obj"] = {}
    # tmp.results = None

    def buildTree(node,dic):
        if node.name.value != "root":
            if getObj:
                dic[node] = {}
            else:
                dic[node.name.value] = {}
                # dic = AnyNode(node.name = )
        for child in node.children:
            if node.name.value != "root":
                if getObj:
                    buildTree(child,dic[node])
                else:
                    buildTree(child,dic[node.name.value])
            else:
                buildTree(child,dic)
    def objTree(node,dic):

        if getObj:
            dic[node] = {}
        else:
            dic[node.name.value] = {}

        for obj in node.objects:
            # print('root '+str(type(obj).__name__)+' '+obj.getName())

            if getObj:
                dic[node][obj] = obj.getClassName()
            else:
                dic[node.name.value][obj.getName()] = obj.getClassName()

        for child in node.children:
            if getObj:
                objTree(child,dic)
            else:
                objTree(child,dic)

    buildTree(node,tmp.results["tree"])
    # print(tmp.results["tree"])
    objTree(node,tmp.results["obj"])
    # print(tmp.results["obj"])

    # for key in tmp.results:
    #     print(str(key)+' : '+str(tmp.results[key])+'\n')

    return tmp.results

def dumpGraphScene(node,fileName='graphScene.yml'):
    '''
    **Dump the Graph of the SOFA scene as 2 dictionnaries in a yaml file**

    +----------+-----------+--------------------------------------+
    | argument | type      | definition                           |
    +==========+===========+======================================+
    | node     | Sofa.node | From which node we want the graph    |
    +----------+-----------+--------------------------------------+
    | fileName | str       | In which File we will put the result |
    +----------+-----------+--------------------------------------+
    '''

    data = getGraphScene(node)
    with open(fileName, 'w') as ymlfile:
        yaml.dump(data,ymlfile, default_flow_style=False)

def importScene(filePath):
    '''
    **Return the graph of a SOFA scene**

    Thanks to the SOFA Launcher, it will launch a templated scene that 
    will extract from an original scene its content as 2 dictionnaries containing\:

    * The different Sofa.node of the scene keeping there hierarchy.
    * All the SOFA component contained in each node with the node.name as key.

    +----------+------+---------------------------------+
    | argument | type | definition                      |
    +==========+======+=================================+
    | filePath | str  | Absolute path to the SOFA scene |
    +----------+------+---------------------------------+
    '''
    numiterations = 1
    filename = "importScene.py"
    path = os.path.dirname(os.path.abspath(__file__))+'/template/'
    filesandtemplates = [ (open(path+filename).read(), filename)]

    listSofaScene = [
                        {"ORIGINALSCENE": filePath,
                         "nbIterations":numiterations}
                    ]

    results = startSofa(listSofaScene, filesandtemplates, launcher=SerialLauncher())

    with open(results[0]["directory"]+'/graphScene.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile,Loader=yaml.FullLoader)

    return cfg