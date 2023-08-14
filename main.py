import pandas as pd
import tkinter as tk
import customtkinter as ctk
from PIL import Image
import requests
import os
import ctypes
from utils import mainstat_to_ratings, parse_use_stats_yaml
from stat_curve_parsing import parse_curves
from item_parsing import parse_items_xml, clean_items_df
from query_item import query_item, stats_to_ratings
from essence_value import get_essence_value, ESSENCES

classes = ['Brawler', 'Beorning', 'Burglar', 'Captain', 'Champion', 'Guardian', 'Hunter', 'Lore-master', 'Minstrel', 'Rune-keeper', 'Warden']
stats_list = ['Armour','Vitality','Might','Agility','Will','Fate','Finesse','Critical Rating',
              'Outgoing Healing Rating','Incoming Healing Rating','Tactical Mastery','Physical Mastery',
              'Tactical Mitigation','Physical Mitigation','Evade Rating','Parry Rating','Block Rating',
              'Critical Defense','Resistance Rating','Maximum Morale']
ratings_list = ['Maximum Morale','Finesse','Critical Rating',
                'Outgoing Healing Rating','Incoming Healing Rating','Tactical Mastery','Physical Mastery',
                'Tactical Mitigation','Physical Mitigation','Evade Rating','Parry Rating','Block Rating',
                'Critical Defense','Resistance Rating']
essences = ["Vivid Delver's Essences", "Lively Delver's Essences", "Delver's Essences", "Ruthless Essences",]

class App(ctk.CTk):
    def __init__(self, items_df, stat_curves_df, use_stats):
        super().__init__()
        self.geometry("1200x965")
        self.title("LOTRO Essence Value Calculator")
        self.iconbitmap('images/ev_icon.ico')
        self.items_df = items_df
        self.stat_curves_df = stat_curves_df
        
        self.grid_columnconfigure(1, weight=1)
        self.sidebar = SidebarFrame(self, use_stats)
        self.sidebar.grid(row=0,column=0,padx=10, pady=(10,0), sticky="nw")
        
        self.item_frames = MultiItemFrame(self, orientation="horizontal", fg_color="transparent", height=930)
        self.item_frames.grid(row=0,column=1,padx=0,pady=(0,0), sticky="nsew")
        
        
    def toggle_stats(self):
        self.item_frames.toggle_stats(self.sidebar.stats_var)
        
    def toggle_ratings(self):
        self.item_frames.toggle_ratings(self.sidebar.ratings_var)
        
    def get_params(self):
        return self.sidebar.get_params()
    
    def get_dfs(self):
        return self.items_df, self.stat_curves_df
    
    def updated_class(self):
        self.item_frames.updated_class()
    def updated_stats_or_essences(self):
        self.item_frames.updated_stats_or_essences()
                                             
class MultiItemFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master_app = master #for some reason, doesn't seem to be saving it properly?
        
        self.item_frames = []
        item1 = ItemFrame(self)
        item1.grid(row=0,column=0,padx=10,pady=(10,0), sticky="n")
        self.item_frames.append(item1)
        
        self.new_item_button = ctk.CTkButton(self, text="+", width=40, height=40, command=self.add_new_item)
        self.new_item_button.grid(row=0, column=1, padx=10, pady=(10,0), sticky="nw")
        
        
    def toggle_stats(self, stats_var):
        for item in self.item_frames:
            item.update_show_stats(stats_var)
        
    def toggle_ratings(self, ratings_var):
        for item in self.item_frames:
            item.update_show_ratings(ratings_var)
    
    def add_new_item(self):
        self.new_item_button.destroy() #remove the new item button to put the new item in it's place
        
        #Add new item column
        new_item = ItemFrame(self)
        new_item.grid(row=0,column=len(self.item_frames),padx=10,pady=(10,0),sticky="n")
        self.item_frames.append(new_item)
        
        #Make new button
        self.new_item_button = ctk.CTkButton(self, text="+", width=40, height=40, command=self.add_new_item)
        self.new_item_button.grid(row=0, column=len(self.item_frames), padx=10, pady=(10,0), sticky="nw")
        
    
    def item_removed(self):
        self.new_item_button.destroy()
        for i, frame in enumerate(self.item_frames):
            if frame.exists == False:
                frame.destroy()
                self.item_frames.pop(i)
        for i, frame in enumerate(self.item_frames):
            frame.grid(row=0,column=i,padx=10,pady=(10,0), sticky="n")
        self.new_item_button = ctk.CTkButton(self, text="+", width=40, height=40, command=self.add_new_item)
        self.new_item_button.grid(row=0, column=len(self.item_frames),padx=10,pady=(10,0),sticky="nw")
        
    def get_params(self):
        return self.master_app.get_params()
    def get_dfs(self):
        return self.master_app.get_dfs()
    
    def updated_class(self):
        for frame in self.item_frames:
            frame.updated_class()
    def updated_stats_or_essences(self):
        for frame in self.item_frames:
            frame.updated_stats_or_essences()
        

class ItemFrame(ctk.CTkFrame):
    def __init__(self, master, show_stats=True, show_ratings=True):
        super().__init__(master)
        self.show_stats = show_stats
        self.show_ratings = show_ratings
        self.ratings_dict = None
        self.stats_dict = None
        self.item_exists = False #Flag to let us skip things when recalculating with parameter (sidebar) changes
        
        #TODO: Change color to red?
        self.remove_button = ctk.CTkButton(self, text="X", width=20, height=20, command=self.x_button_press)
        self.remove_button.grid(row=0,column=0,sticky="w")
        
        self.item_select = ItemSelectFrame(self)
        self.item_select.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        
        if self.show_stats:
            self.item_stats = ItemStatsFrame(self, self.stats_dict)
        else:
            self.item_stats = ctk.CTkFrame(self, height=20)
        self.item_stats.grid(row=2,column=0,padx=10,pady=(0,10),sticky="ew")
        
        if self.show_ratings:
            self.item_ratings = ItemRatingsFrame(self, self.ratings_dict)
        else:
            self.item_ratings = ctk.CTkFrame(self, height=20)
        self.item_ratings.grid(row=3,column=0,padx=10,pady=(0,10),sticky="ew")
        
        self.exists=True
        
    def update_show_stats(self, show_stats):
        self.item_stats.destroy()
        if show_stats.get() == "on":
            self.item_stats = ItemStatsFrame(self, self.stats_dict)
            self.show_stats=True
        else:
            self.item_stats = ctk.CTkFrame(self, height=20)
            self.show_stats = False
        self.item_stats.grid(row=2,column=0,padx=10,pady=(0,10),sticky="ew")
        
    def update_show_ratings(self, show_ratings):
        self.item_ratings.destroy()
        if show_ratings.get() == "on":
            self.item_ratings = ItemRatingsFrame(self, self.ratings_dict)
            self.show_ratings = True
        else:
            self.item_ratings = ctk.CTkFrame(self, height=20)
            self.show_ratings = False
        self.item_ratings.grid(row=3,column=0,padx=10,pady=(0,10),sticky="ew")
        
    def x_button_press(self):
        self.exists=False
        self.master.item_removed()
        
    def get_params(self):
        return self.master.get_params()
    
    def get_dfs(self):
        return self.master.get_dfs()
    
    def update_stats(self, stats_dict):
        self.stats_dict = stats_dict
        if self.show_stats:
            self.item_stats.update_stats(self.stats_dict)
    def update_ratings(self, ratings_dict):
        self.ratings_dict = ratings_dict
        if self.show_ratings:
            self.item_ratings.update_ratings(ratings_dict)
    
    #When class is updated, need to recalculate ratings derivation AND EV
    def updated_class(self):
        if self.item_exists:
            params = self.master.get_params() #Get new params
            #Recalculate ratings dict
            item_ratings_dict = stats_to_ratings(self.stats_dict, params["class"])
            self.update_ratings(item_ratings_dict)
            #Recalculate EV
            ev = get_essence_value(item_ratings_dict, params["class"], use_stat=params["stats_to_use"], essences=params["essences"])
            self.item_select.ev.set(f"{ev:.3f}")
    
    #When stats or essences are updated, only need to recalculate EV
    def updated_stats_or_essences(self):
        if self.item_exists:
            params = self.master.get_params() #get new params
            ev = get_essence_value(self.ratings_dict, params["class"], use_stat=params["stats_to_use"], essences=params["essences"])
            self.item_select.ev.set(f"{ev:.3f}")
            
    def reset_stats(self): #Resets dicts, flags, and stats/ratings frames
        self.item_exists = False
        self.stats_dict = None
        self.ratings_dict = None
        
        #Reset stats frame
        self.item_stats.destroy()
        if self.show_stats:
            self.item_stats = ItemStatsFrame(self, self.stats_dict)
        else:
            self.item_stats = ctk.CTkFrame(self, height=20)
        self.item_stats.grid(row=2,column=0,padx=10,pady=(0,10),sticky="ew")
        
        #Reset ratings frame
        self.item_ratings.destroy()
        if self.show_ratings:
            self.item_ratings = ItemRatingsFrame(self, self.ratings_dict)
        else:
            self.item_ratings = ctk.CTkFrame(self, height=20)
        self.item_ratings.grid(row=3,column=0,padx=10,pady=(0,10),sticky="ew")
        
        
class ItemSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        #Item Name Entry
        self.iname_lbl = ctk.CTkLabel(self, text="Item Name")
        self.iname_lbl.grid(row=0,column=0,padx=10,pady=10, sticky="w")
        self.iname = tk.StringVar()
        self.iname_entry = ctk.CTkEntry(self, textvariable=self.iname)
        self.iname_entry.grid(row=0, column=1, padx=(0,10), pady=(5,0), sticky="ew")
        
        #Item Level Entry
        self.ilvl_lbl = ctk.CTkLabel(self, text="Item Level")
        self.ilvl_lbl.grid(row=1,column=0,padx=10,pady=10, sticky="w")
        self.ilvl = tk.StringVar()
        self.ilvl_entry = ctk.CTkEntry(self, textvariable=self.ilvl, width=40)
        self.ilvl_entry.grid(row=1, column=1, padx=(0,10), pady=(0,5), sticky="w")
        
        #Essence Value
        self.ev_lbl = ctk.CTkLabel(self, text="Essence Value")
        self.ev_lbl.grid(row=2,column=0,padx=10,pady=10, sticky="w")
        self.ev = tk.StringVar()
        self.ev_entry = ctk.CTkEntry(self, textvariable=self.ev, width=80, state="disabled")
        self.ev_entry.grid(row=2, column=1, padx=(0,10), pady=(0,5), sticky="w")
        
        #Update button
        self.update_button = ctk.CTkButton(self, text="Update", command=self.update)
        self.update_button.grid(row=3,column=0, padx=10, pady=(5,10), sticky="ew", columnspan=2)
        
    def update(self):
        ilvl = self.ilvl.get()
        try:
            assert(int(ilvl) > 0 and int(ilvl) < 600)
        except:
            print("Ilvl not valid. Please select ilvl in range [1, 600]")
            self.ilvl_entry.configure(fg_color="red") #Make the ilvl entry red to signify bad entry
            self.master.reset_stats()
            return -1
        self.ilvl_entry.configure(fg_color= ("#F9F9FA", "#343638")) #Reset to default value for blue theme
            
        params = self.master.get_params()
        items_df, stat_curves_df = self.master.get_dfs()
        
        #Query item from database + get stats at ilvl
        try: 
            item_stats_dict = query_item(items_df, stat_curves_df, self.iname.get(), int(self.ilvl.get()))
        except NameError:
            print(f"Could not find item with name '{self.iname.get()}'")
            self.iname_entry.configure(fg_color="red") #Make the iname entry red to signify bad entry
            self.master.reset_stats()
            return -1
        self.iname_entry.configure(fg_color=("#F9F9FA", "#343638")) #Reset to default value for blue theme
        self.master.update_stats(item_stats_dict)
        self.master.item_exists = True
        
        #derive the ratings from stats + player class
        item_ratings_dict = stats_to_ratings(item_stats_dict, params["class"])
        self.master.update_ratings(item_ratings_dict)
        
        ev = get_essence_value(item_ratings_dict, params["class"], use_stat=params["stats_to_use"], essences=params["essences"])
        self.ev.set(f"{ev:.3f}")
    
        
        
class ItemStatsFrame(ctk.CTkFrame):
    def __init__(self, master, stats_dict=None):
        super().__init__(master)
        
        #Frame label
        self.title = ctk.CTkLabel(self, text="Item Stats")
        self.title.grid(row=0, column=0, padx=10, pady=(5,10), sticky="w")
        
        self.stat_val_lbls=[]
        self.update_stats(stats_dict)
        
        
    def update_stats(self, stats_dict):
        self.stat_val_lbls=[] #Remove previous labels
        if stats_dict is not None:
            i = 0
            for stat, value in stats_dict.items():
                if value > 0: #Only show non-zero stats
                    out_str = f"{int(value):,}  {stat}"
                    stat_val_lbl = ctk.CTkLabel(self, text=out_str)
                    stat_val_lbl.grid(row=i+1,column=0,padx=10, pady=(0,0), sticky="w")
                    self.stat_val_lbls.append(stat_val_lbl)
                    i+=1
                
class ItemRatingsFrame(ctk.CTkFrame):
    def __init__(self, master, ratings_dict=None):
        super().__init__(master)
        
        #Frame label
        self.title = ctk.CTkLabel(self, text="Derived Rating Values")
        self.title.grid(row=0, column=0, padx=10, pady=(5,10), sticky="w")
        
        self.rating_val_lbls={}
        for i, rating in enumerate(ratings_list):
            out_str = f"0  {rating}"
            rating_lbl = ctk.CTkLabel(self, text=out_str)
            rating_lbl.grid(row=i+1,column=0,padx=10,pady=(0,0),sticky="w")
            self.rating_val_lbls[rating] = rating_lbl
            
        self.update_ratings(ratings_dict)
            
    def update_ratings(self, ratings_dict):
        if ratings_dict is not None:
            for rating, val in ratings_dict.items():
                if rating in ratings_list:
                    out_str = f"{int(val):,}  {rating}"
                    self.rating_val_lbls[rating].configure(text=out_str)
        
        
class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, use_stats):
        super().__init__(master)
        
        self.class_select = ClassSelectFrame(self)
        self.class_select.grid(row=0,column=0, padx=0, pady=(0,10), sticky="ew")
        
        self.essence_select = EssenceSelectFrame(self)
        self.essence_select.grid(row=1, column=0, padx=0, pady=(0,10), sticky="ew")
        
        self.stats_select = StatsSelectFrame(self, use_stats)
        self.stats_select.grid(row=2, column=0, padx=0, pady=(0,10), sticky="ew")
        
        self.stats_var = ctk.StringVar(value="on")
        self.show_stats = ctk.CTkSwitch(self, text="Show Item Stats", command=self.toggle_stats, variable=self.stats_var,
                                        onvalue="on", offvalue="off")
        self.show_stats.grid(row=3, column=0, padx=(5,10), pady=(20,10), sticky="w")
        self.ratings_var = ctk.StringVar(value="on")
        self.show_ratings = ctk.CTkSwitch(self, text="Show Derived Rating Values", command=self.toggle_ratings, variable=self.ratings_var,
                                          onvalue="on", offvalue="off")
        self.show_ratings.grid(row=4, column=0, padx=(5,10), pady=(0,10), sticky="w")
        
        self.download_button = ctk.CTkButton(self, text="Update Data", command=self.download_event, height=56)
        self.download_button.grid(row=5, column=0, padx=10, pady=(20,10), sticky="ews")
        
    def toggle_stats(self):
        self.master.toggle_stats()
    def toggle_ratings(self):
        self.master.toggle_ratings()
        
    def get_params(self):
        pclass = self.class_select.selected_class.get()
        essence_type = self.essence_select.selected_essences.get()
        essences = ESSENCES[essence_type]
        stats = self.stats_select.get()
        return {"class": pclass, "essences": essences, "stats_to_use": stats} 
                                  
    def download_event(self):
        #Delete existing xml/csv files if they exist
        items_fp = 'data/items.xml'
        if os.path.exists(items_fp):
            os.remove(items_fp)
        curves_fp = 'data/progressions.xml'
        if os.path.exists(curves_fp):
            os.remove(curves_fp)
        items_csv_fp = 'data/items.csv'
        if os.path.exists(items_csv_fp):
            os.remove(items_csv_fp)
        curves_csv_fp = 'data/progressions.csv'
        if os.path.exists(curves_csv_fp):
            os.remove(curves_csv_fp)
        
        #Download items DB
        items_url = "https://raw.githubusercontent.com/LotroCompanion/lotro-items-db/master/items.xml"
        response = requests.get(items_url)
        if response.status_code == 200:
            with open(items_fp, "wb") as f:
                f.write(response.content)
        else:
            print("Failed to download items.xml file. Status code: {}".format(response.status_code))
        
        #Download stat progression curves DB
        curves_url = "https://raw.githubusercontent.com/LotroCompanion/lotro-data/master/common/progressions.xml"
        response = requests.get(curves_url)
        if response.status_code == 200:
            with open(curves_fp, "wb") as f:
                f.write(response.content)
        else:
            print("Failed to download progressions.xml file. Status code: {}".format(response.status_code))
        
        #Log successful downloads
        print("Finished downloading updated data")
        
        #re-parse xmls
        items_df = parse_items_xml(fp='data/items.xml')
        items_df = clean_items_df(items_df)
        items_df.to_csv('data/items.csv') #save to csv for faster loading
        stat_curves_df = parse_curves(fp='data/progressions.xml')
        stat_curves_df.to_csv('data/progressions.csv') #save to csv for faster loading
        #save new df's to master class
        self.master.items_df = items_df
        self.master.stat_curves_df = stat_curves_df
        
        
    def updated_class(self):
        self.master.updated_class()
    def updated_stats_or_essences(self):
        self.master.updated_stats_or_essences()
        
        
class ClassSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.selected_class = tk.StringVar()
        self.select_class = ctk.CTkComboBox(self, values=classes, variable=self.selected_class, command=self.update_class, state="readonly")
        self.selected_class.set(classes[0])
        
        im_fp = "images/Brawler.png"
        im = ctk.CTkImage(light_image=Image.open(im_fp), size=(30,30))
        self.im_lbl = ctk.CTkLabel(self, image=im, text="")
        
        self.select_class.grid(row=0, column=1, padx=(0,10), pady=10, sticky="ew")
        self.im_lbl.grid(row=0, column=0, padx=(5,10), pady=10, sticky="w")
        
    def update_class(self, selected_choice):
        self.update_class_image(selected_choice)
        self.master.updated_class()
        
    def update_class_image(self, selected_choice):
        fn = "images/" + selected_choice + ".png"
        im = ctk.CTkImage(light_image=Image.open(fn), size=(30,30))
        self.im_lbl.configure(image=im)
        
class EssenceSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.title = ctk.CTkLabel(self, text="Choose Essence Type")
        self.title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.selected_essences = tk.StringVar()
        self.select_essence = ctk.CTkComboBox(self, values=essences, variable=self.selected_essences, command=self.update_essences, width=185, state="readonly")
        self.select_essence.set(essences[0])
        self.select_essence.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
    
    def update_essences(self, choice):
        self.master.updated_stats_or_essences()
        
class StatsSelectFrame(ctk.CTkFrame):
    def __init__(self, master, use_stats):
        super().__init__(master)
        
        self.title = ctk.CTkLabel(self, text="Choose Stats")
        self.title.grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.checkboxes = []
        for i, stat in enumerate(ratings_list):
            checkbox = ctk.CTkCheckBox(self, text=stat, command=self.updated_stats)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10,0), sticky="w")
            if use_stats[stat]: #Not sure what default is, so just do both sides bc why not
                checkbox.select()
            else:
                checkbox.deselect()
            self.checkboxes.append(checkbox)
            
    def get(self):
        checkbox_vals = {} #make dict of rating: checked
        for i, checkbox in enumerate(self.checkboxes):
            checkbox_vals[ratings_list[i]] = checkbox.get() #.get() returns 1 or 0 for checked/not
        return checkbox_vals
        
    def updated_stats(self):
        self.master.updated_stats_or_essences()
        

if __name__ == "__main__":
    #force windows recognize this as a seperate application to get the taskbar icon to update correctly
    #or something like that? Ref: https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105
    myappid = 'bearingLotro.EVCalculator.v1' #Arbitrary unicode string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    #Appearance settings
    ctk.set_appearance_mode("dark") #Light/dark
    ctk.set_default_color_theme("blue") #Default color
    
    #Use pandas to read/write parsed xml files to csv to speed up app loading
    #Should drop load times from ~3.5s -> ~0.5s (based on my pc)
    if os.path.exists('data/items.csv'): #Read from .csv if possible
        items_df = pd.read_csv('data/items.csv')
    else:
        #Get DF of items
        items_df = parse_items_xml(fp='data/items.xml')
        items_df = clean_items_df(items_df)
        #Save parsed xml file to csv
        items_df.to_csv('data/items.csv')
    
    #Use pandas to read/write parsed xml files to csv to speed up app loading
    if os.path.exists('data/progressions.csv'): #Read from .csv if possible
        stat_curves_df = pd.read_csv('data/progressions.csv', index_col=0)
    else: #Otherwise parse from xml and save to csv
        #Get DF of stat curves
        stat_curves_df = parse_curves(fp='data/progressions.xml')
        #Save parsed xml file to csv
        stat_curves_df.to_csv('data/progressions.csv')
    
    
    #Get the list of stats to use in EV calculations
    use_stats = parse_use_stats_yaml('data/use_stats.yml')
    
    app=App(items_df, stat_curves_df, use_stats)
    #Run app
    app.mainloop()
    #TODO: Save stat selections on sidebar on exit to data/use_stats.yml