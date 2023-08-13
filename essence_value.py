import pandas as pd
import numpy as np
from utils import mainstat_to_ratings, parse_use_stats_yaml
import argparse
from stat_curve_parsing import parse_curves
from item_parsing import parse_items_xml, clean_items_df
import os
from query_item import query_item, stats_to_ratings

#Hard coded bc I cbf to make a look-up for it and it's not that much to do manually
#TODO: Actually pull from itemDB and make this scale (assuming they all share the same scaling)
lively = {
    'ilvl': 474,
    'Vitality': 2338,
    'Incoming Healing Rating': 54527,
    'Outgoing Healing Rating': 73863,
    'Critical Rating': 31386,
    'Physical Mastery': 29943,
    'Tactical Mastery': 29943,
    'Finesse': 46753,
    'Physical Mitigation': 42292,
    'Tactical Mitigation': 39649,
    'Resistance Rating': 54441,
    'Block Rating': 54441,
    'Parry Rating': 54441,
    'Evade Rating': 54441,
    'Critical Defense': 49610
}
vivid = {
    'ilvl': 481,
    'Vitality': 2563,
    'Incoming Healing Rating': 59755,
    'Outgoing Healing Rating': 79278,
    'Critical Rating': 33686,
    'Physical Mastery': 32143,
    'Tactical Mastery': 32143,
    'Finesse': 52310,
    'Physical Mitigation': 44506,
    'Tactical Mitigation': 43163,
    'Resistance Rating': 61569,
    'Block Rating': 61569,
    'Parry Rating': 61569,
    'Evade Rating': 61569,
    'Critical Defense': 54367
}
delvers = {
    'ilvl': 467,
    'Vitality': 2114,
    'Incoming Healing Rating': 49298,
    'Outgoing Healing Rating': 68449,
    'Critical Rating': 29086,
    'Physical Mastery': 27743,
    'Tactical Mastery': 27743,
    'Finesse': 41196,
    'Physical Mitigation': 40078,
    'Tactical Mitigation': 36135,
    'Resistance Rating': 47312,
    'Block Rating': 47312,
    'Parry Rating': 47312,
    'Evade Rating': 47312,
    'Critical Defense': 44853
}
ruthless = {
    'ilvl': 465,
    'Vitality': 2114, #Use delvers value since no moors vit essence & delvers close in ilvl (TODO: actually scale this...)
    'Incoming Healing Rating': 47804,
    'Outgoing Healing Rating': 66902,
    'Critical Rating': 28429,
    'Physical Mastery': 27114,
    'Tactical Mastery': 27114,
    'Finesse': 39608,
    'Physical Mitigation': 39445,
    'Tactical Mitigation': 39445,
    'Resistance Rating': 45276,
    'Block Rating': 45276,
    'Parry Rating': 45276,
    'Evade Rating': 45276,
    'Critical Defense': 43494
}
ESSENCES = {"Vivid Delver's Essences": vivid,
            "Lively Delver's Essences": lively,
            "Delver's Essences": delvers,
            "Ruthless Essences": ruthless
           }
            


#Whether or not to use specific stats in EV calculations. Eventually, move this to .yml or argparser
use_stat = {
    'Maximum Morale': True,
    'Incoming Healing Rating': True,
    'Outgoing Healing Rating': True,
    'Critical Rating': True,
    'Physical Mastery': True,
    'Tactical Mastery': True,
    'Finesse': True,
    'Physical Mitigation': True,
    'Tactical Mitigation': True,
    'Resistance Rating': True,
    'Block Rating': True,
    'Parry Rating': True,
    'Evade Rating': True,
    'Critical Defense': True
}

#Calculate essence value based on the ratings dictionary, which stats to use, and values on essences 
def get_essence_value(item_ratings_dict, char_class, use_stat=use_stat, essences=vivid):
    stats_to_use = [k for k,v in use_stat.items() if v] #Only use stats if they're toggled on
    ev = 0 #Initialize at 0 essence value (EV)
    
    #Add EV for each stat into total
    for stat in stats_to_use:
        if stat != 'Maximum Morale':
            value = item_ratings_dict[stat] / essences[stat]
            ev += value
    
    #Deal with Maximum Morale
    if "Maximum Morale" in stats_to_use:
        if item_ratings_dict['Maximum Morale'] != 0:
            #Reverse engineer an EV for maximum morale from vitality
            #Get stats from 1 essence of vit
            included_stats, vals = mainstat_to_ratings(char_class, 'Vitality', essences['Vitality'])

            #Calculate EV of non-morale stats
            non_morale_ev = 0.
            #Vit includes Max Morale, TMit, Block, Resist, NCMR -- Ignore NCMR for EV calculations
            vit_stats = ['Tactical Mitigation', 'Block Rating', 'Resistance Rating']
            use_vit_stats = [stat for stat in vit_stats if use_stat[stat]] #Only compute if we care about the non-morale values
            if len(use_vit_stats) > 0:
                for stat in use_vit_stats:
                    stat_ev = vals[included_stats.index(stat)] / essences[stat]
                    non_morale_ev += stat_ev

            #The EV from the total morale is complementary to the EV from the non-morale stats
            total_morale_ev = 1-non_morale_ev 
            #EV per single morale = total morale EV / morale from 1 vit essence
            ev_per_morale = total_morale_ev / vals[included_stats.index('Maximum Morale')]

            #Now calculate the EV of the maximum morale stat on the item with ev_per_morale
            ev += item_ratings_dict['Maximum Morale'] * ev_per_morale
    
    #Add in essence slots as 1:1
    #TODO: Add in moors essence slots devaluation?
    ev += item_ratings_dict['Essence Slots']
    
    return ev

#Example python call: C:\Users\brand\Desktop\Lotro Items Python Sandbox>Python essence_value.py --name "Hiddenhoard Steel Stud" --ilvl 475 -c Brawler --items_fp "/Users/brand/Downloads/lotro_items_u34_3.xml"
def main(args):
    #Make sure supplied file paths all exist
    if not os.path.isfile(args.use_stats_fp):
        print(f"File '{args.use_stats_fp}' does not exist.")
        return -1
    if not os.path.isfile(args.items_fp):
        print(f"File '{args.items_fp}' does not exist.")
        return -1
    if not os.path.isfile(args.stat_curves_fp):
        print(f"File '{args.stat_curves_fp}' does not exist.")
        return -1
    
    #Make sure supplied class is valid
    allowed_classes = ['Brawler', 'Beorning', 'Burglar', 'Captain', 'Champion', 'Guardian', 'Hunter', 'Lore-master', 'Ministrel', 'Rune-keeper', 'Warden']
    if not args.pclass in allowed_classes:
        print(f"Class '{args.pclass}' not valid. Valid classes are: {allowed_classes}")
        return -1
    #Maybe make sure supplied ilvl is 1->549?
    
    
    #Get DF of items
    items_df = parse_items_xml(fp=args.items_fp)
    items_df = clean_items_df(items_df)

    #Get DF of stat curves
    stat_curves_df = parse_curves(fp=args.stat_curves_fp)
    
    #Get the list of stats to use in EV calculations
    use_stats = parse_use_stats_yaml(args.use_stats_fp)
    
    try: 
        item_stats_dict = query_item(items_df, stat_curves_df, args.name, args.ilvl)
    except NameError:
        print(f"Could not find item with name '{args.name}'")
        return -1
    
    item_ratings_dict = stats_to_ratings(item_stats_dict, args.pclass)
    
    ev = get_essence_value(item_ratings_dict, args.pclass)
    
    print(f"Item          : {args.name}")
    print(f"Item level    : {args.ilvl}")
    print(f"Class         : {args.pclass}")
    print(f"Essence Value : {ev}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inputs for calculating an item essence value")
    parser.add_argument('--name', '-n', type=str, help='Item name', required=True)
    parser.add_argument('--ilvl', '-i', type=int, help='Item level', required=True)
    parser.add_argument('--pclass', '-c', type=str, help='Player class', required=True)
    parser.add_argument('--use_stats_fp', '-u', type=str, help="File path to use_stats.yml (default: 'use_stats.yml')", required=False, default='use_stats.yml')
    parser.add_argument('--items_fp', type=str, help="File path to xml of items db (from LC) (default: 'lotro_items_u34_3.xml')",
                        required=False, default='lotro_items_u34_3.xml')
    parser.add_argument('--stat_curves_fp', type=str, help="File path to xml of stat curves db (from LC) (default: 'stat_progressions.xml')",
                        required=False, default='stat_progressions.xml')
    args = parser.parse_args()
    main(args)