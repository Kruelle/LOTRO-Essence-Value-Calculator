import numpy as np
import polars as pl
import os
import yaml
from functools import reduce
import operator

main_stats = ['Critical Rating', 
               'Finesse', 
               'Physical Mastery',
               'Tactical Mastery',
               'Outgoing Healing Rating',
               'Resistance Rating',
               'Block Rating',
               'Parry Rating',
               'Evade Rating',
               'Physical Mitigation',
               'Tactical Mitigation',
              ]
vitality_stats = ['Maximum Morale', 
                  'In Combat Morale Regen', 
                  'Out of Combat Morale Regen',
                 ]
vit_vals = [4.5,0.012,0.12]
fate_stats = ['Maximum Power',
              'In Combat Power Regen',
              'Out of Combat Power Regen',
             ]
fate_vals = [1, 0, 0.07]

stats_data = {
    'Stat': ['Might','Agility','Vitality','Will','Fate'],
    'Included Stats': [main_stats, main_stats, vitality_stats, main_stats, fate_stats],
    'Beorning': [[1,0,3,0,3,0,0,1,2,1,1,],[2,1,2,0,2,0,0,0,1,0,0,],vit_vals,[0,1,1,0,1,1,0,0,0,1.5,1.5,],[0,0,0]],
    'Brawler': [[1,0,3,0,3,0,0,1,1,1,1,],[2,1,2,0,2,0,0,0,2,0,0,],vit_vals,[0,1,1,0,1,1,0,0,0,1.5,1.5,],fate_vals],
    'Burglar': [[1.5,1.5,2,0,2,0,0,0,1,0,0,],[1,0,3,0,3,0,0,1,2,1,1,],vit_vals,[0.5,1.5,2,0,2,1,0,0,0,1,0],fate_vals],
    'Captain': [[1,0,3,3,0,0,2,1,0,1,1,],[2,1,2,2,0,0,0,1,0,0,0,],vit_vals,[0,1,1,1,0,1,0,0,0,1.5,1.5,],fate_vals],
    'Champion': [[1,0,3,0,3,0,0,3,0,1,1,],[2,1,2,0,2,0,0,1,0,0,0,],vit_vals,[0,1,1,0,1,1,0,0,0,1.5,1.5,],fate_vals],
    'Guardian': [[1,0,3,0,3,0,1,2,0,1,1,],[2,1,2,0,2,0,0,1,0,0,0,],vit_vals,[0,1,1,0,1,1,0,0,0,1.5,1.5,],fate_vals],
    'Hunter': [[1.5,1.5,2,0,2,0,0,0,1,0,0,],[1,0,3,0,3,0,0,1,2,1,1,],vit_vals,[0.5,1.5,2,0,2,1,0,0,0,1,0,],fate_vals],
    'Lore-master': [[1.5,1.5,0,2,0,0,0,1,0,0,0,],[2,1,0,2,0,0,0,0,1,0,0,],vit_vals,[1,0,0,3,0,1,0,0,2,1,1,],fate_vals],
    'Mariner': [[1.5,1.5,2,0,2,0,0,1,0,0,0,],[1,0,3,0,3,0,0,3,0,1,1,],vit_vals,[0.5,1.5,2,0,2,1,0,0,0,1,0,],fate_vals],
    'Minstrel': [[1,0,0,2,2,0,0,0,0,0,1,],[2,1,0,2,0,0,0,0,1,0,0,],vit_vals,[1,0,0,3,0,1,1,0,1,1,1,],fate_vals],
    'Rune-keeper': [[1,0,0,2,2,0,0,0,0,0,1,],[2,1,0,2,0,0,0,0,1,0,0,],vit_vals,[1,0,0,3,0,1,0,0,2,1,1,],fate_vals],
    'Warden': [[1.5,1.5,2,0,2,0,1,0,0,0,0,],[1,0,3,0,3,0,2,1,0,1,1,],vit_vals,[0,1,1,0,1,1,0,0,0,1.5,1.5,],fate_vals],
}
for k,v in stats_data.items():
    if k not in ['Stat','Included Stats']:
        for i, stat_list in enumerate(stats_data[k]):
            assert(len(stat_list) == len(stats_data['Included Stats'][i]))
        

stats_df = pl.DataFrame(stats_data)

mainstats = ["Vitality", "Might", "Agility", "Will", "Fate"]

def mainstat_to_ratings(char_class, mainstat, val):
    included_stats = list(stats_df.filter(pl.col('Stat')==mainstat).select('Included Stats').item())
    stats = stats_df.filter(pl.col('Stat')==mainstat).select(char_class).item()
    stats = stats.to_numpy() * val
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