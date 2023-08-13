import numpy as np
import pandas as pd
import os
import yaml
from functools import reduce
import operator

might_stats = ['Physical Mastery', 'Tactical Mastery', 'Critical Rating', 'Block Rating', 
               'Parry Rating', 'Evade Rating', 'Physical Mitigation', 'Finesse']
agility_stats = ['Physical Mastery', 'Critical Rating', 'Parry Rating', 'Evade Rating']
vitality_stats = ['Maximum Morale', 'Tactical Mitigation', 'Block Rating', 'Resistance Rating', 'Non-Combat Morale Regen']
will_stats = ['Tactical Mastery', 'Finesse', 'Tactical Mitigation', 'Resistance Rating', 'Evade Rating']
fate_stats = ['Critical Rating', 'Finesse', 'Tactical Mitigation', 'Resistance Rating',
              'In-Combat Morale Regen', 'In-Combat Power Regen', 'Non-Combat Power Regen']

stats_data = {
    'Stat': ['Might','Agility','Vitality','Will','Fate'],
    'Included Stats': [might_stats, agility_stats, vitality_stats, will_stats, fate_stats],
    'Beorning': [[2.5,2.5,1,2,3,1,0,0],[2,1,0,2],[4.8,0,0,1,7.2],[2,0,1,1,1],[2.5,0.5,2,1,3,0,0]],
    'Brawler': [[3,0,0,0,2,3,0,1],[0,0,2,3],[5,0,0,1,7.2],[1,0,2,1,0],[2.5,1,1,1,1.5,3.56,24]],
    'Burglar': [[0,0,0,3,2,0,0,0],[3,1,2,3],[4.5,0,0,1,7.2],[1,0,1,2,1],[2.5,1,1,1,1.5,1.71,24]],
    'Captain': [[2.5,2.5,0,3,2,0,0,0],[0,1,2,3],[4.5,0,0,2,7.2],[0,0,1,2,0],[2.5,1,1,0,1.5,1.71,24]],
    'Champion': [[3,0,1,3,2,2,1,0],[0,1,2,3],[4.5,0,1,1,7.2],[1,0,1,2,0],[2.5,1,1,1,1.5,1.71,24]],
    'Guardian': [[3,0,0,3,2,0,0,0],[0,1,2,3],[4.8,0,0,1,7.2],[1,0,1,2,0],[2.5,1,1,1,1.5,1.71,24]],
    'Hunter': [[0,0,0,3,2,0,0,0],[3,1,2,3],[4,1,0,1,7.2],[1,0,1,2,0],[2.5,1,1,1,1.5,1.71,22]],
    'Lore-master': [[0,0,0,3,2,0,0,0],[0,1,2,3],[4,1,0,1,7.2],[3,1,1,2,1],[2.5,0,1,1,1.5,1.71,24]],
    'Minstrel': [[0,0,0,3,2,0,0,0],[0,1,2,3],[4,1,0,1,7.2],[3,1,1,2,1],[2.5,0,1,1,1.5,1.71,24]],
    'Rune-keeper': [[0,0,0,3,2,0,0,0],[0,1,2,3],[4,1,0,1,7.2],[3,1,1,2,1],[2.5,0,1,1,1.5,1.71,24]],
    'Warden': [[2,0,0,3,2,0,0,0],[3,1,2,3],[4.8,0,0,1,7.2],[0,0,1,2,0],[2.5,1,1,1,1.5,1.71,24]],
}

stats_df = pd.DataFrame(stats_data)

mainstats = ["Vitality", "Might", "Agility", "Will", "Fate"]

def mainstat_to_ratings(char_class, mainstat, val):
    included_stats = stats_df[stats_df['Stat']==mainstat]['Included Stats'].iloc[0]
    stats = stats_df[stats_df['Stat']==mainstat][char_class].iloc[0]
    stats = np.array(stats) * val
    return included_stats, stats

def parse_char_yaml(fp='/Users/brand/Desktop/Lotro Items Python Sandbox/char.yml'):
    with open(fp, 'r') as file:
        char_configs = yaml.safe_load(file)
    
    #List of dicts -> dict using reduce operator
    char_stats = reduce(operator.ior, char_configs['char_stats'], {})
    char_class = char_configs['char_class']
    use_stats = reduce(operator.ior, char_configs['use_stats'], {})
    virtues = char_configs['virtues']
    enforce_4set = char_configs['enforce_4set']
    enforce_3set = char_configs['enforce_3set']

    items_dict = {
        'helmet':None,
        'shoulders': None,
        'cloak': None,
        'chest': None,
        'gloves': None,
        'pants': None,
        'boots': None,
        'class_item': None,
        'offhand': None,
        'bow': None,
        'earring': None,
        'necklace': None,
        'bracelet': None,
        'ring': None
    }

    for slot in items_dict:
        if char_configs[slot][0] != 'None':
            items_dict[slot] = reduce(operator.ior, char_configs[slot], {})

    rating_caps = {
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
    }

    for stat in rating_caps:
        rating_caps[stat] = reduce(operator.ior, char_configs[stat], {})
        
    everything_dict = {
        'char_stats': char_stats,
        'char_class': char_class,
        'use_stats': use_stats,
        'virtues': virtues,
        'enforce_4set': enforce_4set,
        'enforce_3set': enforce_3set,
        'items_dict': items_dict,
        'rating_caps': rating_caps
    }
    
    return everything_dict

def parse_use_stats_yaml(fp='/Users/brand/Desktop/Lotro Items Python Sandbox/use_stats.yml'):
    #Read yaml file
    with open(fp, 'r') as file:
        char_configs = yaml.safe_load(file)
    
    #Condense the list of dictionaries into single dictionary
    use_stats = reduce(operator.ior, char_configs['use_stats'], {})
    
    return use_stats

def get_gear_combinations(items_dict):
    items_list_slots_base = ['helmet', 'shoulders', 'cloak', 'chest', 'gloves', 'pants', 'boots',
                             'class_item', 'offhand', 'bow', 
                             'earring', 'earring', 'necklace', 'bracelet', 'bracelet', 'ring', 'ring'] #Slots order of items in list
    item_list_slots = [slot for slot in items_list_slots_base if items_dict[slot] is not None] #Remove slots with no specified gear
    #Put items into correct order for getting 
    item_list = [[k for k,v in items_dict[slot].items()] for slot in item_list_slots] #combinations

    combinations = list(itertools.product(*item_list)) #Full list of gear combinations
    return combinations, item_list_slots