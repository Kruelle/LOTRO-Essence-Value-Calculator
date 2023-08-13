import os
import xml.etree.ElementTree as ETree
import pandas as pd
import numpy as np
import argparse

#File path to the most recent Lotro-Companion xml items db
#Download from https://github.com/LotroCompanion/lotro-items-db
items_xml_fp = '/Users/brand/Downloads/lotro_items_u34_3.xml'
save_pth = '/Users/brand/Desktop/Lotro Items Python Sandbox/lotro_items_u34_3_v6.csv'

def parse_items_xml(fp = items_xml_fp):
    #Parse with ETree, then convert to pandas dataframe
    #Read file, get root
    prstree = ETree.parse(fp)
    root = prstree.getroot()

    # Initialize lists
    item_stats = []
    all_items = []

    #Iterate thru the highest level xml tree
    for itemNo in root.iter('item'):

        #Base Attributes
        itemId = itemNo.attrib.get('key')
        itemName = itemNo.attrib.get('name')
        iconId = itemNo.attrib.get('icon')
        iLvl = itemNo.attrib.get('level')
        slot = itemNo.attrib.get('slot')
        category = itemNo.attrib.get('category')
        classId = itemNo.attrib.get('class')
        equipmentCategory = itemNo.attrib.get('equipmentCategory')
        binding = itemNo.attrib.get('binding')
        durability = itemNo.attrib.get('durability')
        sturdiness = itemNo.attrib.get('sturdiness')
        quality = itemNo.attrib.get('quality')
        valueTableId = itemNo.attrib.get('valueTableId')
        armourType = itemNo.attrib.get('armourType')
        #stats
        dps = itemNo.attrib.get('dps')
        minDamage = itemNo.attrib.get('minDamage')
        maxDamage = itemNo.attrib.get('maxDamage')
        damageType = itemNo.attrib.get('damageType')
        weaponType = itemNo.attrib.get('weaponType')
        description = itemNo.attrib.get('description')
        unique = itemNo.attrib.get('unique')
        minLevel = itemNo.attrib.get('minLevel')
        stackMax = itemNo.attrib.get('stackMax')
        grants = itemNo.attrib.get('grants')
        requiredClass = itemNo.attrib.get('requiredClass')
        requiredRace = itemNo.attrib.get('requiredRace')
        maxLevel = itemNo.attrib.get('maxLevel')
        requiredFaction = itemNo.attrib.get('requiredFaction')
        reputation = itemNo.attrib.get('reputation')
        itemLevelOffset = itemNo.attrib.get('itemLevelOffset')
        mainLegacyId = itemNo.attrib.get('mainLegacyId')
        mainLegacyBaseRank = itemNo.attrib.get('mainLegacyBaseRank')
        itemProperty = itemNo.attrib.get('property')
        itemXP = itemNo.attrib.get('itemXP')
        virtueXP = itemNo.attrib.get('virtueXP')
        essenceSlots = itemNo.attrib.get('slots')
        maxItems = itemNo.attrib.get('maxItems')
        itemStackMax = itemNo.attrib.get('itemsStackMax')

        #Add stats from xml subtree
        #Empty value for each important stat type
        vitStat = 0
        vitScaling = 0
        willStat = 0
        willScaling = 0
        agiStat = 0
        agiScaling = 0
        mightStat = 0
        mightScaling = 0
        fateStat = 0
        fateScaling = 0
        moraleStat = 0
        moraleScaling = 0
        finesseStat = 0
        finesseScaling = 0
        critStat = 0
        critScaling = 0
        oghStat = 0
        oghScaling = 0
        inchStat = 0
        inchScaling = 0
        tmastStat = 0
        tmastScaling = 0
        pmastStat = 0
        pmastScaling = 0
        tmitStat = 0
        tmitScaling = 0
        pmitStat = 0
        pmitScaling = 0
        blockStat = 0
        blockScaling = 0
        parryStat = 0
        parryScaling = 0
        evadeStat = 0
        evadeScaling = 0
        critdStat = 0
        critdScaling = 0
        resistStat = 0
        resistScaling = 0
        armourStat = 0
        armourScaling = 0

        #Iterate over stats subtree
        for stat in itemNo.iter('stat'):

            #Get the stat name and vals
            statName = stat.attrib.get('name')
            statVal = stat.attrib.get('value')
            statScaling = stat.attrib.get('scaling')
            rangedScaling = stat.attrib.get('ranged')
            if rangedScaling is not None:
                statScaling = rangedScaling.split(":")[1] #Ignore the range... This might break things eventually but probably okay for now

            #Slot stat values into correct vars
            if (statName == 'VITALITY'):
                vitStat = statVal
                vitScaling = statScaling
            elif (statName == 'WILL'):
                willStat = statVal
                willScaling = statScaling
            elif (statName == 'AGILITY'):
                agiStat = statVal
                agiScaling = statScaling
            elif (statName == 'MIGHT'):
                mightStat = statVal
                mightScaling = statScaling
            elif (statName == 'FATE'):
                fateStat = statVal
                fateScaling = statScaling
            elif (statName == 'MORALE'):
                moraleStat = statVal
                moraleScaling = statScaling
            elif (statName == 'FINESSE'):
                finesseStat = statVal
                finesseScaling = statScaling
            elif (statName == 'CRITICAL_RATING'):
                critStat = statVal
                critScaling = statScaling
            elif (statName == 'OUTGOING_HEALING'):
                oghStat = statVal
                oghScaling = statScaling
            elif (statName == 'INCOMING_HEALING'):
                inchStat = statVal
                inchScaling = statScaling
            elif (statName == 'TACTICAL_MASTERY'):
                tmastStat = statVal
                tmastScaling = statScaling
            elif (statName == 'PHYSICAL_MASTERY'):
                pmastStat = statVal
                pmastScaling = statScaling
            elif (statName == 'TACTICAL_MITIGATION'):
                tmitStat = statVal
                tmitScaling = statScaling
            elif (statName == 'PHYSICAL_MITIGATION'):
                pmitStat = statVal
                pmitScaling = statScaling
            elif (statName == 'BLOCK'):
                blockStat = statVal
                blockScaling = statScaling
            elif (statName == 'PARRY'):
                parryStat = statVal
                parryScaling = statScaling
            elif (statName == 'EVADE'):
                evadeStat = statVal
                evadeScaling = statScaling
            elif (statName == 'CRITICAL_DEFENSE'):
                critdStat = statVal
                critdScaling = statScaling
            elif (statName == 'RESISTANCE'):
                resistStat = statVal
                resistScaling = statScaling
            elif (statName == 'ARMOUR'):
                armourStat = statVal
                armourScaling = statScaling

        #Make single list of all stats
        item_stats = [itemId, itemName, iconId, iLvl, slot, category, classId, equipmentCategory, binding, 
                      durability, sturdiness, quality, valueTableId, armourType, dps, minDamage, maxDamage,
                      damageType, weaponType, description, unique, minLevel, stackMax, grants, requiredClass, 
                      requiredRace, maxLevel, requiredFaction, reputation, itemLevelOffset, mainLegacyId, 
                      mainLegacyBaseRank, itemProperty, itemXP, virtueXP, essenceSlots, maxItems, itemStackMax,
                      vitStat, vitScaling,willStat,willScaling, agiStat, agiScaling, mightStat, mightScaling, 
                      fateStat, fateScaling, moraleStat, moraleScaling, finesseStat, finesseScaling, critStat, 
                      critScaling, oghStat, oghScaling, inchStat, inchScaling, tmastStat, tmastScaling, pmastStat, 
                      pmastScaling, tmitStat, tmitScaling, pmitStat, pmitScaling, blockStat, blockScaling, parryStat, 
                      parryScaling, evadeStat, evadeScaling, critdStat, critdScaling, resistStat, resistScaling, 
                      armourStat, armourScaling]

        #Add to list of all items
        all_items.append(item_stats)

    #convert items lists to pandas dataframe with correlated named columns
    column_names = ['itemId', 'itemName', 'iconId', 'iLvl', 'slot', 'category', 'classId', 'equipmentCategory', 'binding', 
                      'durability', 'sturdiness', 'quality', 'valueTableId', 'armourType', 'dps', 'minDamage', 'maxDamage',
                      'damageType', 'weaponType', 'description', 'unique', 'minLevel', 'stackMax', 'grants', 'requiredClass', 
                      'requiredRace', 'maxLevel', 'requiredFaction', 'reputation', 'itemLevelOffset', 'mainLegacyId', 
                      'mainLegacyBaseRank', 'itemProperty', 'itemXP', 'virtueXP', 'essenceSlots', 'maxItems', 'itemStackMax',
                      'vitStat', 'Vitality Scaling', 'willStat', 'Will Scaling', 'agiStat', 'Agility Scaling', 'mightStat', 'Might Scaling', 
                      'fateStat', 'Fate Scaling', 'moraleStat', 'Maximum Morale Scaling', 'finesseStat', 'Finesse Scaling', 'critStat', 
                      'Critical Rating Scaling', 'oghStat', 'Outgoing Healing Rating Scaling', 'inchStat', 
                      'Incoming Healing Rating Scaling', 'tmastStat', 'Tactical Mastery Scaling', 'pmastStat', 
                      'Physical Mastery Scaling', 'tmitStat', 'Tactical Mitigation Scaling', 'pmitStat', 
                      'Physical Mitigation Scaling', 'blockStat', 'Block Rating Scaling', 'parryStat', 
                      'Parry Rating Scaling', 'evadeStat', 'Evade Rating Scaling', 'critdStat', 'Critical Defense Scaling', 
                      'resistStat', 'Resistance Rating Scaling', 'armourStat', 'Armour Scaling']
    itemsDf = pd.DataFrame(all_items,columns=column_names)
    
    return itemsDf

def clean_items_df(itemsDf):
    #prune DF
    goodCategories = ['ARMOUR', 'WEAPON', 'ITEM']
    itemsDf = itemsDf[itemsDf['category'].isin(goodCategories)] #Get rid of items from categories we don't care about
    itemsDf = itemsDf[itemsDf['slot'].notna()] #Get rid of items with no slot
    badSlots = ['TOOL', 'MAIN_HAND_AURA', 'BRIDLE']
    itemsDf = itemsDf[~itemsDf['slot'].isin(badSlots)] #Get rid of items that slot into places we don't care about
    itemsDf = itemsDf[itemsDf['iLvl'] != '1'] #Remove things with iLvl=1 to remove cosmetics
    itemsDf['iLvl'] = itemsDf['iLvl'].astype(int)
    itemsDf = itemsDf[itemsDf['iLvl'] > 99] #Clip to iLvl >= 100 #TODO: Put this into argparser
    
    #Remove accents from letters
    itemsDf['itemName'] = itemsDf['itemName'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    
    #Sort the DF
    sortedDf = itemsDf.sort_values(by=['itemName'], ascending=True)
    
    return sortedDf

#Example call: Python item_parsing.py -f u35_items.xml -s u35_items.csv
def main(args):
    #Make sure xml file path exists
    if not os.path.isfile(args.items_fp):
        print(f"File '{args.items_fp}' does not exist.")
        return -1
    
    df = parse_items_xml(fp=args.items_fp)
    df = clean_items_df(df)
    df.to_csv(args.save_fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse the items database .xml file and save as csv")
    parser.add_argument('--items_fp', '-f', type=str, help="File path to xml of items db (download from LotroCompanion)",required=True)
    parser.add_argument('--save_fp', '-s', type=str, help="Save path/name for csv (include .csv extension)", required=True)
    args = parser.parse_args()
    main(args)  