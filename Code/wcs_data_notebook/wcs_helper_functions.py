# Code developed and shared by:
# Vasilis Oikonomou
# Joshua Abbott
# Jessie Salas

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import re
from random import random
import numpy as np
from matplotlib import gridspec
import warnings
import string
warnings.filterwarnings('ignore')

def readNamingData(namingDataFilePath):
    """
    Read all of namingDataFilePath into a dictionary, and return it.  Assumes data file follows WCS format:
    language number\tspeaker number\tchip number\tlanguage term for chip\n

    Parameters
    ----------
    namingDataFilePath : string
        The path (and filename, with the extension) to read the WCS-formatted color naming data from.
 

    Returns
    -------
    namingData : dictionary
    	A hierarchical dictionary: namingData[languageNumber][speakerNumber][chipNumber] = languageTerm


    Example Usage:
    --------------
    import wcsFunctions as wcs
    namingDictionary = wcs.readNamingData('./WCS-Data/term.txt')

    """
    namingData = {}  # empty dict
    fileHandler = open(namingDataFilePath,'r')

    for line in fileHandler:              			# for each line in the file
        lineElements = line.split()     			# lineElements are denoted by white space
        
        # WCS format for naming data from term.txt:
        # language number\tspeaker number\tchip number\tlanguage term for chip

        languageNumber = int(lineElements[0])    	# 1st element is language number, make it an int
        speakerNumber = int(lineElements[1])  		# 2nd is speaker number, make int
        chipNumber = int(lineElements[2])     		# 3rd is chip number, make int
        languageTerm = lineElements[3]           	# 4th is languageTermegory assignment (term), keep string
        
        if not (languageNumber in namingData.keys()):    						# if this language isn't a key in the namingData dict
            namingData[languageNumber] = {}              							# then make it one, with its value an empty list
        if not (speakerNumber in namingData[languageNumber].keys()):   			# if this speaker isn't a key in the languageNumber dict
            namingData[languageNumber][speakerNumber] = {}             				# then make it one, with its value an empty list
        
        namingData[languageNumber][speakerNumber][chipNumber] = languageTerm  	# fill in these empty lists to make a GIANT namingData dictionary
                                            									# where each entry looks like this: {1: {1: {1: 'LB'}}
                                            									# and thus namingData[1][1][1] returns string 'LB'
    
    fileHandler.close()				# close file after reading it in, for neatness
    return namingData 				# return the dict


def readFociData(fociDataFilePath):
    """
    Read all of fociDataFilePath into a dictionary, and return it. Assumes data file follows WCS format:
    language number\tspeaker number\tterm number\tterm abbreviation\tWCS chip grid coordinate

    Paramaters
    ----------
    fociDataFilePath : string
        The path (and filename, with the extension) to read the WCS-formatted color foci data from.

    Returns
    -------
    fociData : dictionary
    	A hierarchical dictionary: fociData[languageNumber][speakerNumber][languageTerm].append(modGridCoord)


    Example Usage:
    --------------
    import wcsFunctions as wcs
    fociDictionary = wcs.readFociData('./WCS-Data/foci-exp.txt')

    """

    fociData = {} # empty dict
    fileHandler = open(fociDataFilePath,'r')
    for line in fileHandler:				# for each line in the file
        lineElements = line.split()		# elements are denoted by white space
        
        # WCS format for naming data from foci-exp.txt:
        # language number\tspeaker number\tfoci number in term\tlanguage term for chip\tWCS grid coordinate

        languageNumber = int(lineElements[0])	# 1st element is language number, make it an int
        speakerNumber = int(lineElements[1])	# 2nd is speaker number, make int
        termNumber = int(lineElements[2])		# 3rd is term number for which foci goes to which term
        languageTerm = lineElements[3]			# 4th is term abbreviation
        gridcoord = lineElements[4]				# 5th is chip grid coord
        
        # fix WCS bad entries - collapse A1-40 to A0 and J1-40 to J0
        if (gridcoord[0] == 'A'):
            if (int(gridcoord[1:]) > 0):
                gridcoord = "A0"
        
        if (gridcoord[0] == 'J'):
            if (int(gridcoord[1:]) > 0):
                gridcoord = "J0"

        modGridCoord = gridcoord[0] + ":" + gridcoord[1:]	# make it nicer for parsing purposes later
        

        if not (languageNumber in fociData.keys()):	# if this language isn't a key in the fociData dict
            fociData[languageNumber] = {}			# then make it one, with its value an empty list
        if not (speakerNumber in fociData[languageNumber].keys()):	# if this speaker isn't a key in the languageNumber dict
            fociData[languageNumber][speakerNumber] = {}			# then make it one, with its value an empty list
        if not (languageTerm in fociData[languageNumber][speakerNumber].keys()):	# if this term isn't a key in the speakerNumber dict
            fociData[languageNumber][speakerNumber][languageTerm] = []			# then make it one, with its value an empty list
            
        if not(modGridCoord in fociData[languageNumber][speakerNumber][languageTerm]): # if they provided multiple A0 or J0 hits, only record 1
            fociData[languageNumber][speakerNumber][languageTerm].append(modGridCoord)
        
    fileHandler.close()
    return fociData 


def readChipData(chipDataFilePath):
    """
    Read all of chipDataFilePath into two dictionaries, one maps from row/column code to WCS chip number,
	the other maps in the other direction.  Assumes data file follows WCS format:
    chip number\tWCS grid row letter\tWCS grid column number\tWCS grid rowcol abbreviation\n

    Parameters
    ----------
    chipDataFilePath : string
        The path (and filename, with the extension) to read the WCS-formatted chip data from.
 

    Returns
    -------
    cnum : dictionary
    	cnum[row/column abbreviation] = WCS chipnumber, thus cnum maps from row/col designation to chip number

    cname : a dictionary
    	cname[WCS chipnumber] = row letter, column number (a tuple), thus cname maps from chip number to row/col designation


    Example Usage:
    --------------
    import wcsFunctions as wcs
    cnumDictionary, cnameDictionary = wcs.readChipData('./WCS-Data/chip.txt')

    """
    
    cnum = {}    # empty dict to look up number given row/column designation
    cname = {}   # empty dict to look up row/column designation given number
    fileHandler = open(chipDataFilePath, 'r')    # open file for reading
    for line in fileHandler:               # for each line in the file
        lineElements = line.split()      # elements are denoted by white space
        chipnum = int(lineElements[0])   # 1st element is chip number, make it an int
        RC = lineElements[3]             # 4th is row/column designation, leave str (NB dictionaries don't exactly reverse each other)
        letter = lineElements[1]         # 2nd is the letter (row) designation
        number = str(lineElements[2])    # 3rd is the number (column) designation, make string so we can combine it with letter as a tuple in cname dict

        # cnum[rowcol] maps from row/column designation to chip number
        cnum[RC] = chipnum
        # cname[chipnum] maps from chip number to row/column designation (a tuple)
        cname[chipnum] = letter,number
        
    fileHandler.close()

    return cnum,cname            # return both dicts


def readSpeakerData(speakerFilePath):
    #lANUGUAGE[SPEAKER NUMBER]
    """
    Parameters
    ----------
    speakerFilePath : string
        The path (and filename, with the extension) to read the WCS-formatted speaker data from.
 
    Returns
    ------
    speakers : dictionary
               The keys are ints corresponding to the language IDs and the values are lists of tuples, where
               each element of the list contains (AGE,GENDER) corresponding to the speakers recorded for each language

    Example Usage: 
    -------------
    >>> from pprint import pprint 
    >>> speakerDictionary = readSpeakerData('./WCS_data_partial/spkr-lsas.txt')
    >>>  pprint(speakerDictionary)
    """
    speakers = {}                     #Initialize the dictionary
    f = open(speakerFilePath, 'r')    #Open the file containing the input data
    for line in f:                    #Iterate through each line
        content = line.split()        #split input data by whitespace
        language_ID = int(content[0]) #ID is the first element of row, cast as int
        speaker_ID = int(content[1])
        speaker_age = content[2]      #Age is the third element of row
        speaker_gender = content[3]   #Gender is the fourth element of row
        if not (language_ID in speakers.keys()):	
            speakers[language_ID] = {}			
        if not (speaker_ID in speakers[language_ID].keys()):
            speakers[language_ID][speaker_ID] = []
        if not((speaker_age, speaker_gender) in speakers[language_ID][speaker_ID]):
            speakers[language_ID][speaker_ID].append((speaker_age, speaker_gender))
    return speakers

def readClabData(clabFilePath):
    """
    Parameters
    ----------
    clabFilePath : string
        The path (and filename, with the extension) to read the WCS-formatted clab data from.
 
    Returns
    -------
    clab : dictionary
           The keys are ints and the values are tuples (n1,n2,n3), representing the clab coordinates

    Example Usage:
    -------------
    >>> clabDictionary = readClabData('./WCS_data_core/cnum-vhcm-lab-new.txt')
    >>> print(clabDictionary[141])
    (96.00, -.06,.06)
    
    """
    clab = {}                  #Initialize the dictionary
    f = open(clabFilePath,'r') #Open the file containing the input data
    for line in f:             #Iterate through each line
        content = line.split() #split input data by whitespace
        ID = int(content[0])        #ID is the first element of row, cast as int
        n1,n2,n3 = content[-3],content[-2],content[-1] #coords are the last three elements of row
        clab[ID] = (n1,n2,n3)  #Add ID, coordinate pairs to the dictionary
    return clab


def plotValues(values, figx = 80, figy = 40):
    """Takes a numpy array or matrix and produces a color map that shows variation in the values of the array/matrix."""
    """values: array or matrix of numbers
       figx: length of plot on the x axis, defaults to 10
       figy: length of plot on the y axis, defaults to 10"""
    #read in important information for reordering
    plt.rc(['ytick', 'xtick'], labelsize=50)
    cnumDictionary, cnameDictionary = readChipData('./WCS_data_core/chip.txt')
    #reorder the given values
    lst = [values[cnumDictionary['A0']-1], values[cnumDictionary['B0']-1], 
       values[cnumDictionary['C0']-1], values[cnumDictionary['D0']-1], values[cnumDictionary['E0']-1],
      values[cnumDictionary['F0']-1], values[cnumDictionary['G0']-1], values[cnumDictionary['H0']-1],
      values[cnumDictionary['I0']-1], values[cnumDictionary['J0']-1]]
    for letter in list(string.ascii_uppercase[1:9]):
        for num in range(1, 41):
            lst.append(values[cnumDictionary[letter+str(num)]-1])
    values = np.array(lst)
    #plot
    ha = 'center'
    fig = plt.figure(figsize=(figx,figy))
    fig.suptitle('WCS chart', fontsize=80)
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 8], height_ratios=[1,1]) 
    ax1 = plt.subplot(gs[1])
    ax2 = plt.subplot(gs[0])
    core = values[10:].reshape((8, 40))
    ax1.imshow(core, extent = [0, len(core[0]),len(core), 0], interpolation='none')
    labels = ["B", "C", "D", "E", "F", "G", "H", "I"]
    ax1.set_yticklabels(labels)
    ax2.imshow([[i] for i in values[:10]], extent = [0, 0.5, 0, 10], interpolation='none')
    ax1.yaxis.set(ticks=np.arange(0.5, len(labels)), ticklabels=labels)
    ax2.yaxis.set(ticks=np.arange(0.5, len(["A"]+labels+["J"])), ticklabels=(["A"]+labels+["J"])[::-1])
    ax1.xaxis.set(ticks=np.arange(0.5, 40), ticklabels=np.arange(1, 41))
    

def generate_random_values(ar):
    """Takes in an array of terms and returns a dictionary that maps terms to random values between 0 and 1"""
    d = {}
    for term in ar:
        d[term] = random()
    return d

def map_array_to(ar, d):
    """Maps an array of terms into an array of random values given the dictionary created by the above function"""
    return [d[i] for i in ar]
