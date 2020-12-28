# -*- coding: utf-8 -*-

"""
weapon.py provides the Weapon class for weapon representation.

*** Recent Changes: ***
XXXX-XX-XX: Translated comments to English
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import attack as atk

colorCycle = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
markerCycle = [","]
# markerCycle = [".", "o", "1", "s", "x", "+"]

class Sheet:
    def __init__(self, dfWeaponList, minAC, maxAC):
        self.attacks = []
        
        # Aufstellen der Ergebnismatrix
        self.acRange = (minAC, maxAC)
        self.results = np.arange(minAC, maxAC+1).transpose()
        for a in range(len(dfWeaponList)):
            newAttack = atk.Attack(dfWeaponList[a], minAC, maxAC)
            self.attacks.append(newAttack)
            self.results = np.c_[self.results, newAttack.results[:,1]]
        
        # Aufstellen der Differenzmatrix
        self.diffResults = self.results.copy()
        for i in range(2, self.diffResults.shape[1]):
            self.diffResults[:, i] = self.diffResults[:, i] - self.diffResults[:, 1]
        self.diffResults = np.delete(self.diffResults, 1, 1)
            
    def listAttacks(self):
        for a in self.attacks:
            s = ""
            for w in a.weapons:
                s = s + w.name + " " + w.weaponStringHit() + ";   "
            print(s[:-4])
    
    def graphAbsolute(self):
        '''Grafische Darstellung der absoluten Schadenswerte mit Matplotlib.'''
        
        # Neue Figure erstellen und eine leere Liste für Legendeneinträge anlegen
        figAbsolute = plt.figure(dpi=300)
        legendList = []
        
        # Datenreihen iterieren, plotten und Namen in Legendeneinträge schreiben
        for i in range(0, self.results.shape[1]-1):
            plt.plot(self.results[:,0], self.results[:,i+1],
                     color=colorCycle[(i-1)%len(colorCycle)],
                     marker=markerCycle[(i-1)%len(markerCycle)],
                     linewidth=1, markersize=4.2)
            legendList.append(self.attacks[i].weapons[0].name)
        
        # Restliche Einstellungen des Graphen vornehmen
        legendList[0] = legendList[0] + " (Basis)"
        legend = plt.legend(legendList, bbox_to_anchor=(1, 1))
        plt.title("Durchschnittlicher Schaden")
        plt.xlabel("RK des Ziels")
        plt.ylabel("Schaden")
        plt.xlim(self.acRange)
        
        plt.xticks(np.arange(self.acRange[0], self.acRange[1]+1, step=5))
        plt.grid(True, which="major")
        plt.minorticks_on()
        plt.grid(True, which="minor", alpha=0.2, linestyle=":", linewidth=1)
        
        # Grafik als png abspeichern
        plt.savefig("graphAbsolute.png", format="png",
                    bbox_extra_artists=(legend,), bbox_inches='tight')
        
        # Figure zurückgeben, damit diese bei Bedarf noch weiterverarbeitet
        # werden kann.
        return figAbsolute
    
    def graphDifference(self):
        '''Grafische Darstellung der Differenzschadenswerte mit Matplotlib.'''
        figDifference = plt.figure(dpi=300)
        legendList = []
        
        for i in range(0, self.diffResults.shape[1]-1):
            plt.plot(self.diffResults[:,0], self.diffResults[:,i+1],
                     color=colorCycle[i%len(colorCycle)],
                     marker=markerCycle[i%len(markerCycle)],
                     linewidth=1, markersize=4.2)
            legendList.append(self.attacks[i+1].weapons[0].name)
        
        # Restliche Einstellungen des Graphen vornehmen
        legend = plt.legend(legendList, bbox_to_anchor=(1, 1))
        plt.title("Durchschnittliche Schadensdifferenz zum Basisfall")
        plt.xlabel("RK des Ziels")
        plt.ylabel("Schaden")
        plt.xlim(self.acRange)
        
        plt.xticks(np.arange(self.acRange[0], self.acRange[1]+1, step=5))
        plt.grid(True, which="major")
        plt.minorticks_on()
        plt.grid(True, which="minor", alpha=0.2, linestyle=":", linewidth=1)
        
        # Grafik als png abspeichern
        plt.savefig("graphDifference.png", format="png",
                    bbox_extra_artists=(legend,), bbox_inches='tight')
        
        # Figure zurückgeben, damit diese bei Bedarf noch weiterverarbeitet
        # werden kann.
        return figDifference
    
    def outputData(self, outputFileName, outputSheet="Sheet1"):
        '''Ausgabe der numerischen Daten in eine Excel-Datei'''
        cols = ["RK"]
        for i in range(0, self.results.shape[1]-1):
            cols.append(self.attacks[i].weapons[0].name)
            
        df = pd.DataFrame(data=self.results,
                          index=np.arange(self.acRange[0], self.acRange[1]+1),
                          columns=cols)
        
        df.to_excel(outputFileName, sheet_name=outputSheet, float_format="%.3f",
                    index=False)
    
    def outputDataComplete(self, outputFileName, outputSheet=None):
        '''Ausgabe der numerischen Daten in eine Excel-Datei. Die Ausgabe
        enthält dabei detaillierte Ergebnisse zu einzelnen Angriffen und Waffen,
        nach GAB aufgeschlüsselt.'''
        pass