## Usage: python readGieFileAndComputeRIDandWeights.py argv[1] argv[2] argv[3]    
##
##               arg1 = gieFilename             ->  Path to GIE File
##               arg2 = outputfilesName         ->  Name Output File
##               arg3 = tol                     ->  Tolerance (typically between 0.1 and 0.01)
import time, sys
import yaml
import math
import numpy as np
import code #   ???

# from sys import argv
# script, gieFilename, outputfilesName, tol = argv

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
ymlfile.close()

with open(cfg['morConfigFile'], 'r') as ymlfile:
    morConfigFile = yaml.load(ymlfile)
ymlfile.close()
  

gieFilename =                   morConfigFile['gieFilename']
pathToWeightsAndRIDdir =        morConfigFile['weightsAndRID']['pathTodir']
RIDFileName =                   morConfigFile['weightsAndRID']['RIDFileName']
weightsFileName =               morConfigFile['weightsAndRID']['weightsFileName']
tol =                           morConfigFile['weightsAndRID']['tolerance']

verbose = cfg['other']['verbose']

print "###################################################"
print "Executing readGieFileAndComputeRIDandWeights.py\n"
print "Arguments :\n"
print "     INPUT  :"
print "     in gieFilename    :",gieFilename
print "     with arguments    :"
print "         -tolerance        :",tol,"\n"
print "     OUTPUT :"
print "     in pathToWeightsAndRIDdir :",pathToWeightsAndRIDdir
print "         -RIDFileName                :",RIDFileName
print "         -weightsFileName            :",weightsFileName,"\n"
print "###################################################"

################################################################################################

fgie = open(gieFilename,'r')
lineCount = 0
gie = []
keepIndex = []

def update_progress(progress):
    barLength = 40 # Modify this to change the length of the progress bar
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


def errDif(G, xi, b):
    return np.linalg.norm(G.dot(xi) - b)

def etaTild(Gtilde, b):
    return np.linalg.solve( np.transpose(Gtilde).dot(Gtilde) , np.transpose(Gtilde).dot(b) )

def selectECSW(G,b,tau):
    global verbose
    nbLines, numElem = np.shape(G)
    ECSWindex = set([])
    xi = np.zeros((numElem,1))
    valTarget = tau*np.linalg.norm(b);
    currentValue = errDif(G,xi,b)
    marge = currentValue - valTarget

    while (currentValue > valTarget):

        if verbose : 
            print 'Current Error: ', currentValue,' Target Error: ', valTarget
        else :
            update_progress( round( ( 100 - ((currentValue - valTarget)*100) / marge) / 100 , 4) )

        vecDiff = b - G.dot(xi)
        GT = np.transpose(G)
        mu = GT.dot(vecDiff)
        index = int(np.argmax(mu))
        ECSWindex = ECSWindex.union([index])

        Gtilde = G[:,list(ECSWindex)]
        etaTilde = etaTild(Gtilde,b)

        while ( not(all(etaTilde>0) ) ):

            ECSWindexNegative = []
            etaTildeNegative = []
            NonZero = []
            ind = 0

            #if verbose : print 'Hohohohohohohohoho !!!'

            negIndex = (etaTilde-xi[list(ECSWindex)])<0
            negIndex = list(negIndex.flatten())

            for i in negIndex:

                if (i):
                    ECSWindexNegative.append(list(ECSWindex)[ind])
                    etaTildeNegative.append(etaTilde[ind])

                ind = ind + 1

            vec1 = -xi[ECSWindexNegative] 
            vec2 = (etaTildeNegative-xi[ECSWindexNegative])
            maxFeasibleStep = np.amin(vec1/vec2);
            xi[list(ECSWindex)] = xi[list(ECSWindex)] + maxFeasibleStep*(etaTilde - xi[list(ECSWindex)]);
            zeroIndex = np.absolute(xi)<1.0e-12;
            ECSWindex = set(range(numElem))

            ind = 0
            for i in zeroIndex:

                if (not i): NonZero.append(list(ECSWindex)[ind])
                ind = ind + 1

            ECSWindex = set(NonZero)

            Gtilde = G[:,list(ECSWindex)]
            etaTilde = etaTild(Gtilde,b)

        xi[list(ECSWindex)] = etaTilde

        currentValue = errDif(G,xi,b)

    if verbose :
        print "Final Error: ", errDif(G,xi,b) ," Target Error: ", valTarget
    else :    
        update_progress( 1 )

    return (ECSWindex,xi)


#Read all the file & store it in GIE
if verbose : print "Reading file : %r" %gieFilename
for line in fgie:
    lineSplit = line.split();
    lineFloat = map(float,lineSplit)
    gie.append(lineFloat);
    lineCount = lineCount +1
fgie.close()

if verbose : 
    print "     File read until line", lineCount
    print "Done reading file %r:" % gieFilename,'\n'

gie = np.array(gie)
nbLines , nbElements = np.shape(gie)

#Clean GIE
for i in range(nbLines):
    if any(gie[i,:] != 0):
        keepIndex.append(i)

#Creat bECSW from GIE
gie = gie[keepIndex,:]
bECSW = np.sum(gie,axis=1)
bECSW = bECSW[np.newaxis]
bECSW = np.transpose(bECSW)

####################################
if verbose : 
    print "INFO pre-process"
    print "     size GIE (nbLine,nbElements) :   ", '('+str(nbLines)+', '+str(nbElements)+')'
    print "     size cleaned GIE :               ", np.shape(gie)
    print "     size bECSW :                     ", np.shape(bECSW),'\n'
####################################

#Compute RID & Weight
ECSWindex,xi = selectECSW(gie,bECSW,tol)
ECSWindex = np.array(sorted(list(ECSWindex)))
sizeRID = ECSWindex.size
nbElements = xi.size

#Store results in files 
np.savetxt(pathToWeightsAndRIDdir+RIDFileName,ECSWindex, header=str(sizeRID)+' 1', comments='', fmt='%d')
np.savetxt(pathToWeightsAndRIDdir+weightsFileName,xi, header=str(nbElements)+' 1', comments='',fmt='%10.5f')

if verbose: print "===> Success readGieFileAndComputeRIDandWeights.py\n"
