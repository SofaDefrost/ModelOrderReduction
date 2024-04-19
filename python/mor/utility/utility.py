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
**Utilities functions used mainly by the reduceModel classes**

------------------------------------------------------------------
"""
import os, sys
import time
import math
import numpy as np
import shutil
import errno

from subprocess import Popen, PIPE, call
import tempfile
import time


def update_progress(progress):
    barLength = 50 # Modify this to change the length of the progress bar
    status = "Compute Weight&RID"
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress > 1:
        progress = 1
    block = int(round(barLength*progress))
    text = "\r[{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    if progress == 1 :
        text =  text+"\n"
    sys.stdout.write(text)
    sys.stdout.flush()

def copy(src, dest):
    '''
    '''
    try:
        shutil.copytree(src, dest)
    except:
        # If the error was caused because the source wasn't a directory
        try:
            shutil.copy(src, dest)
        except:
            print('Directory not copied. Error: %s' % e)

def checkExistance(dir):
    '''
    '''

    if not os.path.exists(os.path.dirname(dir)):
        try:
            os.makedirs(os.path.dirname(dir))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def copyFileIntoAnother(fileToCopy,fileToPasteInto):
    '''
    '''

    try:
        with open(fileToPasteInto, "a") as myFile:
            currentFile = open(fileToCopy, "r")
            myFile.write(currentFile.read())
            currentFile.close()

    except IOError:
        print("IOError : there is no "+fileToCopy+" , check the template log to find why.\nHere some clue for its probable origin :"\
                        +"    - Your animation arguments are incorrect and it hasn't find anything to animate")

    except:
        raise

from Cheetah.Template import Template
def customLauncher(filesandtemplates,param,resultDir):

    files=[]
    for (content,filename) in filesandtemplates:
        files.append( resultDir+filename )
        param["FILE"+str(len(files)-1)] = files[-1]

    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    i=0
    for (content,filename) in filesandtemplates:
        theFile = open(files[i], "w+")
        t = Template(content, searchList=param)
        theFile.write(str(t))
        theFile.close()
        i+=1

def executeSofaScene(sofaScene,param=["-g", "batch", "-l", "SofaPython3", "-n", "5"],verbose=False):

    if os.path.isfile(sofaScene):

        arg = ["runSofa"]+param+[sofaScene]

        # print(arg)
        # print(os.path.dirname(sofaScene))
        begin = time.time()
        try:
            a = Popen(arg, stdout=PIPE, stderr=PIPE,universal_newlines=True)
        except:
            print("Unable to find runSofa, please add the runSofa location to your PATH and restart sofa-launcher.")
            sys.exit(-1)

        astdout, astderr = a.communicate()
        a.stdout.close()
        a.stderr.close()
        end = time.time()
        logfile = open(os.path.dirname(sofaScene)+"/reduction-log", "w+")
        logfile.write("========= STDOUT-LOG============\n")
        logfile.write(astdout)
        logfile.write("========= STDERR-LOG============\n")
        logfile.write(astderr)
        logfile.close()
        if '[ERROR]' in astderr:
            return False
        return True

    else:
        print("ERROR    the file you try to launch doesn't exist, you have to execute the phase first")
