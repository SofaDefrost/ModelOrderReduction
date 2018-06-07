# -*- coding: utf-8 -*-
"""
Set of functions to create a reusable SOFA component out of a SOFA scene
"""

import os
import sys

path = os.path.dirname(os.path.abspath(__file__))+'/template/'

def writeHeader(packageName):
    """
    Write a templated Header to the file *packageName*

    **Arg:**

    +-------------+------+------------------------------------+
    | argument    | type | definition                         |
    +=============+======+====================================+
    | packageName | str  | Name of the file were we           |
    |             |      | will write (without any extension) |
    +-------------+------+------------------------------------+    
    """
    try:
    
        with open(path+'myHeader.txt', "r") as myfile:
            myHeader = myfile.read()

            myHeader = myHeader.replace('MyReducedModel',packageName[0].upper()+packageName[1:])

            with open(packageName+'.py', "a") as logFile:
                logFile.write(myHeader)
                logFile.close()

            myfile.close()

        # print(myHeader)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise   

def writeGraphScene(packageName,nodeName,myMORModel,myModel):
    """
    With 2 lists describing the 2 Sofa.Node containing the components for our reduced model,

    this function will write each component with there initial parameters and clean or add parameters
    
    in order to have in the end a reduced model component reusable as a function with arguments as :

        .. sourcecode:: python

            def MyReducedModel(     attachedTo=None,
                                    name="MyReducedModel",
                                    rotation=[0.0, 0.0, 0.0],
                                    translation=[0.0, 0.0, 0.0],
                                    scale=[1.0, 1.0, 1.0],
                                    surfaceMeshFileName=False,
                                    surfaceColor=[1.0, 1.0, 1.0],
                                    poissonRatio=None,
                                    youngModulus=None,
                                    totalMass=None)

    **Args:**

    +-------------+-------------+-------------------------------------------------------------+
    | argument    | type        | definition                                                  |
    +=============+=============+=============================================================+
    | packageName | str         | Name of the file were we will write (without any extension) |
    +-------------+-------------+-------------------------------------------------------------+
    | nodeName    | str         | Name of the Sofa.Node we reduce                             |
    +-------------+-------------+-------------------------------------------------------------+
    | myMORModel  | list        | list of tuple (solver_type , param_solver)                  |
    +-------------+-------------+-------------------------------------------------------------+
    | myModel     | OrderedDict || Ordered dic containing has key Sofa.Node.name &            |
    |             |             || has var a tuple of (Sofa_componant_type , param_solver)    |
    +-------------+-------------+-------------------------------------------------------------+
    """
    # print myModel
    try:

        with open(packageName+'.py', "a") as logFile:

            logFile.write("    "+nodeName+'_MOR'+" = attachedTo.createChild(name)\n")

            for type , arg in myMORModel:
                if arg :
                    myArgs = buildArgStr(arg)
                    myArgs = "    "+nodeName+"_MOR.createObject('" + type +"' "+myArgs+")\n"
                else :
                    myArgs = "    "+nodeName+"_MOR.createObject('"+type+"')\n"

                # print('for '+type+' '+myArgs+'\n')
                logFile.write(myArgs)

            modelTranslation = None
            modelRotation = None
            for childName , obj in myModel.items():
                parenNode = ''
                if childName == nodeName :
                    parentNode = nodeName+"_MOR"
                else :
                    parentNode = nodeName
                logFile.write('\n\n')
                logFile.write("    "+childName+" = "+parentNode+".createChild('"+childName+"')\n")
                # print('CHILD :'+childName)
                for type , arg in obj:
                    # print(type+' : '+str(arg)+'\n')
                    if arg :
                        # print(type+' : '+str(arg)+'\n')
                        tmpList = ['MeshGmshLoader','MeshVTKLoader','MeshSTLLoader']
                        if type in tmpList:
                            arg['filename'] = '/mesh/'+arg['filename'].split('/')[-1]
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
                        elif type == 'BoxROI' and not arg['orientedBox']: # orientedBoxes aren't handled yet 
                            tmp = [float(x) for x in arg['box'].split(' ')]
                            # myArgs = ", name= '"+arg['name']+"' , box=np.add(translation,rotate(rotation,"+str(tmp)+") )"
                            if "box" in arg:
                                newPoints = []
                                # print('BOX : '+str(tmp))
                                for i in range(len(tmp)/3):
                                    newPoints.append([tmp[i*3],tmp[i*3+1],tmp[i*3+2]])
                                depth = abs(newPoints[0][2] - newPoints[1][2])
                                tr = (newPoints[0][2] + newPoints[1][2])/2
                                newPoints[1][2] = newPoints[0][2] = 0
                                newPoints.append([newPoints[1][0],0,0])
                                newPoints[2] , newPoints[1] = newPoints[1] , newPoints[2]
                                myArgs= ", name= '"+arg['name']+"' , orientedBox= newBox("+str(newPoints)+" , "+str(modelTranslation)+",translation,rotation,"+str([0,0,tr])+",scale) + multiply(scale[2],"+str([depth])+").tolist(),drawBoxes=True"
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

                        myArgs = "    "+childName+".createObject('" + type +"' "+myArgs+")\n"
                        # print(myArgs)
                    else :
                        myArgs = "    "+childName+".createObject('"+type+"')\n"
                    
                    logFile.write(myArgs)


        logFile.close()
        return (modelRotation,modelTranslation,modelScale)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

def writeFooter(packageName,nodeName,modelTransform):
    """
    Write a templated Footer to the file *packageName*

    **Args:**

    +-------------+------+-------------------------------------------------------------+
    | argument    | type | definition                                                  |
    +=============+======+=============================================================+
    | packageName | str  | Name of the file were we will write (without any extension) |
    +-------------+------+-------------------------------------------------------------+
    """

    try:
        print('modelTransform : '+str(modelTransform))
        with open(path+'myFooter.txt', "r") as myfile:
            myFooter = myfile.read()

            myFooter = myFooter.replace('MyReducedModel',packageName[0].upper()+packageName[1:])
            myFooter = myFooter.replace('myReducedModel',nodeName)
            if modelTransform:
                myFooter = myFooter.replace('arg1',str(modelTransform[0]))
                myFooter = myFooter.replace('arg2',str(modelTransform[1]))
                myFooter = myFooter.replace('arg3',str(modelTransform[2]))
            else:
                myFooter = myFooter.replace('arg1',str([0,0,0]))
                myFooter = myFooter.replace('arg2',str([0,0,0]))
                myFooter = myFooter.replace('arg3',str([1,1,1]))

            with open(packageName+'.py', "a") as logFile:
                logFile.write(myFooter)
                logFile.close()

            myfile.close()
            # print(myFooter)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise   

def buildArgStr(arg,translation=None):
    """
    According to the case it will add translation,rotation,scale arguments

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
            myArgs += ", "+key+" = path + '"+str(val)+"'"

        else :
            myArgs += ", "+key+" = '"+str(val)+"'"

    # print(myArgs)
    return myArgs