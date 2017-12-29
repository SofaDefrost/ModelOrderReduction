## Usage: python readGieFileAndComputeRIDandWeights.py argv[1] argv[2] argv[3]    
##
##               arg1 = gieFilename             ->  Path to GIE File
##               arg2 = outputfilesName         ->  Name Output File
##               arg3 = tol                     ->  Tolerance (typically between 0.1 and 0.01)

import yaml
import math
import numpy as np
import code #   ???

# from sys import argv
# script, gieFilename, outputfilesName, tol = argv

print "Executing readGieFileAndComputeRIDandWeights.py\n"

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("../config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
  

gieFilename =                   "../"+cfg['gieFilename']
pathToWeightsAndRIDdir =        cfg['weightsAndRID']['pathTodir']
RIDFileName =                   cfg['weightsAndRID']['RIDFileName']
weightsFileName =               cfg['weightsAndRID']['weightsFileName']
tol =                           cfg['weightsAndRID']['tolerance']

verbose = cfg['other']['verbose']

print "readGieFileAndComputeRIDandWeights arguments :"
print "     input gieFilename            :",gieFilename
print "     in pathToWeightsAndRIDdir    :",pathToWeightsAndRIDdir
print "         -RIDFileName                :",RIDFileName
print "         -weightsFileName            :",weightsFileName
print "         with a tolerance of",tol,"\n"

################################################################################################

fgie = open(gieFilename,'r')
lineCount = 0
gie = []
keepIndex = []

def errDif(G, xi, b):
    return np.linalg.norm(G.dot(xi) - b)

def etaTild(Gtilde, b):
    return np.linalg.solve( np.transpose(Gtilde).dot(Gtilde) , np.transpose(Gtilde).dot(b) )

def selectECSW(G,b,tau):
    global verbose
    display = 50
    j = 0
    nbLines, numElem = np.shape(G)
    ECSWindex = set([])
    xi = np.zeros((numElem,1))
    valTarget = tau*np.linalg.norm(b);

    while (np.linalg.norm(G.dot(xi) - b) > tau*np.linalg.norm(b)):
        if verbose and display == j: 
            print 'Current Error: ', errDif(G,xi,b),' Target Error: ', valTarget
            j = 0
        j += 1
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

    print "Final Error: ", errDif(G,xi,b) ," Target Error: ", valTarget

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

print "===> Success readGieFileAndComputeRIDandWeights.py\n"