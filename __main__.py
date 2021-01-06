# -*- coding: utf-8 -*-

"""
Instructions/Explanations/Versions





*** Planned Features ***
- Writing the README/Instructions
- Protection against invalid input files
- Completion of test sheet for the program
- Completion of Sheet.outputDataComplete()
- Representation of monster abilities like constrict, rend, rake etc.
- Introduction of Damage Types
- Introduction of Energy Resistance
- Introduction of Spell Damage
- Estimation of applicability of certain damage components and factoring percentage
    into overall damage calculation
- GUI


**********************
*** damage-calc.py ***
**********************

Author: Daniel Kranz
Additional Contributions by: Maxime Fleury

*** Version History: ***
2020-12-29 0.1: First Version
2021-01-02:
    Implemented main function and args to start from command line
    Now outputs absolute and difference damage to excel (previously only absolute)
"""

import sys
import numpy as np

import inputWeapons as iw
import sheet as sht


def main(args):
    # Default settings (can be overridden by input arguments)
    
    # Names of input and output files
    inputFileName = "input_examples.xlsx"
    outputFileName = "output.xlsx"
    
    # Name of the sheet that the program should use
    # (Numerical index or sheet name as string works)
    inputSheet = "Salvador"
    outputSheet = "Sheet0"
    
    # AC range for the calculation, given in minimum and maximum value (default 10 and 40)
    minAC = 10
    maxAC = 40
    
    # Flags for desired output steps
    flagOutputConsole = False
    flagOutputFile = False
    flagOutputGraphAbsolute = False
    flagOutputGraphDifference = False
    
    # Graph titles and file names
    graphAbsoluteTitle = "Average Damage"
    graphAbsoluteFileName = "graphAbsolute.png"
    graphDifferenceTitle = "Average Difference"
    graphDifferenceFileName = "graphDifference.png"
    
    # Parsing input arguments
    try:
        for i in range(len(args)):
            a = args[i]
            if a in ("-h", "--help", "?"):
                helptext()
                return
            elif a in ("-i", "--input-file"):
                inputFileName = args[i+1]
            elif a in ("-o", "--output-file"):
                outputFileName = args[i+1]
            elif a in ("-is", "--input-sheet"):
                inputSheet = args[i+1]
            elif a in ("-os", "--output-sheet"):
                outputSheet = args[i+1]
            elif a in ("-mi", "--min-AC"):
                minAC = int(args[i+1])
            elif a in ("-ma", "--max-AC"):
                maxAC = int(args[i+1])
            elif a in ("-c", "--console"):
                flagOutputConsole = True
            elif a in ("-f", "--file-output"):
                flagOutputFile = True
            elif a in ("-a", "--graph-absolute"):
                flagOutputGraphAbsolute = True
            elif a in ("-d", "--graph-difference"):
                flagOutputGraphDifference = True
            elif a in ("-ta", "--title-absolute"):
                graphAbsoluteTitle = args[i+1]
            elif a in ("-td", "--title-difference"):
                graphDifferenceTitle = args[i+1]
            elif a in ("-fa", "--file-absolute"):
                graphAbsoluteFileName = args[i+1]
            elif a in ("-fd", "--file-difference"):
                graphDifferenceFileName = args[i+1]
    except:
        print("Error parsing arguments. -h or --help for help.")

    # Settings for the Numpy library concerning printing of arrays (mainly for
    # debugging purposes), suppression of scientific notation and setting precision
    # to max. 3 decimal places.
    np.set_printoptions(precision=3)
    np.set_printoptions(suppress=True)
    
    # Start of calculation execution
    sheet = sht.Sheet(iw.readInput(inputFileName, inputSheet), minAC, maxAC)
    
    # Check output flags
    if flagOutputConsole == True:
        sheet.printData()
    if flagOutputFile == True:
        sheet.outputData(outputFileName=outputFileName, outputSheet=outputSheet)
    if flagOutputGraphAbsolute == True:
        sheet.graphAbsolute(fileName=graphAbsoluteFileName, graphTitle=graphAbsoluteTitle)
    if flagOutputGraphDifference == True:
        sheet.graphDifference(fileName=graphDifferenceFileName, graphTitle=graphDifferenceTitle)
    
    # If no other flag was set, print to console as if given -c.
    if (flagOutputConsole == False and flagOutputFile == False and
        flagOutputGraphAbsolute == False and flagOutputGraphDifference == False):
        sheet.printData()
    

def helptext():
    """
    Displays the help text for the main program

    Returns
    -------
    None.
    
    """
    
    justLength = 27
    print("Placeholder for help text")
    print()
    print("Options")
    print("-h or --help".ljust(justLength) + "Displays this help text.")
    print("-i or --input-file".ljust(justLength) +
          "Input file name/path. Default: 'input_examples.xlsx'")
    print("-o or --output-file".ljust(justLength) +
          "Output file name/path. Default: 'output.xlsx'")
    print("-is or --input-sheet".ljust(justLength) +
          "Input sheet name or index. Default: 'Salvador'")
    print("-os or --output-sheet".ljust(justLength) +
          "Output sheet name. Default: 'Sheet0'")
    print("-mi or --min-AC".ljust(justLength) +
          "Minimum AC for calculation. Default: 10")
    print("-ma or --max-AC".ljust(justLength) +
          "Minimum AC for calculation. Default: 40")
    print("-c or --console".ljust(justLength) + "Numerical output to console.")
    print("-f or --file-output".ljust(justLength) + "Numerical output to file.")
    print("-a or --graph-absolute".ljust(justLength) + "Create and save graph of damage values.")
    print("-d or --graph-difference".ljust(justLength) + "Create and save graph of damage differences.")
    print("-ta or --title-absolute".ljust(justLength) + "Title of damage graph.")
    print("-td or --title-difference".ljust(justLength) + "Title of difference graph.")
    print("-fa or --file-absolute".ljust(justLength) + "File name of damage graph.")
    print("-fd or --file-difference".ljust(justLength) + "File name of difference graph.")
    print()
    print("If no output option (-c, -f, -a, -d) is given, the program defaults to console output as if given -c.")

if __name__ == "__main__":
    main(sys.argv[1:])