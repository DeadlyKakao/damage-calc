# -*- coding: utf-8 -*-

"""
weapon.py provides the Weapon class for weapon representation.

*** Recent Changes: ***
2020-12-29: Translated comments to English,
    refactored the groupDice*() functions to a single groupDice(diceList) function
    removed damageBonus argument from createDiceArray()
"""

import numpy as np
import pandas as pd

class Weapon :
    """
    The Weapon class represents a single manufactured or natural weapon.
    Several weapons can be assembled in the form of an Attack object.
    """
    
    def __init__(self, dfWeapon, minAC, maxAC):
        """
        The constructor of the Weapon class takes a Pandas.DataFrame with all
        important weapon data and sorts it into object variables.
        
        dfWeapon: DataFrame containing weapon properties
        minAC:    Minimum target AC for hit chance calculations
        maxAC:    Maximum target AC for hit chance calculations

        Parameters
        ----------
        dfWeapon : pandas.DataFrame
            DataFrame which contains every weapon property from the input file.
        minAC :    int
            Lower limit of target AC for calculations.
        maxAC :    int
            Upper limit of target AC for calculations.

        Returns
        -------
        self : Weapon
        """
        
        self.name = dfWeapon.iloc[0,0]                                          # Weapon name: Useful for distinction in the later results
        self.baseDice = self.diceLineConversion(dfWeapon.iloc[1,:].values)      # Base Weapon Damage Dice
        
        """
        The baseAttacks list contains as many elements as the weapon has
        attacks in a full attack. Every element matches the corresponding
        BAB penalty. A standard weapon with BAB=8 (2 attacks on a full attack)
        would yield [0, -5] as baseAttacks. The same weapon with the haste
        buff has [0, 0, -5] as baseAttacks as haste grants an extra attack
        at full BAB. Penalties from two-weapon fighting should also be
        considered in baseAttacks
        If the wielder adds an off-hand weapon with the TWF and ITWF feats,
        baseAttacks becomes [-2, -2, -7], while the off-hand weapon (which is
        a separate Weapon object) gets [-2, -7]
        """
        baseAttacksLine = dfWeapon.iloc[2,:].values
        self.baseAttacks = []
        for i in baseAttacksLine[~pd.isnull(baseAttacksLine)]:
            self.baseAttacks.append(int(i))
        
        self.attackBonus = int(dfWeapon.iloc[3,0])                              # Overall Attack Bonus (BAB factored in)
        self.damageBonus = int(dfWeapon.iloc[4,0])                              # Overall Damage Bonus
        self.critRange = int(dfWeapon.iloc[5,0])                                # Critical Threat Range (minimum result of d20 which can threaten a critical hit)
        self.critMultiplier = int(dfWeapon.iloc[6,0])                           # Critical Damage Multiplier
        self.critConfirmBonus = int(dfWeapon.iloc[7,0])                         # Separate Attack Bonus for Critical Confirmation Rolls
        self.precisionDice = self.diceLineConversion(dfWeapon.iloc[8,:].values) # Precision Damage Dice (e.g. Sneak Attack)
        self.precisionDamage = int(dfWeapon.iloc[9,0])                          # Precision Damage Bonus
        self.extraDice = self.diceLineConversion(dfWeapon.iloc[10,:].values)    # Additional Damage Dice (e.g. Flaming)
        self.extraCritDice = self.diceLineConversion(dfWeapon.iloc[11,:].values)# Additional Critical Damage Dice (e.g. Flaming Burst)
        self.extraDamage = int(dfWeapon.iloc[12,0])                             # Additional Damage that is not multiplied on a critical hit
        self.extraCritDamage = int(dfWeapon.iloc[13,0])                         # Additional Damage that only comes in on a critical hit (not multiplied by Critical Damage Multiplier)
        self.fortification = dfWeapon.iloc[14,0]*1e-2                           # Fortification -> Chance for critical hits or precision damage to be nullified.
        self.precImmunity = dfWeapon.iloc[15,0]                                 # Immunity versus Precision Damage (0: not immune, 1: immune)
        self.failChance = dfWeapon.iloc[16,0]*1e-2                              # Failure chance due to concealment or similar effects. Also affects confirmation rolls
        self.damageReduction = int(dfWeapon.iloc[17,0])                         # Target Damage Reduction
        self.acRange = [minAC, maxAC]                                           # AC range to consider for damage calculations
        self.acArray = np.arange(self.acRange[0], self.acRange[1]+1)
        
        # Calculation of overall damage bonus for normal and critical hits
        # from the individual damage bonuses
        # Immunity vs. precision damage is considered here
        self.damageHit = self.damageBonus + self.extraDamage
        if self.precImmunity == 0:
            self.damageHit += self.precisionDamage
        self.damageCrit = self.damageBonus * self.critMultiplier + self.precisionDamage + self.extraDamage + self.extraCritDamage
        if self.precImmunity == 0:
            self.damageCrit += self.precisionDamage
        
        # Calculation of average damage per hit and per critical hit
        # considering all damage dice and bonuses
        self.avgDamageHit = self.calcDamageHit()
        self.avgDamageCrit = self.calcDamageCrit()
        
        # Calculation of average damage array considering the given AC range
        self.attackResults = self.calcAttacks()
    
    def diceLineConversion(self, line):
        """
        The input dice notation always occurs in pairs of table cells and every
        row with dice notation can contain no, one or more of those pairs,
        which has no connection to the actual row length, which is just
        determined from the longest row in the entire array.
        A dice pair is always <first cell>d<second cell>.
        This function returns a list of 2-tuples containing these dice pairs.

        Parameters
        ----------
        line : pandas.DataFrame
            Input line which contains the dice description in cell pairs.

        Returns
        -------
        diceArray : list
            List of 2-tuples which describe the dice number and types given
            in a single line of the input file, in the form of
            a1db1, a2db2 -> [(a1,b1), (a2,b2)].
        """
        
        # Remove NaN entries in the passed line
        line = line[~pd.isnull(line)]
        # Initialise empty list which takes the dice pairs as tuples
        diceArray = []
        # Cycle through non-NaN cells in pairs
        for i in [2*x for x in range(int(line.size/2))]:
            # Ignore any pair where one of the cells contains zero
            if line[i] != 0 and line[i+1] != 0:
                diceArray.append((int(line[i]),int(line[i+1])))
        
        return diceArray

    def diceTupleToList(self, diceTupleList):
        """
        Simple function to convert the tuple notation of dice pairs to a list
        which is sorted by die size.
        Example: [(2,6), (1,8), (1,4)] -> [4, 6, 6, 8]

        Parameters
        ----------
        diceTupleList : list
            List of dice tuples to compile into a list.

        Returns
        -------
        sorted(diceList) : list
            List of dice from a given dice tuple list n the form of
            [x, ..., x, y, ..., y, ...], sorted ascending by dice type.
        """
        
        diceList = []
        for t in diceTupleList:
            for i in range(t[0]):
                diceList.append(t[1])
        return sorted(diceList)

    def listData(self):
        """
        Output function that prints weapon properties to the console.

        Parameters
        ----------
        None

        Returns
        -------
        None.
        
        """
        
        justLength = 30
        print("Weapon:".ljust(justLength) + "{}".format(self.name))
        s = ""
        for t in self.baseDice:
            s += str(t[0]) + "d" + str(t[1]) + " + "
        print("Base Damage Dice:".ljust(justLength) + "{}".format(s[:-3]))
        s = ""
        for t in self.baseAttacks:
            s += str(t) + "/"
        print("Full Attack:".ljust(justLength) + "{}".format(s[:-1]))
        print("Attack Bonus:".ljust(justLength) + "{}".format(self.attackBonus))
        print("Damage Bonus:".ljust(justLength) + "{}".format(self.damageBonus))
        print("Critical Threat Range:".ljust(justLength) + "{}".format(self.critRange))
        print("Critical Multiplier:".ljust(justLength) + "{}".format(self.critMultiplier))
        print("Confirmation Bonus:".ljust(justLength) + "{}".format(self.critConfirmBonus))
        s = ""
        for t in self.precisionDice:
            s += str(t[0]) + "d" + str(t[1]) + " + "
        print("Precision Damage Dice:".ljust(justLength) + "{}".format(s[:-3]))
        print("Precision Damage Bonus:".ljust(justLength) + "{}".format(self.precisionDamage))
        s = ""
        for t in self.extraDice:
            s += str(t[0]) + "d" + str(t[1]) + " + "
        print("Additional Damage Dice:".ljust(justLength) + "{}".format(s[:-3]))
        s = ""
        for t in self.extraCritDice:
            s += str(t[0]) + "d" + str(t[1]) + " + "
        print("Additional Critical Dice:".ljust(justLength) + "{}".format(s[:-3]))
        print("Bonus Damage (no Crit.):".ljust(justLength) + "{}".format(self.extraDamage))
        print("Bonus Damage (only on Crit.):".ljust(justLength) + "{}".format(self.extraCritDamage))
        print("Fortification Chance:".ljust(justLength) + "{} %".format(self.fortification*1e2))
        print("Immunity vs. Precision:".ljust(justLength) + "{}".format(self.precImmunity))
        print("Failure Chance:".ljust(justLength) + "{} %".format(self.failChance*1e2))
        print("Damage Reduction:".ljust(justLength) + "{}".format(self.damageReduction))
    
    def listDiceHit(self):
        """
        This function generates a sorted list of all damage dice which need to
        be rolled on a normal hit.
        Example: 1d4 + 2d6 + 1d12 becomes [4, 6, 6, 12]

        Parameters
        ----------
        None

        Returns
        -------
        sorted(diceList) : list
            List of damage dice for a normal hit in the form of
            [x, ..., x, y, ..., y, ...], sorted ascending by dice type.
        """
        
        diceList = []
        for t in self.baseDice:
            for i in range(t[0]):
                diceList.append(t[1])
        if self.precImmunity == 0:
            for t in self.precisionDice:
                for i in range(t[0]):
                    diceList.append(t[1])
        for t in self.extraDice:
            for i in range(t[0]):
                diceList.append(t[1])
        return sorted(diceList)
        
    def listDiceCrit(self):
        """
        As listDiceHit(), but for critical hits

        Parameters
        ----------
        None.

        Returns
        -------
        sorted(diceList) : list
            List of damage dice for a critical hit in the form of
            [x, ..., x, y, ..., y, ...], sorted ascending by dice type.
        """
        
        diceList = []
        for t in self.baseDice:
            for i in range(t[0]):
                for j in range(self.critMultiplier):
                    diceList.append(t[1])
        if self.precImmunity == 0:
            for t in self.precisionDice:
                for i in range(t[0]):
                    diceList.append(t[1])
        for t in self.extraDice:
            for i in range(t[0]):
                diceList.append(t[1])
        for t in self.extraCritDice:
            for i in range(t[0]):
                diceList.append(t[1])
        return sorted(diceList)
    
    def groupDice(self, diceList):
        """
        This function generates a grouped list of dice from an ungrouped list.
        Example: [3, 3, 4, 6, 6] becomes [[2,3], [1,4], [2,6]]

        Parameters
        ----------
        diceList : list
            List of dice to group.

        Returns
        -------
        diceGroup : list
            List containing a list for every dice type in the form of [x, y]
            corresponding to xdy.
        """
        
        # The input list is assumed to be sorted because every function that
        # generates such a list returns it sorted.
        # list is initialised with the first entry from the passed dice list.
        diceGroup = [[1, diceList[0]]]
        
        lastDice = diceList[0]
        # Cycle through list
        for d in diceList[1:]:
            if d == lastDice:
                diceGroup[-1][0] += 1
            else:
                diceGroup.append([1,d])
            lastDice = d
        return diceGroup
    
    def weaponStringHit(self):
        """
        Outputs a short string with full attack bonuses and damage expression
        for a normal hit.

        Parameters
        ----------
        None

        Returns
        -------
        s : str
            Short weapon rolls description with normal damage.
        """
        
        s = ""
        diceGroup = self.groupDice(self.listDiceHit())
        attacks = np.array(self.baseAttacks) + self.attackBonus
        for b in attacks:
            s += "{0:+d}".format(b) + "/"
        s = s[:-1] + ", "
        for l in diceGroup:
            s += str(l[0]) + "d" + str(l[1]) + " + "
        s = s[:-3]
        damage = self.damageHit
        s += "+" + str(damage)
        return s
    
    def weaponStringCrit(self):
        """
        As weaponStringHit(), but for critical hits.

        Parameters
        ----------
        None

        Returns
        -------
        s : str
            Short weapon rolls description with critical damage.
        """
        
        s = ""
        diceGroup = self.groupDice(self.listDiceCrit())
        attacks = np.array(self.baseAttacks) + self.attackBonus
        for b in attacks:
            s += "{0:+d}".format(b) + "/"
        if self.critConfirmBonus != 0:
            s = s[:-1] + " (+" + str(self.critConfirmBonus) + " Confirmation) "
        s = s[:-1] + ", "
        for l in diceGroup:
            s += str(l[0]) + "d" + str(l[1]) + " + "
        s = s[:-3]
        damage = self.damageCrit
        s += "+" + str(damage)
        
        return s
    
    def calcDamageHit(self):
        """
        Calculation of average damage per normal hit from weapon properties.
        This function generates a np.array with as many dimensions as damage dice
        to calculate every possible dice outcome in order to accurately represent
        the influence of damage reduction on the average damage since it can
        not reduce damage dealt below zero, thus damage reduction vastly
        complicates the damage calculation.
        This array grows exponentially with amount of dice which quickly becomes
        a problem with weapons that get several additional dice like sneak attacks.
        The array size is capped to prevent calculation times of several minutes.
        The program also checks if the damage reduction is actually able to
        reduce damage dealt to zero, otherwise the creation of a dice array is
        not necessary.

        Parameters
        ----------
        None

        Returns
        -------
        avgDamage : float
            Average damage per normal hit.
        """
        
        # Get dice list for normal hits
        diceList = self.listDiceHit()
        
        # Two conditions need to be met for the program to create the complete
        # dice array:
        # The size of the array (= possible dice combinations) needs to be
        # below 1e6 and the damage reduction must be greater than the minimum
        # damage roll (every die rolls a one)
        minDamage = len(diceList) + self.damageHit
        if minDamage >= self.damageReduction or np.prod(diceList) > 1e6:
            
            # Without complete dice array, the average damage is calculated as
            # average dice roll plus bonuses minus damage reduction
            avgDamage = (self.calcDamageFromDice(diceList)
                         + self.damageHit - self.damageReduction)
        
        else:
            print("Created complete dice array.")
            diceArray = self.createDiceArray(diceList, self.damageHit)
            avgDamage = np.sum(diceArray) / np.size(diceArray)
        
        # Extra condiction for fortification and precision damage dice
        # This can slightly falsify the result with damage reduction
        # Note: Fortification does not affect flat precision damage bonuses.
        if self.fortification != 0:
            avgDamage -= (self.fortification * 
                self.calcDamageFromDice(self.diceTupleToList(self.precisionDice)))
        
        return avgDamage
        
    def calcDamageCrit(self):
        """
        As calcDamageHit(), but for critical hits

        Parameters
        ----------
        None

        Returns
        -------
        avgDamage : float
            Average damage per critical hit.
        """
        
        # Get dice list for critical hits
        diceList = self.listDiceCrit()
        
        # Two conditions need to be met for the program to create the complete
        # dice array:
        # The size of the array (= possible dice combinations) needs to be
        # below 1e6 and the damage reduction must be greater than the minimum
        # damage roll (every die rolls a one)
        minDamage = len(diceList) + self.damageCrit
        if minDamage >= self.damageReduction or np.prod(diceList) > 1e6:
            avgDamage = (self.calcDamageFromDice(diceList)
                         + self.damageCrit - self.damageReduction)
        
        else:
            print("Created complete dice array.")
            diceArray = self.createDiceArray(diceList, self.damageCrit)
            avgDamage = np.sum(diceArray) / np.size(diceArray)
        
        # Extra condiction for fortification and precision damage dice
        # This can slightly falsify the result with damage reduction
        # Note: Fortification does not affect flat precision damage bonuses.
        if self.fortification != 0:
            avgDamage -= (self.fortification * 
                self.calcDamageFromDice(self.diceTupleToList(self.precisionDice)))
        
        return avgDamage
    
    def calcDamageFromDice(self, diceList):
        """
        This function calculates the average dice roll according to this formula:
        avg(xdy) = x * (y+1)/2

        Parameters
        ----------
        diceList : list
            List of dice to calculate average damage from.

        Returns
        -------
        damage : float
            Average roll of given dice list.
        """
        
        damage = 0
        for d in diceList:
            damage += (d+1)/2
        return damage
    
    def createDiceArray(self, diceList):
        """
        This function creates an array for a given list of dice with as many
        dimensions as damage dice, where every dimension is as long als the
        correspoding die has sides, which contains the result of every possible
        roll combination with the array index indicating the single die result -1.
        Damage bonuses and damage reduction are subsequently applied to this
        array element-wise.
        The array for 2d4+3 would look like this:
            0   1   2   3
        0   5   6   7   8
        1   6   7   8   9
        2   7   8   9   10
        3   8   9   10  11

        Parameters
        ----------
        diceList : list
            List of dice to create array from.

        Returns
        -------
        diceArray : ndarray
            Array filled with the sum of every possible dice roll combination.
        """
        
        diceArray = np.zeros(tuple(diceList), dtype=int)
        
        # nditer is a powerful iterator that iterates over every single array
        # element and is able to access the indices of every element in order
        # to calculate the dice results from them.
        it = np.nditer(diceArray, op_flags=['readwrite'], flags=['multi_index'])
        
        # len(diceList) is the offset between the sum of array indices and actual
        # result, since arrays start indexing at zero and dice start at one.
        damageMod = len(diceList) + self.damageHit - self.damageReduction
        for x in it:
            x[...] = max(np.sum(it.multi_index) + damageMod, 0)
    
        return diceArray
    
    def hitChance(self, bab):
        """
        Hit chance calculation for a single attack with a single weapon. The
        hit chance is appropriately modified by the given BAB penalty depending
        on the attack.

        Parameters
        ----------
        bab : int
            Additional roll penalty for iterative attacks, twf, secondary etc.

        Returns
        -------
        result : np.array
            Hit chance for every AC in the given AC range.
        """
        
        result = np.zeros(self.acArray.size,)
        for i in range(len(result)):
            ac = self.acArray[i]
            baseChance = (self.attackBonus + 21 + bab - ac) * 0.05
            
            # Chance is capped at 5% and 9% due to auto-hit and auto-miss
            if baseChance > 0.95:
                baseChance = 0.95
            elif baseChance < 0.05:
                baseChance = 0.05
            result[i] = baseChance * (1 - self.failChance)
        return result
        
    def critChance(self, bab):
        """
        As hitChance(bab), but for the chance of critical hits.

        Parameters
        ----------
        bab : int
            Additional roll penalty for iterative attacks, twf, secondary etc.

        Returns
        -------
        result : np.array
            Critical hit chance for every AC in the given AC range.
        """
        
        result = np.zeros(self.acArray.size,)
        maxThreat = (21-self.critRange) * 0.05
        for i in range(len(result)):
            ac = self.acArray[i]
            
            # Threat chance is calculated similarly to hit chance
            baseChance = (self.attackBonus + 21 + bab - ac) * 0.05
            if baseChance > maxThreat:
                baseChance = maxThreat
            elif baseChance < 0.05:
                baseChance = 0.05
            threatChance = baseChance * (1 - self.failChance)
            
            # Chance of confirmation
            # baseChance is an auxiliary variable and can be overwritten safely
            baseChance = (self.attackBonus + self.critConfirmBonus + 21 + bab - ac) * 0.05
            # Chance is capped at 5% and 9% due to auto-hit and auto-miss
            # Auto-hit, auto-miss and failure chance are applied to confirmation rolls
            if baseChance > 0.95:
                baseChance = 0.95
            elif baseChance < 0.05:
                baseChance = 0.05
            result[i] = threatChance * baseChance * (1 - self.failChance) * (1 - self.fortification)
        return result
    
    def calcAttacks(self):
        """
        This function assembles an array with average damage values for every
        element in self.baseAttacks, while the first columns contains the sum
        of every row.

        Parameters
        ----------
        None

        Returns
        -------
        attackResults : np.array
            Average damage of weapon, corresponding to target AC.

        """
        attackResults = np.zeros((self.acArray.size, len(self.baseAttacks)+1))
        
        for b in range(len(self.baseAttacks)):
            bab = self.baseAttacks[b]
            hitChances = self.hitChance(bab)
            critChances = self.critChance(bab)
            attackResults[:,b+1] = self.avgDamageHit * hitChances + (self.avgDamageCrit - self.avgDamageHit) * critChances
            attackResults[:,0] = attackResults[:,0] + attackResults[:,b+1]
            
        return attackResults