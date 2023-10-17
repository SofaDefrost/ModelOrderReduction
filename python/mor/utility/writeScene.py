# -*- coding: utf-8 -*-
###############################################################################
#            Model Order Reduction plugin for SOFA                            #
#                         version 1.0                                         #
#                       Copyright © Inria                                     #
#                       All rights reserved                                   #
#                       2018                                                  #
#                                                                             #
# This software is under the GNU General Public License v2 (GPLv2)            #
#            https://www.gnu.org/licenses/licenses.en.html                    #
#                                                                             #
#                                                                             #
#                                                                             #
# Authors: Olivier Goury, Felix Vanneste                                      #
#                                                                             #
# Contact information: https://project.inria.fr/modelorderreduction/contact   #
###############################################################################
"""
**Set of functions to create a reusable SOFA component out of a SOFA scene**

------------------------------------------------------------------
"""

import os
import sys
import platform

slash = '/'
if "Windows" in platform.platform():
    slash ='\\'

path = os.path.dirname(os.path.abspath(__file__))+'/template/'

def writeHeader(packageName,nbrOfModes):
    """
    **Write a templated Header to a file**

    **Arg:**

    +-------------+------+----------------------------------------------------+
    | argument    | type | definition                                         |
    +=============+======+====================================================+
    | packageName | str  | Name of the file were we                           |
    |             |      | will write (without any extension)                 |
    +-------------+------+----------------------------------------------------+
    | nbrOfModes  | int  | Maximum number of nodes set as a default parameter |
    +-------------+------+----------------------------------------------------+
    """
    try:
        with open(path+'myHeader.txt', "r") as myfile:
            myHeader = myfile.read()

            myHeader = myHeader.replace('MyReducedModel',packageName[0].upper()+packageName[1:])
            myHeader = myHeader.replace('NBOFMODES',str(nbrOfModes))

            with open(packageName+'.py', "w") as logFile:
                logFile.write(myHeader)
                logFile.close()

        # print(myHeader)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def writeFooter(packageName,nodeName,listplugin,dt,gravity):
    """
    **Write a templated Footer to a file**
    
    This footer will finalize the component created 
    by :py:func:`.writeHeader` & :py:func:`.writeGraphScene` allowing the user to test it rapidly
    while keeping its original root configuration (listplugin/dt/gravity) 

    **Args:**

    +----------------+------+---------------------------------------------------------------+
    | argument       | type | definition                                                    |
    +================+======+===============================================================+
    | packageName    | str  || Name of the file were we will write (without any extension)  |
    |                |      ||that will also be the name for the new component              |
    +----------------+------+---------------------------------------------------------------+
    | nodeName       | str  | Name of the Sofa.Node we reduce                               |
    +----------------+------+---------------------------------------------------------------+
    | listplugin     | str  | Initial scene plugin list                                     |
    +----------------+------+---------------------------------------------------------------+
    | dt             | str  | Initial scene plugin dt                                       |
    +----------------+------+---------------------------------------------------------------+
    | gravity        | str  | Initial scene plugin gravity                                  |
    +----------------+------+---------------------------------------------------------------+

    """
    try:
        with open(path+'myFooter.txt', "r") as myfile:
            myFooter = myfile.read()

            myFooter = myFooter.replace('myReducedModel',nodeName)
            myFooter = myFooter.replace('MyReducedModel',packageName[0].upper()+packageName[1:])
            myFooter = myFooter.replace('PLUGIN',str(listplugin))
            myFooter = myFooter.replace('GRAVITY',str(gravity))
            myFooter = myFooter.replace('DT',str(dt))


            with open(packageName+'.py', "a") as logFile:
                logFile.write(myFooter)

            # print(myFooter)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise   


def writeGraphScene(packageName,nodeName,myMORModel,myModel):
    """
    **Write a SOFA scene from lists**

    With 2 lists describing the 2 Sofa.Node containing the components for our reduced model,
    this function will write each component with their initial parameters and clean or add parameters
    in order to have in the end a reduced model component reusable as a function with arguments as :

        .. sourcecode:: python

            def MyReducedModel(
                              attachedTo=None,
                              name="MyReducedModel",
                              rotation=[0.0, 0.0, 0.0],
                              translation=[0.0, 0.0, 0.0],
                              scale=[1.0, 1.0, 1.0],
                              surfaceMeshFileName=False,
                              surfaceColor=[1.0, 1.0, 1.0],
                              nbrOfModes=nbrOfModes,
                              hyperReduction=True):

    **Args:**

    +-------------+-------------+-------------------------------------------------------------+
    | argument    | type        | definition                                                  |
    +=============+=============+=============================================================+
    | packageName | str         | Name of the file were we will write (without any extension) |
    +-------------+-------------+-------------------------------------------------------------+
    | nodeName    | str         | Name of the Sofa.Node we reduce                             |
    +-------------+-------------+-------------------------------------------------------------+
    | myMORModel  | list        | list of tuple (solver_type , param_solver)                  |
    |             |             | *more details see* :py:obj:`.myMORModel`                    | 
    +-------------+-------------+-------------------------------------------------------------+
    | myModel     | OrderedDict || Ordered dic containing has key Sofa.Node.name &            |
    |             |             || has var a tuple of (Sofa_componant_type , param)           |
    |             |             || *more details see* :py:obj:`.myModel`                      |
    +-------------+-------------+-------------------------------------------------------------+

    """
    #print("------------>", myModel)
    try:
        filesName = []
        with open(packageName+'.py', "a+") as logFile:

            logFile.write("    "+nodeName+'_MOR'+" = modelRoot.addChild('"+nodeName+'_MOR'+"')\n")

            for type , arg in myMORModel:
                # print(type+' : '+str(arg)+'\n')                    
                if arg :
                    if type == "MechanicalObject":
                        arg['position'] = "[0]*nbrOfModes"
                    myArgs = buildArgStr(arg)
                    myArgs = "    "+nodeName+"_MOR.addObject('" + type +"' "+myArgs+")\n"
                else :
                    myArgs = "    "+nodeName+"_MOR.addObject('"+type+"')\n"

                # print('for '+type+' '+myArgs+'\n')
                myArgs = myArgs.replace("'[0]*nbrOfModes'","[0]*nbrOfModes")
                logFile.write(myArgs)
            modelTranslation = None
            modelRotation = None
            modelScale = None
            for childName , obj in myModel.items():
                logFile.write('\n\n')
                parentNode = ''
                if childName.split('/')[-1] == nodeName :
                    print(childName,0)
                    childName = childName.split('/')[-1]
                    parentNode = nodeName+"_MOR"
                elif childName.find('/'+nodeName+'/') == -1:
                    print(childName,1)
                    tmp = list(filter(None, childName.split('/')))
                    if len(tmp) > 2: # Add all the parents that haven't been created yet 
                        for i, node in enumerate(tmp):
                            if i < len(tmp)-2:
                                toFind = ''
                                if i == 0:
                                    toFind += "    "+tmp[i]+" = modelRoot.addChild('"+tmp[i]+"')\n"
                                toFind += "    "+tmp[i+1]+" = "+tmp[i]+".addChild('"+tmp[i+1]+"')\n"
                                logFile.seek(0)
                                if toFind not in logFile.read():
                                    # print(toFind)
                                    logFile.write(toFind)
                        parentNode = childName.split('/')[-2]
                    else:
                        parentNode = 'modelRoot'

                    childName = childName.split('/')[-1]
                else:
                    print(childName,2)
                    if childName.split('/')[-2] == nodeName:
                        parentNode = nodeName
                    else:
                        tmp = list(filter(None, childName.split('/')))
                        parentNode = tmp[-2]
                        if len(tmp) > 2:
                            for i, node in enumerate(tmp):
                                if i < len(tmp)-2:
                                    toFind = "    "+tmp[i+1]+" = "+tmp[i]+".addChild('"+tmp[i+1]+"')\n"
                                    logFile.seek(0)
                                    if toFind not in logFile.read():
                                        # print(toFind)
                                        logFile.write(toFind)

                    childName = childName.split('/')[-1]

                logFile.write("    "+childName+" = "+parentNode+".addChild('"+childName+"')\n")
                # print('CHILD :'+childName)
                for type , arg in obj:
                    # print(type+' : '+str(arg)+'\n')
                    if arg :
                        # print(type+' : '+str(arg)+'\n')
                        tmpList = ['MeshGmshLoader','MeshVTKLoader','MeshSTLLoader','MeshOBJLoader']
                        if type in tmpList:
                            print(arg['filename'])
                            if arg['filename'] not in filesName:
                                filesName.append(arg['filename'])

                            filename = os.path.normpath(arg['filename'])
                            filename = filename.split(slash)[-1]

                            arg['filename'] = slash+'mesh'+slash+filename

                            if 'translation' not in arg:
                                arg['translation'] = [0.0,0.0,0.0]
                            if 'rotation' not in arg:
                                arg['rotation'] = [0.0,0.0,0.0]
                            if 'scale3d' not in arg:
                                arg['scale3d'] = [1.0,1.0,1.0]
                            myArgs = buildArgStr(arg)
                            # if modelTranslation :
                            #     myArgs = buildArgStr(arg,modelTranslation)
                            # else:
                            #     myArgs = buildArgStr(arg)
                            if childName == nodeName :
                                modelTranslation = arg['translation']
                                modelRotation = arg['rotation']
                                modelScale = arg['scale3d']
                            # print(myArgs)
                        elif type == 'BoxROI' and not 'orientedBox' in arg: # orientedBoxes aren't handled yet 
                            # myArgs = ", name= '"+arg['name']+"' , box=np.add(translation,rotate(rotation,"+str(tmp)+") )"
                            if "box" in arg:
                                if isinstance(arg['box'], str):
                                    tmp = [float(x) for x in arg['box'].split(' ')]
                                else:
                                    tmp = arg['box']
                                newPoints = []

                                # print('BOX : '+str(tmp))
                                for i in range(int(len(tmp)/3)):
                                    newPoints.append([tmp[i*3],tmp[i*3+1],tmp[i*3+2]])
                                depth = abs(newPoints[0][2] - newPoints[1][2])
                                tr = depth/2.0
                                pointMin = newPoints[0]
                                pointMax = newPoints[1]
                                p1 = [pointMin[0],pointMax[1],pointMin[2]]
                                p2 = [pointMin[0],pointMin[1],pointMin[2]]
                                p3 = [pointMax[0],pointMin[1],pointMin[2]]
                                points = [p1,p2,p3]
                                # newPoints[2] , newPoints[1] = newPoints[1] , newPoints[2]
                                if (modelTranslation == None):
                                    modelTranslation ='[0.0, 0.0, 0.0]'
                                myArgs= ", name= '"+arg['name']+"' , orientedBox= newBox("+str(points)+" , "+str(modelTranslation)+",translation,rotation,"+str([0,0,tr])+",scale) + multiply(scale[2],"+str([depth])+").tolist(),drawBoxes=True"
                            # elif "orientedBox" in arg :      
                            #     myArgs= ", orientedBox= add("+str(translation)+" , PositionsTRS(subtract("+str(arg['orientedBox'])+" , "+str(translation)+"),translation,rotation))"
                            else:
                                raise Exception('Wrong BoxROI arguments :'+str(arg))
                            # print('BOXROI ARG: ',myArgs)

                        else :
                            # print(childName)
                            if childName == nodeName :
                                myArgs = buildArgStr(arg)
                            else:
                                myArgs = buildArgStr(arg,modelTranslation)

                        myArgs = "    "+childName+".addObject('" + type +"' "+myArgs+")\n"
                        # print(myArgs)
                    else :
                        myArgs = "    "+childName+".addObject('"+type+"')\n"
                    
                    logFile.write(myArgs)

        with open('meshFiles.txt', "a") as logFile:
            for mesh in filesName:
                logFile.write(mesh+'\n')

        return (modelRotation,modelTranslation,modelScale)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def buildArgStr(arg,translation=None):
    """
    **According to the case it will add translation,rotation,scale arguments**

    Allowing to move easily in a scene the created component

    **Args:**

    +-------------+-------+-----------------------------------------------+
    | argument    | type  | definition                                    |
    +=============+=======+===============================================+
    | arg         | dic   | Contains all argument of a Sofa Component     |
    +-------------+-------+-----------------------------------------------+
    | translation | float || Contanis the initial translation of the model|
    |             |       || this will allow us to calculate a new        |
    |             |       || position of an object depending of our       |
    |             |       || reduced model by substracting our model      |
    |             |       || relative origin make the TRS in the absolute |
    |             |       || origin and replace it in our model relative  |
    |             |       || origin                                       |
    +-------------+-------+-----------------------------------------------+ 
    """
    myArgs = ''
    for key, val in arg.items():
        # print(type(val))
        # print('key : '+key+'\narg : '+str(val))
        if isinstance(val,list):

            if translation: 
                if key == 'position' or key == 'pullPoint':
                    # print('translation ',translation)
                    myArgs += ", "+key+" = TRSinOrigin("+str(val)+" , "+str(translation)+",translation,rotation,scale)"
                # elif key == 'translation':
                #     myArgs += ", "+key+" = np.add(translation,"+str(val)+")"
                # elif key == 'rotation':
                #     myArgs += ", "+key+" = np.add(rotation,"+str(val)+")"
                else:
                    myArgs += ", "+key+" = "+str(val)
            else:
                if key == 'translation':
                    myArgs += ", "+key+" = add(translation,"+str(val)+")"
                elif key == 'rotation':
                    myArgs += ", "+key+" = add(rotation,"+str(val)+")"
                elif key == 'scale3d':
                    myArgs += ", "+key+" = multiply(scale,"+str(val)+")"
                elif key == 'pullPoint':
                    myArgs += ", "+key+" = add(translation,rotate(rotation,"+str(val)+"))"
                else:
                    myArgs += ", "+key+" = "+str(val)

        elif key.find('Path') != -1 or key.find('filename') != -1:
            # add 'r' before val to avoid special char due to windows path
            myArgs += ", "+key+" = path + r'"+str(val)+"'"

        else :
            if key == "nbModes":
                myArgs += ", "+key+" = nbrOfModes"
            elif key == "performECSW":
                myArgs += ", "+key+" = hyperReduction"
            elif isinstance(val,str):
            #     if '@' in val:
            #         if '_MOR' in val:
            #             tmp = val.split('/')
            #             toChange = 0
            #             print(val)
            #             for i,node in enumerate(tmp):
            #                 print(node,i)
            #                 if '_MOR' in node:
            #                     # print("FOUND")
            #                     toChange = i
            #             # print(toChange,tmp[:toChange],tmp[toChange:])
            #             myArgs += ", "+key+" = '"+'/'.join(tmp[:toChange])+"/"+\
            #                                     "'+name+'"+"/"+\
            #                                     '/'.join(tmp[toChange+1:])+"'"
            #             print(myArgs)
            #         else:
            #             myArgs += ", "+key+" = '"+str(val)+"'"
            #     else:
                myArgs += ", "+key+" = '"+str(val)+"'"
            else:
                myArgs += ", "+key+" = "+str(val)#+"'"

    # print(myArgs)
    return myArgs