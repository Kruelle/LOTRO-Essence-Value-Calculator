import numpy as np
import polars as pl
import os
from utils import stats_df, mainstats, mainstat_to_ratings
from stat_curve_parsing import parse_curves
from item_parsing import parse_items_xml, clean_items_df
import math
import argparse

#List of available stats for looping purposes (excluding ICMR, etc because I don't care about those specific stats)
stats_list = ['Armour','Vitality','Might','Agility','Will','Fate','Finesse','Critical Rating',
              'Outgoing Healing Rating','Incoming Healing Rating','Tactical Mastery','Physical Mastery',
              'Tactical Mitigation','Physical Mitigation','Evade Rating','Parry Rating','Block Rating',
              'Critical Defense','Resistance Rating','Maximum Morale', 'Maximum Power',
              'In Combat Power Regen',]

#Initialize a dict of all the possible stats
def empty_stats_dict():
    empty_dict = {
        'Armour': 0,
        'Vitality': 0,
        'Might': 0,
        'Agility': 0,
        'Will': 0,
        'Fate': 0,
        'Finesse': 0,
        'Critical Rating': 0,
        'Outgoing Healing Rating': 0,
        'Incoming Healing Rating': 0,
        'Tactical Mastery': 0,
        'Physical Mastery': 0,
        'Tactical Mitigation': 0,
        'Physical Mitigation': 0,
        'Evade Rating': 0,
        'Parry Rating': 0,
        'Block Rating': 0,
        'Critical Defense': 0,
        'Resistance Rating': 0,
        'Maximum Morale': 0,
        'Maximum Power': 0,
        'In Combat Morale Regen': 0,
        'In Combat Power Regen': 0,
        'Out of Combat Morale Regen': 0,
        'Out of Combat Power Regen': 0,
        'Essence Slots': 0
    }
    return empty_dict

#Initialize a dict of all rating values (i.e. like a stats dict but without main stats or armour)
def empty_ratings_dict():
    empty_dict = {
        'Finesse': 0,
        'Critical Rating': 0,
        'Outgoing Healing Rating': 0,
        'Incoming Healing Rating': 0,
        'Tactical Mastery': 0,
        'Physical Mastery': 0,
        'Tactical Mitigation': 0,
        'Physical Mitigation': 0,
        'Evade Rating': 0,
        'Parry Rating': 0,
        'Block Rating': 0,
        'Critical Defense': 0,
        'Resistance Rating': 0,
        'Maximum Morale': 0,
        'Maximum Power': 0,
        'In Combat Morale Regen': 0,
        'In Combat Power Regen': 0,
        'Out of Combat Morale Regen': 0,
        'Out of Combat Power Regen': 0,
        'Essence Slots': 0
    }
    return empty_dict

#Get the rating value from the stat curve + ilvl, using the stat curve dataframe
def scaling_to_rating(stat_curves_df, curve_id, ilvl):
    val = stat_curves_df.lazy().filter(pl.col('iLvl')==ilvl).select(curve_id).collect().item()
    return val

#Get a specific stat value from an item's entry in the item dataframe, at a specific ilvl
#TODO: add "inplace=False" option to let this also return the stat_val instead of update the stat_dict directly
def stat_query(item, stat, ilvl, stat_curves_df, stat_dict):
    stat_col = stat+" Scaling" #column name for stat curve ID is "Stat Scaling"
    scaling_id = int(item.select(stat_col).item()) #Query item entry to get stat curve ID for specified stat
    #print(stat_col + ": " + str(scaling_id))
    
    if scaling_id != 0: #If scaling id == 0, the stat is 0 (i.e. no change to stats dict)
        #Get the stat value from the scaling id + ilvl
        stat_val = scaling_to_rating(stat_curves_df, str(scaling_id), ilvl)
        #Round the value
        if stat in mainstats:
            stat_val = math.floor(stat_val) #Main stats always rounded down
        #else: #Shouldn't round rating values until display
        #    stat_val = round(float(stat_val))
            
        #Update the dictionary entry for that stat
        stat_dict[stat] = stat_val
        
#Get the stats associated with an item and ilvl
def query_item(items_df, stat_curves_df, item_name, ilvl):
    stats_dict = empty_stats_dict() #Initialize all stats at 0
    
    item = items_df.filter(pl.col('itemName')==item_name)
    if len(item) == 0: #return exception if no item found
        raise NameError
    
    #Loop over possible stats, and update dictionary with new stat values (function implicitly inplace=True)
    for stat in stats_list:
        stat_query(item, stat, ilvl, stat_curves_df, stats_dict)
    #TODO: Change this to a DF JOIN
    
    #Get essence slots from item query
    num_slots = item.select('essenceSlots').item()
    if num_slots is not None:
        try:
            stats_dict['Essence Slots'] = int(num_slots)
        except:
            stats_dict['Essence Slots'] = len(num_slots) #TODO: More complex breakdown of Basic/Primary/Vitals EVs
            #print(num_slots)
            #continue #Don't care if essenceSlots='WW' or similar
        
    return stats_dict
        
#Convert all mainstats + armour into ratings and return as new dict
def stats_to_ratings(stats_dict, char_class):
    ratings_dict = empty_ratings_dict()
    
    #Initialize with rating values from stats_dict
    for key in ratings_dict:
        ratings_dict[key] += stats_dict[key]
        
    #Convert TMastery -> OGH
    ratings_dict['Outgoing Healing Rating'] += stats_dict['Tactical Mastery']
        
    #Convert armour values 1x->pmit, 0.2x->tmit
    ratings_dict['Physical Mitigation'] += stats_dict['Armour']*1.0
    ratings_dict['Tactical Mitigation'] += stats_dict['Armour']*0.2
    
    #Convert mainstats to ratings
    for mainstat in mainstats: #Loop over main stats
        #Get converted rating values from mainstat
        stats_to_add, vals_to_add = mainstat_to_ratings(char_class, mainstat, stats_dict[mainstat])
        
        #Add converted ratings to ratings dict
        for stat, val in zip(stats_to_add, vals_to_add):
            ratings_dict[stat] += val
    
    return ratings_dict
        
#Example python call: 
#Python query_item.py --name "Hiddenhoard Steel Stud" --ilvl 475 --items_fp "/Users/brand/Downloads/lotro_items_u34_3.xml"
#Can optionally add -r -c <class> to return derived rating values instead of baseline values
def main(args):
    #Make sure supplied file paths all exist
    if not os.path.isfile(args.items_fp):
        print(f"File '{args.items_fp}' does not exist.")
        return -1
    if not os.path.isfile(args.stat_curves_fp):
        print(f"File '{args.stat_curves_fp}' does not exist.")
        return -1
    
    if args.return_ratings:
        #Make sure supplied class is valid
        if args.pclass is None:
            print("Please supply a class (using --pclass or -c) to generate rating values")
            return -1
        allowed_classes = ['Brawler', 'Beorning', 'Burglar', 'Captain', 'Champion', 'Guardian', 'Hunter', 'Lore-master', 'Mariner', 'Ministrel', 'Rune-keeper', 'Warden']
        if not args.pclass in allowed_classes:
            print(f"Class '{args.pclass}' not valid. Valid classes are: {allowed_classes}")
            return -1
    #Maybe make sure supplied ilvl is 1->549?
    
    
    #Get DF of items
    items_df = parse_items_xml(fp=args.items_fp)
    items_df = clean_items_df(items_df)

    #Get DF of stat curves
    stat_curves_df = parse_curves(fp=args.stat_curves_fp)
    
    try: 
        item_stats_dict = query_item(items_df, stat_curves_df, args.name, args.ilvl)
    except NameError:
        print(f"Could not find item with name '{args.name}'")
        return -1
    if args.return_ratings:
        item_ratings_dict = stats_to_ratings(item_stats_dict, args.pclass)
        for k, v  in item_ratings_dict.items():
            if v != 0: print(f"{k:<22} : {round(v)}") 
    else:
        for k, v in item_stats_dict.items():
            if v != 0: print(f"{k:<22} : {round(v)}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Return an item's stats at a specific ilvl")
    parser.add_argument('--name', '-n', type=str, help='Item name', required=True)
    parser.add_argument('--ilvl', '-i', type=int, help='Item level', required=True)
    parser.add_argument('--items_fp', type=str, help="File path to xml of items db (from LC) (default: 'data/items.xml')",
                        required=False, default='C:/Users/Brandon/Downloads/items.xml')
    parser.add_argument('--stat_curves_fp', type=str, help="File path to xml of stat curves db (from LC) (default: 'data/progressions.xml')",
                        required=False, default='C:/Users/Brandon/Downloads/progressions.xml')
    parser.add_argument('--return_ratings', '-r', help="Use to return the calculated ratings instead of item stats", required=False,
                            action='store_true')
    parser.add_argument('--pclass', '-c', type=str, help='Player class', required=False)
    args = parser.parse_args()
    main(args)  