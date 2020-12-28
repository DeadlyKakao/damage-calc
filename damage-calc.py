# -*- coding: utf-8 -*-

''' Instructions/Explanations/Versions




'''

import numpy as np

import inputWeapons as iw
import sheet as sht


# Optionen für Numpy zur Textausgabe von Arrays
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)

# Name der Eingabedatei
inputFileName = "input_test.xlsx"
# Name des Excel-Sheets (Index oder Name funktioniert)
excelSheet = "Salvador"
# excelSheet = 3

minAC = 10
maxAC = 40

# Start des Programms
sheet = sht.Sheet(iw.readInput(inputFileName, excelSheet), minAC, maxAC)

# Auswertung und Ausgabe

# sheet.listAttacks()
# print(sheet.results)
# print(sheet.diffResults)

# sheet.graphAbsolute()
# sheet.graphDifference()
sheet.outputData("output_test.xlsx")