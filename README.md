#Repository for all things Essence Value Calculator

##Requirements
Make sure you have downloaded Python3 including the following libraries: pandas, numpy, customtkinter (you can `pip install` those after python3 is downloaded).
Note that windows is weird with path variables + Python. If this is your first time downloading Python on windows, and you run into an error where it says python isn't installed, follow this guide: https://www.educative.io/answers/how-to-add-python-to-path-variable-in-windows

##GUI
There is a gui built in to main.py. Simply download this repository, open a cmd prompt and `cd` your way to the repository, and run `Python main.py` to open the gui. This will be turned into an application at some time in the future for easier use using pyinstaller.
The gui includes a button to update the data which re-downloads the database files from Lotro-Companion. This data totals to around 65MB (and growing with each added item) and doesn't have a confirmation popup (sorry I'm lazy and 65MB isn't really that bad), so don't click it if you're low on data usage I guess.
The data will also be re-saved to a .csv after being parsed and trimmed so that the app loads faster (~4s -> ~1s in my limited testing on my pc). This eats up only a small amount of extra memory (~20MB), if that's an issue for anyone, please just get a new hard drive (or reach out and I'll make this optional... please don't make me)

#CLI
There is also CLI usage for each (most) of the .py files. I didn't add an update data function here so either use the GUI function for that or do it manually.
To get an item's stats at a specified item level, run `Python query_item.py -n <item name> -i <item level>`
To get an item's derived stats at a specified item level for a specified class, run `Python query_item.py -n <item name> -i <item level> -r -c <class>`
To get an item's essence value, run `Python essence_value.py -n <item name> -i <item level> -c <class>`
Note that <item name> should be surrounded by quotes if more than one word, ilvl needs to be [0,550] (for now, will increase range if needed), and file paths can be specified if they're not in the default locations using `--items_fp` and `--stat_curves_fp` (defaults are "data/items.xml" and "data/progressions.xml")
