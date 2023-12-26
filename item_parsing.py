import os
import xml.etree.ElementTree as ETree
import polars as pl
import numpy as np
import argparse
from unicodedata import normalize

#File path to the most recent Lotro-Companion xml items db
#Download from https://github.com/LotroCompanion/lotro-items-db
items_xml_fp = '/Users/brand/Downloads/lotro_items_u34_3.xml'
save_pth = '/Users/brand/Desktop/Lotro Items Python Sandbox/lotro_items_u34_3_v6.csv'

STAT_NAME_MAP = {
    "VITALITY": "Vitality Scaling",
    "AGILITY": "Agility Scaling",
    "WILL": "Will Scaling",
    "MIGHT": "Might Scaling",
    "FATE": "Fate Scaling",
    "MORALE": "Maximum Morale Scaling",
    "FINESSE": "Finesse Scaling",
    "CRITICAL_RATING": "Critical Rating Scaling",
    "OUTGOING_HEALING": "Outgoing Healing Rating Scaling",
    "INCOMING_HEALING": "Incoming Healing Rating Scaling",
    "TACTICAL_MASTERY": "Tactical Mastery Scaling",
    "PHYSICAL_MASTERY": "Physical Mastery Scaling",
    "TACTICAL_MITIGATION": "Tactical Mitigation Scaling",
    "PHYSICAL MITIGATION":"Physical Mitigation Scaling",
    "BLOCK": "Block Rating Scaling",
    "PARRY": "Parry Rating Scaling",
    "EVADE": "Evade Rating Scaling",
    "CRITICAL_DEFENCE": "Critical Defense Scaling",
    "RESISTANCE": "Resistance Rating Scaling",
    "ARMOUR": "Armour Scaling",
    "POWER": "Maximum Power Scaling",
    "OCPR": "Out of Combat Power Regen Scaling",
    "ICPR": "In Combat Power Regen Scaling",
    "ICMR": "In Combat Morale Regen Scaling",
    "OCMR": "Out of Combat Morale Regen Scaling"
}
ATTRIB_NAME_MAP = {
    'key': "itemId",
    "name": "itemName",
    "icon": "iconId",
    "level": "iLvl",
    "class": "classId",
    "property": "itemProperty",
    "slots": "essenceSlots",
}
ATTRIB_NAMES = ['key', 'name', 'icon', 'level', 'slot', 'category', 'class', 'equipmentCategory', 'binding', 
                  'durability', 'sturdiness', 'quality', 'valueTableId', 'armourType', 'dps', 'minDamage', 'maxDamage',
                  'damageType', 'weaponType', 'description', 'unique', 'minLevel', 'stackMax', 'grants', 'requiredClass', 
                  'requiredRace', 'maxLevel', 'requiredFaction', 'reputation', 'itemLevelOffset', 'mainLegacyId', 
                  'mainLegacyBaseRank', 'property', 'itemXP', 'virtueXP', 'slots', 'maxItems', 'itemStackMax',]

def process_attrib(big_dict, xml_thing, name):
    attrib = xml_thing.attrib.get(name)
    if attrib is None:
        attrib = None
    if name in ATTRIB_NAME_MAP:
        name = ATTRIB_NAME_MAP[name]
    if name in big_dict:
        big_dict[name].append(attrib)
    else:
        big_dict[name] = [attrib,]
def process_stat(stats_dict, stat_xml):
    #Get the stat name and vals
    statName = stat_xml.attrib.get('name')
    if statName not in STAT_NAME_MAP:
        return
    
    statScaling = stat_xml.attrib.get('scaling')
    rangedScaling = stat_xml.attrib.get('ranged')
    if rangedScaling is not None:
        statScaling = rangedScaling.split(":")[1] #Ignore the range... This might break things eventually but probably okay for now
    if statScaling is None:
        statScaling = 0
    if "," in str(statScaling):
        statScaling = statScaling.split(",")[0]
    
    saveName = STAT_NAME_MAP[statName]
    stats_dict[saveName] = statScaling
    
def parse_items_xml(fp = items_xml_fp):
    #Parse with ETree, then convert to polars dataframe
    #Read file, get root
    prstree = ETree.parse(fp)
    root = prstree.getroot()
    
    items_dict = {}
    #Iterate thru the highest level xml tree
    for itemNo in root.iter('item'):
        for name in ATTRIB_NAMES:
            process_attrib(items_dict, itemNo, name)

        #Instantiate all stats as 0
        stats_dict = {}
        for name in STAT_NAME_MAP:
            stats_dict[STAT_NAME_MAP[name]] = 0
        #Iterate over stats subtree
        for stat in itemNo.iter('stat'):
            process_stat(stats_dict, stat)

        for k,v in stats_dict.items():
            if k in items_dict:
                items_dict[k].append(int(v))
            else:
                items_dict[k] = [int(v),]

    #convert items lists to polars dataframe with correct dtypes
    column_dtypes = {'itemId':pl.Int64, 
                    'itemName':pl.Utf8, 
                    'iconId':pl.Utf8, 
                    'iLvl':pl.UInt64, 
                    'slot':pl.Utf8, 
                    'category':pl.Utf8, 
                    'classId':pl.Utf8, 
                    'equipmentCategory':pl.Utf8, 
                    'binding':pl.Utf8, 
                    'durability':pl.Utf8, 
                    'sturdiness':pl.Utf8, 
                    'quality':pl.Utf8, 
                    'valueTableId':pl.Utf8, 
                    'armourType':pl.Utf8, 
                    'dps':pl.Utf8, 
                    'minDamage':pl.Utf8, 
                    'maxDamage':pl.Utf8,
                    'damageType':pl.Utf8, 
                    'weaponType':pl.Utf8, 
                    'description':pl.Utf8, 
                    'unique':pl.Utf8, 
                    'minLevel':pl.Utf8, 
                    'stackMax':pl.Utf8, 
                    'grants':pl.Utf8, 
                    'requiredClass':pl.Utf8, 
                    'requiredRace':pl.Utf8, 
                    'maxLevel':pl.Utf8, 
                    'requiredFaction':pl.Utf8, 
                    'reputation':pl.Utf8, 
                    'itemLevelOffset':pl.UInt8, 
                    'mainLegacyId':pl.Utf8, 
                    'mainLegacyBaseRank':pl.Utf8, 
                    'itemProperty':pl.Utf8, 
                    'itemXP':pl.Utf8, 
                    'virtueXP':pl.Utf8, 
                    'essenceSlots':str, 
                    'maxItems':pl.Utf8, 
                    'itemStackMax':pl.Utf8,
                    'Vitality Scaling':pl.Int64, 
                    'Will Scaling':pl.Int64, 
                    'Agility Scaling':pl.Int64, 
                    'Might Scaling':pl.Int64, 
                    'Fate Scaling':pl.Int64, 
                    'Maximum Morale Scaling':pl.Int64, 
                    'Maximum Power Scaling':pl.Int64,
                    'Finesse Scaling':pl.Int64, 
                    'Critical Rating Scaling':pl.Int64, 
                    'Outgoing Healing Rating Scaling':pl.Int64,  
                    'Incoming Healing Rating Scaling':pl.Int64, 
                    'Tactical Mastery Scaling':pl.Int64, 
                    'Physical Mastery Scaling':pl.Int64, 
                    'Tactical Mitigation Scaling':pl.Int64, 
                    'Physical Mitigation Scaling':pl.Int64, 
                    'Block Rating Scaling':pl.Int64, 
                    'Parry Rating Scaling':pl.Int64, 
                    'Evade Rating Scaling':pl.Int64, 
                    'Critical Defense Scaling':pl.Int64, 
                    'Resistance Rating Scaling':pl.Int64, 
                    'Armour Scaling':pl.Int64,
                    'Out of Combat Power Regen Scaling': pl.Int64,
                    'In Combat Power Regen Scaling': pl.Int64,
                    'In Combat Morale Regen Scaling': pl.Int64,
                    'Out of Combat Morale Regen Scaling': pl.Int64,
                   }

    df = pl.DataFrame(items_dict, schema = column_dtypes)
    
    return df

def clean_items_df(df):
    df = (df.lazy().filter(pl.col("category").is_in(['ARMOUR', 'WEAPON', 'ITEM']))
          .filter(pl.col("slot").is_not_null())
          .filter(~pl.col("slot").is_in(['TOOL', 'MAIN_HAND_AURA', 'BRIDLE']))
          .filter(pl.col("iLvl") > 1)
          .with_columns(pl.col("itemName").map_elements(lambda x: normalize('NFKD',x).encode('ascii', errors='ignore').decode('utf-8')))
          .unique(subset=["itemName",], keep='first',maintain_order=False)
          .sort("itemName")
         ).collect()
    return df

#Example call: Python item_parsing.py -f u35_items.xml -s u35_items.csv
def main(args):
    #Make sure xml file path exists
    if not os.path.isfile(args.items_fp):
        print(f"File '{args.items_fp}' does not exist.")
        return -1
    
    df = parse_items_xml(fp=args.items_fp)
    df = clean_items_df(df)
    df.write_csv(args.save_fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse the items database .xml file and save as csv")
    parser.add_argument('--items_fp', '-f', type=str, help="File path to xml of items db (download from LotroCompanion)",required=True)
    parser.add_argument('--save_fp', '-s', type=str, help="Save path/name for csv (include .csv extension)", required=True)
    args = parser.parse_args()
    main(args)  