
import numpy as np
import glob
import csv
import pandas as pd 
import os 
from pathlib import Path

properties = r"D:\Data\EOVegetation\Utils\info\Saocom_scenes.csv"
names=list()
start_times=list()
orbit = list()
sub_mode = list()

def rename(input_file):
    with open(properties, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            names.append(row['Name'])
            start_times.append(row['StartTime'])
            orbit.append(row["OrbitDirection"])
            sub_mode.append([row["SubMode"]])
    df = pd.DataFrame({"Name": names,"StartTime": start_times, "SubMode": sub_mode, "OrbitDirection": orbit})
    
    for f in input_file:
        name = Path(f).stem.split(".")[0]
        for _, row in df.iterrows():
            if name ==row["Name"].split(".")[0]:
                acquisition_date = row["StartTime"].replace("-","").replace(":","").split(".")[0]
                outname = "{}_{}_{}_{}.tif".format(
                    name, 
                    acquisition_date, 
                    row["SubMode"][0], 
                    row["OrbitDirection"][:3])
                print(outname)
                outdir=os.path.join(
                    r"D:\Data\EOVegetation\Processing\Cal_TF_TC_db_cubic_rename",
                    outname)
                os.rename(f,outdir)



input_file = glob.glob(r"D:\Data\EOVegetation\Processing\Cal_TF_TC_db_cubic\*\*\*\*.tif", recursive=True)
rename(input_file) 
