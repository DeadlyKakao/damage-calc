# -*- coding: utf-8 -*-

"""
Instructions/Explanations/Versions





*** Planned Features ***
- Completion of test sheet for the program
- Introduction of Damage Types
- Introduction of Energy Resistance


**********************
*** damage-calc.py ***
**********************

Author: Daniel Kranz
Additional Contributions by: Maxime Fleury

*** Version History: ***
2020-12-29 0.1: First Version
"""

import numpy as np

import inputWeapons as iw
import sheet as sht


# Settings for the Numpy library concerning printing of arrays (mainly for
# debugging purposes), suppression of scientific notation and setting precision
# to max. 3 decimal places.
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)

# Name of the input and output files
inputFileName = "input_test.xlsx"
outputFileName = "output_test.xlsx"

# Name of the sheet that the program should use
# (Numerical index or sheet name as string works)
excelSheet = "Salvador"
# excelSheet = 3

# AC range for the calculation, given in minimum and maximum value (default 10 and 40)
minAC = 10
maxAC = 40

# Start of calculation execution
sheet = sht.Sheet(iw.readInput(inputFileName, excelSheet), minAC, maxAC)

print(sheet.attacks[0].weapons[0].critChance(0))

# sheet.listAttacks()
# print(sheet.results)
# print(sheet.diffResults)
# sheet.graphAbsolute()
# sheet.graphDifference()
# sheet.outputData(outputFileName)