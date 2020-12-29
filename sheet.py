# -*- coding: utf-8 -*-

"""
sheet.py provides the Sheet class for representation of multiple attacks
wrapped up in an input Excel sheet.

*** Recent Changes: ***
2020-12-29: Translated comments to English
    Added function graphStonks()
    Added argument for output file name to graph functions
    Added argument for graph title to graph functions
    Added functions printData() and printDataComplete()
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import attack as atk

# Global options for graphics with matplotlib.pyplot
colorCycle = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
markerCycle = [","]
# markerCycle = [".", "o", "1", "s", "x", "+"]

class Sheet:
    """
    The Sheet class represents an Excel sheet of the input file. In the input
    sheet, every column constitutes an attack represented by the Attack object
    which contains one or more weapons.
    """
    
    def __init__(self, inputDataTuple, minAC=10, maxAC=40):
        """
        The constructor of the Sheet class takes a two-dimensional list of
        pandas.DataFrames as given by inputWeapons and uses it to create as many
        Attack objects als the list has columns.
        
        Parameters
        ----------
        inputDataTuple : 2-tuple
            1st part: 2D-list of pandas.DataFrame objects. Every column in this
            list represents one attack with one or more weapons.
            2nd part: list of attack names
        minAC : int, optional
            Lower limit of target AC for calculations.
        maxAC : int, optional
            Upper limit of target AC for calculations.

        Returns
        -------
        None.
        
        """
        
        self.attacks = []
        
        # Split inputDataTuple into weapon list and attack name list
        dfWeaponList = inputDataTuple[0]
        attackNames = inputDataTuple[1]
        
        # Create a result array
        self.acRange = (minAC, maxAC)
        self.results = np.arange(minAC, maxAC+1).transpose()
        for a in range(len(dfWeaponList)):
            newAttack = atk.Attack(dfWeaponList[a], attackNames[a], minAC, maxAC)
            self.attacks.append(newAttack)
            self.results = np.c_[self.results, newAttack.results[:,1]]
        
        # Create a differenc earray
        self.diffResults = self.results.copy()
        for i in range(2, self.diffResults.shape[1]):
            self.diffResults[:, i] -= self.diffResults[:, 1]
        # Remove first row (= base case, no difference)
        self.diffResults = np.delete(self.diffResults, 1, 1)
            
    def listAttacks(self):
        """
        Prints a list of attacks in self.attacks

        Returns
        -------
        None.
        
        """
        
        for a in self.attacks:
            s = ""
            for w in a.weapons:
                s += w.name + " " + w.weaponStringHit() + ";   "
            print(s[:-4])
    
    def graphAbsolute(self, fileName="graphAbsolute.png", graphTitle="Average Damage"):
        """
        Produces a graph of the absolute damage values with matplotlib.pyplot.

        Parameters
        -------
        fileName : str, optional
            Name of the output file. The default is "graphAbsolute.png".
        graphTitle : str, optional
            Title of the graph. The default is "Average Damage".

        Returns
        -------
        figAbsolute : matplotlib.pyplot.Figure
            Handle of the created figure.
        
        """
        
        # Create new figure and an empty list for legend entries
        figAbsolute = plt.figure(dpi=300)
        legendList = []
        
        # Iterate data columns, plot, put names into legend entries
        for i in range(0, self.results.shape[1]-1):
            
            # i-1: Ensures that the colors of data columns match with the same
            # attacks in the difference plot, which lacks the first attack.
            plt.plot(self.results[:,0], self.results[:,i+1],
                     color=colorCycle[(i-1)%len(colorCycle)],
                     marker=markerCycle[(i-1)%len(markerCycle)],
                     linewidth=1, markersize=4.2)
            legendList.append(self.attacks[i].name)
        
        # Remaining graph settings
        legendList[0] = legendList[0] + " (Base)"
        legend = plt.legend(legendList, bbox_to_anchor=(1, 1))
        plt.title("Average Damage")
        plt.xlabel("Target AC")
        plt.ylabel("Damage")
        plt.xlim(self.acRange)
        
        # Grid settings
        plt.xticks(np.arange(self.acRange[0], self.acRange[1]+1, step=5))
        plt.grid(True, which="major")
        plt.minorticks_on()
        plt.grid(True, which="minor", alpha=0.2, linestyle=":", linewidth=1)
        
        # Save graph as png image
        plt.savefig(fileName, format="png",
                    bbox_extra_artists=(legend,), bbox_inches='tight')
        
        # Return figure for possible further handling
        return figAbsolute
    
    def graphDifference(self, fileName="graphDifference.png", graphTitle="Average Difference"):
        """
        Produces a graph of the damage difference values between the attacks
        with matplotlib.pyplot.
        The first attack is assumed as base case and difference is calculated
        between the first attack and every other.
        
        Parameters
        -------
        fileName : str, optional
            Name of the output file. The default is "graphDifference.png".
        graphTitle : str, optional
            Title of the graph. The default is "Average Difference".

        Returns
        -------
        figDifference : matplotlib.pyplot.Figure
            Handle of the created figure.
        
        """
        
        # Create new figure and an empty list for legend entries
        figDifference = plt.figure(dpi=300)
        legendList = []
        
        # Iterate data columns, plot, put names into legend entries
        for i in range(0, self.diffResults.shape[1]-1):
            plt.plot(self.diffResults[:,0], self.diffResults[:,i+1],
                     color=colorCycle[i%len(colorCycle)],
                     marker=markerCycle[i%len(markerCycle)],
                     linewidth=1, markersize=4.2)
            legendList.append(self.attacks[i+1].name)
        
        # Remaining graph settings
        legend = plt.legend(legendList, bbox_to_anchor=(1, 1))
        plt.title("Average damage difference to base case")
        plt.xlabel("Target AC")
        plt.ylabel("Damage")
        plt.xlim(self.acRange)
        
        # Grid settings
        plt.xticks(np.arange(self.acRange[0], self.acRange[1]+1, step=5))
        plt.grid(True, which="major")
        plt.minorticks_on()
        plt.grid(True, which="minor", alpha=0.2, linestyle=":", linewidth=1)
        
        # Save graph as png image
        plt.savefig(fileName, format="png",
                    bbox_extra_artists=(legend,), bbox_inches='tight')
        
        # Return figure for possible further handling
        return figDifference
    
    def graphStonks(self, fileName="graphStonks.png"):
        """
        STONKS

        Parameters
        ----------
        fileName : TYPE, optional
            DESCRIPTION. The default is "graphStonks.png".

        Returns
        -------
        figStonks : matplotlib.pyplot.Figure
            Handle of the created figure.

        """
        
        # Create new figure and an empty list for legend entries
        figDifference = plt.figure(dpi=300)
        legendList = []
        
        # Iterate data columns, plot, put names into legend entries
        for i in range(0, self.diffResults.shape[1]-1):
            plt.plot(self.diffResults[:,0], self.diffResults[:,i+1],
                     color=colorCycle[i%len(colorCycle)],
                     marker=markerCycle[i%len(markerCycle)],
                     linewidth=1, markersize=4.2)
            legendList.append("STONKS")
        
        # Remaining graph settings
        legend = plt.legend(legendList, bbox_to_anchor=(1, 1))
        plt.title("STONKS")
        plt.xlabel("STONKS")
        plt.ylabel("STONKS")
        plt.xlim(self.acRange)
        
        # Grid settings
        plt.xticks(np.arange(self.acRange[0], self.acRange[1]+1, step=5))
        plt.grid(True, which="major")
        plt.minorticks_on()
        plt.grid(True, which="minor", alpha=0.2, linestyle=":", linewidth=1)
        
        # Save graph as png image
        plt.savefig(fileName, format="png",
                    bbox_extra_artists=(legend,), bbox_inches='tight')
        
        # Return figure for possible further handling
        return figDifference
    
    def outputData(self, outputFileName="Output.xlsx", outputSheet="Sheet1"):
        """
        Write the results to Excel file.

        Parameters
        ----------
        outputFileName : str, optional
            Output file name. The default is "Output.xlsx".
        outputSheet : str, optional
            Name of the sheet the output is written to. The default is "Sheet1".

        Returns
        -------
        None.

        """
        
        cols = ["AC"]
        for i in range(0, self.results.shape[1]-1):
            cols.append(self.attacks[i].name)
            
        df = pd.DataFrame(data=self.results,
                          index=np.arange(self.acRange[0], self.acRange[1]+1),
                          columns=cols)
        
        df.to_excel(outputFileName, sheet_name=outputSheet, float_format="%.3f",
                    index=False)
    
    def outputDataComplete(self, outputFileName="Output.xlsx", outputSheet="Sheet1"):
        """
        NOT YET IMPLEMENTED

        Parameters
        ----------
        outputFileName : str, optional
            Output file name. The default is "Output.xlsx".
        outputSheet : str, optional
            Name of the sheet the output is written to. The default is "Sheet1".

        Returns
        -------
        None.
        
        """

        pass

    def printData(self):
        """
        Prints the same data that would be output with outputData().
        
        Returns
        -------
        None.
        
        """
        pass

    def printDataComplete(self):
        """
        Prints the same data that would be output with outputDataComplete().
        
        Returns
        -------
        None.
        
        """
        pass