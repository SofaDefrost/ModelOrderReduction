# -*- coding: utf-8 -*-
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))+'/template/'

def writeHeader(packageName):
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
                            if modelTranslation :
                                myArgs = buildArgStr(arg,modelTranslation)
                            else:
                                myArgs = buildArgStr(arg)
                            if childName == nodeName :
                                modelTranslation = arg['translation']
                                modelRotation = arg['rotation']
                            # print(myArgs)
                        elif type == 'BoxROI':
                            tmp = [float(x) for x in arg['box'].split(' ')]
                            myArgs = ", name= '"+arg['name']+"' , box=addTripletList(translation,rotate(rotation,"+str(tmp)+") )"
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
        return (modelRotation,modelTranslation)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

def writeFooter(packageName,nodeName,modelTransform):
    try:
        print('modelTransform : '+str(modelTransform))
        with open(path+'myFooter.txt', "r") as myfile:
            myFooter = myfile.read()

            myFooter = myFooter.replace('MyReducedModel',packageName[0].upper()+packageName[1:])
            myFooter = myFooter.replace('myReducedModel',nodeName)
            if modelTransform:
                myFooter = myFooter.replace('arg1',str(modelTransform[0]))
                myFooter = myFooter.replace('arg2',str(modelTransform[1]))
            else:
                myFooter = myFooter.replace('arg1',str([0,0,0]))
                myFooter = myFooter.replace('arg2',str([0,0,0]))

            with open(packageName+'.py', "a") as logFile:
                logFile.write(myFooter)
                logFile.close()

            myfile.close()
            # print(myFooter)

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise   

def buildArgStr(arg,translation=None):
    myArgs = ''
    for key, val in arg.items():
        # print('key : '+key+'\narg : '+str(val))
        if isinstance(val,list):

            if translation: 
                if key == 'position' or key == 'pullPoint':
                    # print('translation ',translation)
                    myArgs += ", "+key+" = addTripletList("+str(translation)+" , addTripletList(translation,rotate(rotation, subTripletList ("+str(translation)+" , "+str(val)+"))))"
                if key == 'translation':
                    myArgs += ", "+key+" = addTripletList(translation,"+str(val)+")"
                elif key == 'rotation':
                    myArgs += ", "+key+" = addTripletList(rotation,"+str(val)+")"
                else:
                    myArgs += ", "+key+" = "+str(val)
            else:
                if key == 'translation':
                    myArgs += ", "+key+" = addTripletList(translation,"+str(val)+")"
                elif key == 'rotation':
                    myArgs += ", "+key+" = addTripletList(rotation,"+str(val)+")"
                elif key == 'pullPoint':
                    myArgs += ", "+key+" = addTripletList(translation,rotate(rotation,"+str(val)+"))"
                else:
                    myArgs += ", "+key+" = "+str(val)

        elif key.find('Path') != -1 or key.find('filename') != -1:
            myArgs += ", "+key+" = path + '"+str(val)+"'"

        else :
            myArgs += ", "+key+" = '"+str(val)+"'"

    # print(myArgs)
    return myArgs