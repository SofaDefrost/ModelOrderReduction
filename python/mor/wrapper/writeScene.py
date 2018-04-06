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
                            myArgs = buildArgStr(arg)
                            # if modelTranslation :
                            #     myArgs = buildArgStr(arg,modelTranslation)
                            # else:
                            #     myArgs = buildArgStr(arg)
                            if childName == nodeName :
                                modelTranslation = arg['translation']
                                modelRotation = arg['rotation']
                            # print(myArgs)
                        elif type == 'BoxROI':
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
                                myArgs= ", name= '"+arg['name']+"' , orientedBox= newBox("+str(newPoints)+" , "+str(modelTranslation)+",translation,rotation,"+str([0,0,tr])+")+"+str([depth])+",drawBoxes=True"
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
                    myArgs += ", "+key+" = TRSinOrigin("+str(val)+" , "+str(translation)+",translation,rotation)"
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