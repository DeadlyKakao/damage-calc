# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

class Weapon :
    '''Diese Klasse beinhaltet eine einzelne hergestellte oder natürliche
    Waffe. Mehrere Waffen können im Rahmen einer Attack zusammengestellt werden.
    Sofern mit einer Waffe im Rahmen eines vollen Angriffs mehrere Angriffe
    möglich sind, ist dies im baseAttacks-Vektor mit den zugehörigen Mail
    festgehalten.'''
    
    def __init__(self, dfWeapon, minAC, maxAC):
        '''Diese Funktion nimmt den übergebenen dfWeapon-DataFrame auseinander
        und sortiert den Inhalt in dafür vorgesehene Variablen ein.'''
        
        self.name = dfWeapon.iloc[0,0]                                          # Name des Angriffs (hilfreich zur Unterscheidung später)
        self.baseDice = self.diceLineConversion(dfWeapon.iloc[1,:].values)      # Grund-Waffenschadenswürfel
        
        # Die Grundangriffszeile enthält so viele Einträge, wie es Angriffe im
        # Fall eines vollen Angriffs gibt, mit den dazugehörigen GAB-Mali.
        # Ein Standardangriff hat dabei den Wert 0, während spätere Angriffe
        # negative Werte aufweisen.
        baseAttacksLine = dfWeapon.iloc[2,:].values
        self.baseAttacks = []
        for i in baseAttacksLine[~pd.isnull(baseAttacksLine)]:
            self.baseAttacks.append(int(i))
        
        self.attackBonus = int(dfWeapon.iloc[3,0])                              # Gesamter Angriffsbonus (GAB eingerechnet)
        self.damageBonus = int(dfWeapon.iloc[4,0])                              # Schadensbonus
        self.critRange = int(dfWeapon.iloc[5,0])                                # min. Würfelergebnis, bei dem eine kritische Bedrohung erzielt werden kann.
        self.critMultiplier = int(dfWeapon.iloc[6,0])                           # Kritischer Schadensmultiplikator
        self.critConfirmBonus = int(dfWeapon.iloc[7,0])                         # Gesonderter Angriffsbonus auf Bestätigungswürfe
        self.precisionDice = self.diceLineConversion(dfWeapon.iloc[8,:].values) # Präzisionsschadenswürfel (bspw. Hinterhältiger Angriff)
        self.precisionDamage = int(dfWeapon.iloc[9,0])                          # Präzisionsschadensbonus
        self.extraDice = self.diceLineConversion(dfWeapon.iloc[10,:].values)    # Zusatzschadenswürfel (bspw. Aufflammen)
        self.extraCritDice = self.diceLineConversion(dfWeapon.iloc[11,:].values)# Zusätzliche kritische Schadenswürfel (bspw. Flammeninferno)
        self.extraDamage = int(dfWeapon.iloc[12,0])                             # Zusatzschaden, der bei kritischem Treffer nicht mitmultipliziert wird
        self.extraCritDamage = int(dfWeapon.iloc[13,0])                         # Zusatzschaden, der nur bei kritischem Treffer berücksichtigt wird.
        self.fortification = dfWeapon.iloc[14,0]*1e-2                           # Bollwerk -> Fehlschlagchance kritischer Treffer
        self.precImmunity = dfWeapon.iloc[15,0]                                 # Immunität gegen Präzisionsschaden? (0: nein, 1: ja)
        self.failChance = dfWeapon.iloc[16,0]*1e-2                              # Fehlschlagchance aufgrund von Tarnung etc., gilt auch für Bestätigungswürfe
        self.damageReduction = int(dfWeapon.iloc[17,0])                         # Schadensreduzierung
        self.acRange = [minAC, maxAC]                                           # RK-Bereich, der für die Rechnung berücksichtigt werden soll
        self.acArray = np.arange(self.acRange[0], self.acRange[1]+1)
        
        # Berechnung der gesamten Schadensboni für normale und kritische Treffer
        # aus den einzelnen Schadensboni.
        self.damageHit = self.damageBonus + self.extraDamage
        if self.precImmunity == 0:
            self.damageHit = self.damageHit + self.precisionDamage
        self.damageCrit = self.damageBonus * self.critMultiplier + self.precisionDamage + self.extraDamage + self.extraCritDamage
        if self.precImmunity == 0:
            self.damageCrit = self.damageCrit + self.precisionDamage
        
        # Berechnung des durchschnittlichen Schadens pro Treffer und pro
        # kritischem Treffer unter Berücksichtigung aller Schadenswürfel und Boni.
        self.avgDamageHit = self.calcDamageHit()
        self.avgDamageCrit = self.calcDamageCrit()
        
        # Berechnung des Schadens-Arrays nach 
        self.attackResults = self.calcAttacks()
    
    def diceLineConversion(self, line):
        '''Die Würfelnotation der Eingabe erfolgt immer in Zellpaaren und
        jede Zeile mit Würfelnotation kann eine oder mehrere dieser Paarungen
        enthalten, die nicht mit der Gesamtlänge der Zeile zusammenhängt.
        Ein Würfelpaar ist immer <Erste Zelle>d<Zweite Zelle>'''
        
        # Da die Zeilenlänge nichts mit der Anzahl der Würfelpaare zu tun hat,
        # zuerst NaN-Einträge entfernen.
        line = line[~pd.isnull(line)]
        # Leere Liste, in die die Würfel als 2-Tupel geschrieben werden.
        diceArray = []
        # Übrige Zellen paarweise durchgehen
        for i in [2*x for x in range(int(line.size/2))]:
            # Einträge mit 0 als Angabe ebenfalls ignorieren
            if line[i] != 0 or line[i+1] != 0:
                diceArray.append((int(line[i]),int(line[i+1])))
        
        return diceArray

    def diceTupleToList(self, diceTupleList):
        '''Einfache Funktion, die aus der Tupel-Darstellung der Schadenswürfel
        eine (nach Würfelgröße sortierte) Liste erstellt.
        [(2,6), (1,8), (1,4)] -> [4, 6, 6, 8]'''
        
        diceList = []
        for t in diceTupleList:
            for i in range(t[0]):
                diceList.append(t[1])
        return sorted(diceList)

    def listData(self):
        '''Diese Funktion stellt eine Ausgabe der Waffendaten zur Verfügung'''
        
        justLength = 26
        print("Waffe:".ljust(justLength) + "{}".format(self.name))
        s = ""
        for t in self.baseDice:
            s = s + str(t[0]) + "W" + str(t[1]) + " + "
        print("Grund-Schadenswürfel:".ljust(justLength) + "{}".format(s[:-3]))
        s = ""
        for t in self.baseAttacks:
            s = s + str(t) + "/"
        print("Voller Angriff:".ljust(justLength) + "{}".format(s[:-1]))
        print("Angriffsbonus:".ljust(justLength) + "{}".format(self.attackBonus))
        print("Schadensbonus:".ljust(justLength) + "{}".format(self.damageBonus))
        print("Bedrohungsbereich:".ljust(justLength) + "{}".format(self.critRange))
        print("Kritischer Multiplikator:".ljust(justLength) + "{}".format(self.critMultiplier))
        print("Bestätigungsbonus:".ljust(justLength) + "{}".format(self.critConfirmBonus))
        s = ""
        for t in self.precisionDice:
            s = s + str(t[0]) + "W" + str(t[1]) + " + "
        print("Präzisionsschadenswürfel:".ljust(justLength) + "{}".format(s[:-3]))
        print("Präzisionsschadensbonus:".ljust(justLength) + "{}".format(self.precisionDamage))
        s = ""
        for t in self.extraDice:
            s = s + str(t[0]) + "W" + str(t[1]) + " + "
        print("Zusatzschadenswürfel:".ljust(justLength) + "{}".format(s[:-3]))
        s = ""
        for t in self.extraCritDice:
            s = s + str(t[0]) + "W" + str(t[1]) + " + "
        print("Kritische Zusatzwürfel:".ljust(justLength) + "{}".format(s[:-3]))
        print("Zusatzschaden:".ljust(justLength) + "{}".format(self.extraDamage))
        print("Kritischer Zusatzschaden:".ljust(justLength) + "{}".format(self.extraCritDamage))
        print("Bollwerk:".ljust(justLength) + "{} %".format(self.fortification*1e2))
        print("Präzisionsimmunität:".ljust(justLength) + "{}".format(self.precImmunity))
        print("Fehlschlagchance:".ljust(justLength) + "{} %".format(self.failChance*1e2))
        print("Schadensreduzierung:".ljust(justLength) + "{}".format(self.damageReduction))
        print("RK-Bereich:".ljust(justLength) + "{} - {}".format(self.acRange[0], self.acRange[1]))
    
    def listDiceHit(self):
        '''Diese Funktion erstellt eine geordnete Liste aller Schadenswürfel
        mit der entsprechenden Anzahl, die im Falle eines normalen Treffers
        gewürfelt werden müssen.
        1W4 + 2W6 + 1W12 wird mit dieser Funktion zu [4, 6, 6, 12]'''
        
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
        '''Diese Funktion funktioniert genau wie listDiceHit(), allerdings
        für kritische Treffer.'''
        
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
    
    def groupDiceHit(self):
        '''Aufstellen eine gruppierten Würfelliste für normale Treffer
        Aus der Würfelliste [3, 3, 4, 6, 6] wird [[2,3], [1,4], [2,6]]'''
        
        diceList = self.listDiceHit()
        # Würfelgruppenliste wird mit dem ersten Eintrag der Würfelliste initialisiert
        diceGroup = [[1, diceList[0]]]
        
        lastDice = diceList[0]
        for d in diceList[1:]:
            if d == lastDice:
                diceGroup[-1][0] = diceGroup[-1][0] + 1
            else:
                diceGroup.append([1,d])
            lastDice = d
        return diceGroup
    
    def groupDiceCrit(self):
        '''Aufstellen eine gruppierten Würfelliste für kritische Treffer'''
        
        diceList = self.listDiceCrit()
        # Würfelgruppenliste wird mit dem ersten Eintrag der Würfelliste initialisiert
        diceGroup = [[1, diceList[0]]]
        
        lastDice = diceList[0]
        for d in diceList[1:]:
            if d == lastDice:
                diceGroup[-1][0] = diceGroup[-1][0] + 1
            else:
                diceGroup.append([1,d])
            lastDice = d
        return diceGroup
    
    def weaponStringHit(self):
        '''Ausgabe einer Zeichenkette, die Angriffsbonus und Schaden für einen
        normalen Treffer abbildet'''
        
        s = ""
        diceGroup = self.groupDiceHit()
        attacks = np.array(self.baseAttacks) + self.attackBonus
        for b in attacks:
            s = s + "{0:+d}".format(b) + "/"
        s = s[:-1] + ", "
        for l in diceGroup:
            s = s + str(l[0]) + "W" + str(l[1]) + " + "
        s = s[:-3]
        damage = self.damageHit
        s = s + "+" + str(damage)
        return s
    
    def weaponStringCrit(self):
        '''Ausgabe einer Zeichenkette, die Angriffsbonus und Schaden für einen
        kritischen Treffer abbildet'''
        
        s = ""
        diceGroup = self.groupDiceCrit()
        attacks = np.array(self.baseAttacks) + self.attackBonus
        for b in attacks:
            s = s + "{0:+d}".format(b) + "/"
        if self.critConfirmBonus != 0:
            s = s[:-1] + " (+" + str(self.critConfirmBonus) + " Bestätigung) "
        s = s[:-1] + ", "
        for l in diceGroup:
            s = s + str(l[0]) + "W" + str(l[1]) + " + "
        s = s[:-3]
        damage = self.damageCrit
        s = s + "+" + str(damage)
        
        return s
    
    def calcDamageHit(self):
        '''Berechnung des durchschnittlichen Schadens pro (normalem) Treffer
        abhängig von den gegebenen Daten des Weapon-Objektes'''
        
        diceList = self.listDiceHit()
        
        # Wenn die Anzahl der möglichen Würfelkombinationen zu hoch ist, die
        # genaue Berechnung nicht durchführen.
        # Wenn der minimale Schaden nicht kleiner als die Schadensreduzierung
        # ist, kann man sich die genaue Berechnung ebenfalls sparen
        minDamage = len(diceList) + self.damageHit
        if minDamage >= self.damageReduction or np.prod(diceList) > 1e6:
            avgDamage = (self.calcDamageFromDice(diceList)
                         + self.damageHit - self.damageReduction)
        
        else:
            print("Würfel-Array erstellt.")
            diceArray = self.createDiceArray(diceList, self.damageHit)
            avgDamage = np.sum(diceArray) / np.size(diceArray)
        
        # Weiterrechnung mit dem durchschnittlichen Schaden pro Treffer
        # Sonderklausel für Präzisionsschadenswürfel und die Bollwerk-Verzauberung
        # Diese kann das Ergebnis mit Schadensreduzierung leicht verfälschen
        if self.fortification != 0:
            avgDamage = avgDamage - (
                self.fortification * 
                self.calcDamageFromDice(self.diceTupleToList(self.precisionDice)))
        
        return avgDamage
        
    def calcDamageCrit(self):
        '''Wie calcDamageHit(), aber für kritische Treffer'''
        
        diceList = self.listDiceCrit()
        
        # Wenn die Anzahl der möglichen Würfelkombinationen zu hoch ist, die
        # genaue Berechnung nicht durchführen.
        # Wenn der minimale Schaden nicht kleiner als die Schadensreduzierung
        # ist, kann man sich die genaue Berechnung ebenfalls sparen
        minDamage = len(diceList) + self.damageCrit
        if minDamage >= self.damageReduction or np.prod(diceList) > 1e6:
            avgDamage = (self.calcDamageFromDice(diceList)
                         + self.damageCrit - self.damageReduction)
        
        else:
            print("Würfel-Array erstellt.")
            diceArray = self.createDiceArray(diceList, self.damageCrit)
            avgDamage = np.sum(diceArray) / np.size(diceArray)
        
        # Weiterrechnung mit dem durchschnittlichen Schaden pro Treffer
        # Sonderklausel für Präzisionsschadenswürfel und die Bollwerk-Verzauberung
        # Diese kann das Ergebnis mit Schadensreduzierung leicht verfälschen
        if self.fortification != 0:
            avgDamage = avgDamage - (
                self.fortification * 
                self.calcDamageFromDice(self.diceTupleToList(self.precisionDice)))
        
        return avgDamage
    
    def calcDamageFromDice(self, diceList):
        '''Diese Funktion berechnet die durchschnittliche Summe eines Wurfes
        der in diceList gegebenen Würfel nach folgender Formel:
        avg(xdy) = x * (y+1)/2'''
        
        damage = 0
        for d in diceList:
            damage = damage + (d+1)/2
        return damage
    
    def createDiceArray(self, diceList, damageBonus):
        '''Diese Funktion liefert ein Numpy-Array mit so vielen Dimensionen
        wie es Schadenswürfel in diceList gibt, gefüllt mit dem Würfelergebnis,
        das eintritt, wenn die Indizes den einzelnen Würfen entsprechen'''
        
        diceArray = np.zeros(tuple(diceList), dtype=int)
        
        # Iterator aus Numpy, der über das mehrdimensionale Array iteriert
        # und die Indizes zusammen addiert, zusammen mit einem Offset in Höhe
        # der Anzahl von Würfeln, um den Index-Start bi 0 statt 1 auszugleichen
        it = np.nditer(diceArray, op_flags=['readwrite'], flags=['multi_index'])
        damageMod = len(diceList) + self.damageBonus - self.damageReduction
        for x in it:
            x[...] = max(np.sum(it.multi_index) + damageMod, 0)
    
        return diceArray
    
    def hitChance(self, bab):
        '''Berechnung der Trefferchance für einen einzelnen Angriff. Die
        Zusatzinformation bab ist nützlich für iterative Angriffe, Sekundärangriffe
        mit natürlichen Waffen und Kampf mit zwei Waffen und hat generell einen
        der folgenden Werte: 0, -2, -5, -7, -10, -12, -15, -17, -20'''
        
        result = np.zeros(self.acArray.size,)
        for i in range(len(result)):
            ac = self.acArray[i]
            baseChance = (self.attackBonus + 21 + bab - ac) * 0.05
            # Aufgrund von Auto-Hit und Auto-Miss bei 5% und 95% cappen.
            if baseChance > 0.95:
                baseChance = 0.95
            elif baseChance < 0.05:
                baseChance = 0.05
            result[i] = baseChance * (1 - self.failChance)
        return result
        
    def critChance(self, bab):
        '''Wie hitChance(), aber berechnet die Chance eines kritischen Treffers'''
        result = np.zeros(self.acArray.size,)
        maxThreat = (21-self.critRange) * 0.05
        for i in range(len(result)):
            ac = self.acArray[i]
            # Zunächst Bedrohungschance (ähnliche Berechnung wie Trefferchance)
            baseChance = (self.attackBonus + 21 + bab - ac) * 0.05
            if baseChance > maxThreat:
                baseChance = maxThreat
            elif baseChance < 0.05:
                baseChance = 0.05
            threatChance = baseChance * (1 - self.failChance)
            
            # Dann die Chance eines bestätigten Treffers
            # baseChance ist eine Hilfsvariable und kann überschrieben werden.
            baseChance = (self.attackBonus + self.critConfirmBonus + 21 + bab - ac) * 0.05
            # Aufgrund von Auto-Hit und Auto-Miss bei 5% und 95% cappen.
            if baseChance > 0.95:
                baseChance = 0.95
            elif baseChance < 0.05:
                baseChance = 0.05
            result[i] = threatChance * baseChance * (1 - self.failChance) * (1 - self.fortification)
        return result
    
    def calcAttacks(self):
        attackResults = np.zeros((self.acArray.size, len(self.baseAttacks)+1))
        
        for b in range(len(self.baseAttacks)):
            bab = self.baseAttacks[b]
            hitChances = self.hitChance(bab)
            critChances = self.critChance(bab)
            attackResults[:,b+1] = self.avgDamageHit * hitChances + (self.avgDamageCrit - self.avgDamageHit) * critChances
            attackResults[:,0] = attackResults[:,0] + attackResults[:,b+1]
            
        return attackResults