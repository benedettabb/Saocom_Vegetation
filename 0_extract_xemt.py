
# this is to read properies from all xemt files associated with each SAOCOM scene
# output csv with id, date, orbit dir ect

import glob
import pandas as pd
from pathlib import Path 
from os.path import dirname as up


files = glob.glob(r"D:\Data\EOVegetation\Data\*\*\*\*.xemt", recursive=True)

names=[Path(f).stem for f in files]
sites = [str(Path(f).parents[2]).split(r'EOVegetation\Data')[1][1:] for f in files]

identifier = "<id>"
startTime = "<startTime>"
subMode = "<Swath>"
orbitDirection = "<OrbitDirection>"

def read_prop(key_start, key_end):
    lista=[]
    for i in files:
        reader = pd.read_csv(i, sep="\t", header=None, engine='python')
        dates=[]
        for row in reader.iterrows():
            row_str = str(row[1])
            if key_start in row_str:
                splitted= row_str.split(key_start)
                date=splitted[1]
                splitted1 = date.split(key_end)
                dates.append(splitted1)
        lista.append(dates[0][0])
    return lista

id_list = read_prop(identifier, "</")  # list of ids
startTime_list = read_prop(startTime, "...")  # list of acquisition dateTime
subMode_list = read_prop(subMode, "</")  # list of submodes    
orbitDirection_list = read_prop(orbitDirection, "</")  # list of orbit directions

dict = {'Name': names,
        "Site": sites,
        'Id': id_list, 
        'StartTime': startTime_list, 
        'SubMode': subMode_list, 
        "OrbitDirection": orbitDirection_list}

df = pd.DataFrame(dict)

df.to_csv(r"D:\Data\EOVegetation\Data\Saocom_scenes.csv", index=False)
print(df)