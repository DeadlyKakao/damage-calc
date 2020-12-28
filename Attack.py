# -*- coding: utf-8 -*-

import numpy as np
import weapon as wp

class Attack:
    '''Ein Objekt der Klasse Attack enthält eine oder mehrere Waffen als
    Weapon-Objekt. Es fasst die Schadensinformationen aller Waffen zusammen
    und bietet einfachen Zugriff auf die Daten.'''
    
    def __init__(self, dfWeapons, minAC, maxAC):
        self.weapons = []
        # Für jede Waffe in dfWeapons ein neues Weapon-Objekt erstellen.
        for weapon in dfWeapons:
            self.weapons.append(wp.Weapon(weapon, minAC, maxAC))
        
        self.minAC = minAC
        self.maxAC = maxAC
        self.acRange = np.arange(minAC, maxAC+1).transpose()
        self.results = np.arange(minAC, maxAC+1).transpose()
        
        self.results = np.c_[self.results, np.zeros((self.results.shape[0],1))]
        
        self.calcFullAttack()
            
    def listWeapons(self):
        '''Diese Funktion listet die Waffen der Attacke auf, allerdings nur
        mit Namen. Details sind über Weapon.listData() zugänglich'''
        
        for w in self.weapons:
            print (w.name + " " + w.weaponStringHit())
    
    def getSingleAttack(self):
        '''Nimmt den ersten Angriff der ersten Waffe aus self.weapons und gibt
        die Ergebnisse zusammen mit der RK-Spalte zurück'''
        
        return np.c_[self.acRange, self.weapons[0].attackResults[:,1]]
    
    def getFullAttack(self):
        return self.results
    
    def calcFullAttack(self):
        '''Berechnung des Schadens eines vollen Angriffs. Damit sind alle Angriffe
        mit jeweils allen GAB-Einträgen gemeint. Das Ergebnis wird in der Spalte 1
        (2. Spalte) der results-Matrix abgelegt. Jede Spalte dahinter ist der
        volle Angriff einer Waffe, in der Reihenfolge, in der sie in
        self.weapons stehen.'''
        
        for w in self.weapons:
            self.results = np.c_[self.results, w.attackResults[:,0]]
            self.results[:,1] = self.results[:,1] + w.attackResults[:,0]
        