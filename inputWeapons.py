# -*- coding: utf-8 -*-

"""
weapon.py provides the Weapon class for weapon representation.

*** Recent Changes: ***
XXXX-XX-XX: Translated comments to English
"""

import pandas as pd

def readInput(fileName, sheet):
    '''Allgemeine Input-Funktion. Nimmt den Dateinamen der Excel-Datei, in der
    sich die Waffendaten befinden und liest den Inhalt als DataFrame ein.
    Die untergeordnete readInputWeapons()-Funktion zerteilt die Eingabe nach
    einzelnen Waffen und Attacken.'''
    
    # Waffendaten aus Excel-Datei einlesen
    # sheet akzeptiert sowohl den Index des Zeichenblattes als auch den Namen
    # als Zeichenkette
    # header=None hindert Pandas daran, die erste Zeile als Kopfzeile zu
    # behandeln, was uns Schwierigkeiten machen würde.
    dfWeapon = pd.read_excel(fileName, sheet_name=sheet, header=None)
    
    # Zelle A1 legt die spezifische Eingabefunktion fest
    # functionFlag = dfWeapon.at[0,0]
    
    # Erste Spalte der Eingabe wird nicht gebraucht
    # dfWeapon = dfWeapon.drop(labels=0, axis=1)
    
    dfWeaponList = readInputWeapons(dfWeapon)
    
    return dfWeaponList

def readInputWeapons(dfWeapon):
    '''Funktion zum Zerlegen des DataFrames aus der Eingabe-Excel-Datei.
    Dieser hat folgende Form
                    Waffe1  Waffe1  ...
    Eigenschaft 1   xxx     xxx     ...
    Eigenschaft 2   xxx     xxx     ...
    
                    Waffe2  Waffe2  ...
    Eigenschaft 1   xxx     xxx     ...
    ...             ...     ...     ...
    
    The weapon properties are fixed regarding their order and may not be mixed
    up.
    '''
    
    # Die erste Spalte enthält Beschreibungen der Zeileninhalte und wird damit
    # genutzt, um die Leerzeilen zu finden, an denen der DataFrame geteilt wird.
    cutIndexHorizontal = [-1]
    
    cutMap = dfWeapon.isna().values
    for i in range(dfWeapon.values.shape[0]):
        if not False in cutMap[i,:]:
            cutIndexHorizontal.append(i)
    
    # Anschließend die erste Spalte abtrennen, sie wird nicht mehr gebraucht.
    dfWeapon = dfWeapon.drop(labels=0, axis=1)
    
    # Nach Leerzeilen suchen. An dieser werden die verschiedenen Angriffe des
    # Sheets voneinander getrennt.
    cutIndexVertical = [-1]

    # dfWeapon.isna() nach True-Spalten durchsuchen, an denen muss getrennt werden.
    cutMap = dfWeapon.isna().values
    for i in range(dfWeapon.values.shape[1]):
        if not False in cutMap[:,i]:
            cutIndexVertical.append(i)
    
    # dfWeapon gemäß der Indizes in cutIndexVertical zerteilen
    # Die Einträge werden in dfAttackList zwischengespeichert, bevor sie im
    # nächsten Schritt weiter zerteilt und in dfWeaponList gesteckt werden.
    dfAttackList = []
    for index in range(1,len(cutIndexVertical)):
        dfAttackList.append(dfWeapon.iloc[:,cutIndexVertical[index-1]+1:cutIndexVertical[index]])
    
    dfAttackList.append(dfWeapon.iloc[:,cutIndexVertical[-1]+1:])

    # Die dabei entstandenen DataFrames werden jetzt horizontal geteilt und
    # in dfWeaponList einsortiert, wobei leere DataFrames weggelassen werden.
    # Leere Waffenliste initialisieren
    dfWeaponList = []

    for a in range(len(dfAttackList)):
        dfWeaponList.append([])
        attack = dfAttackList[a]
        for index in range(1,len(cutIndexHorizontal)):
            subset = attack.iloc[cutIndexHorizontal[index-1]+1:cutIndexHorizontal[index],:]
            if False in subset.isna().values:
                dfWeaponList[a].append(subset)
        subset = attack.iloc[cutIndexHorizontal[-1]+1:,:]
        if False in subset.isna().values:
            dfWeaponList[a].append(subset)
        
    return dfWeaponList