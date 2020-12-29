# -*- coding: utf-8 -*-

"""
attack.py provides the Attack class for attack representation.
An attack consists of one or several weapons.

*** Recent Changes: ***
2020-12-29: Translated comments to English
"""

import numpy as np
import weapon as wp

class Attack:
    """
    The Attack object compiles one or several weapons into a single full attack.
    It summarizes the damage information and provides easier access.
    """
    
    def __init__(self, dfWeapons, name, minAC, maxAC):
        """
        The constructor takes a list of weapon DataFrames and the upper and
        lower bounds of the target AC for all weapon calculations. It creates
        a Weapon object for every DataFrame in dfWeapons and calls the
        calculation routine for a full attack to store the results for later use.

        Parameters
        ----------
        dfWeapons : list
            List of pandas.DataFrame objects which contain the properties of 
            an entire column of weapons, where each weapon is a DataFrame.
        name : str
            Name of the attack as defined in the input file
        minAC : int
            Lower limit of target AC for calculations.
        maxAC : int
            Upper limit of target AC for calculations.

        Returns
        -------
        None.

        """
        
        self.name = name
        self.weapons = []
        # Create a new Weapon object for every weapon DataFrame in dfWeapons.
        for weapon in dfWeapons:
            self.weapons.append(wp.Weapon(weapon, minAC, maxAC))
        
        self.minAC = minAC
        self.maxAC = maxAC
        self.acRange = np.arange(minAC, maxAC+1).transpose()
        self.results = np.arange(minAC, maxAC+1).transpose()
        
        self.results = np.c_[self.results, np.zeros((self.results.shape[0],1))]
        
        self.calcFullAttack()
            
    def listWeapons(self):
        """
        This function lists the weapons of the attack by their
        weaponStringHit() function.

        Returns
        -------
        None.

        """
        
        for w in self.weapons:
            print (w.name + " " + w.weaponStringHit())
    
    def getSingleAttack(self):
        """
        Takes the first attack with the first weapon of self.weapons and returns
        that column along with the AC column.

        Returns
        -------
        np.array
            two-column array with the first columns being the target ACs between
            minAC and maxAC and the second one being the average damage per single
            attack of the first weapon.

        """
        
        return np.c_[self.acRange, self.weapons[0].attackResults[:,1]]
    
    def getFullAttack(self):
        """
        Returns the results of a full attack with all weapons of self.

        Returns
        -------
        np.array
            Full results array.

        """
        
        return self.results
    
    def calcFullAttack(self):
        """
        Calculates the average damage of a full attack. This includes every weapon
        with every BAB entry. The result appears in column 1 (second column) of
        the results array. Every column thereafter is the average full attack
        damage of one weapon in the order which is maintained in self.weapons.

        Returns
        -------
        None.

        """
        
        for w in self.weapons:
            self.results = np.c_[self.results, w.attackResults[:,0]]
            self.results[:,1] += w.attackResults[:,0]
