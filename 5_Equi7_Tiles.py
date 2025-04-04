# This is to project the scenes into the Equi7 T01 grid reference system


from pathlib import Path
from osgeo import gdal
import os
import glob 
from multiprocessing import Process
import numpy as np 

# Equi7 grid reference system
equi7 = "+proj=aeqd +lat_0=53 +lon_0=24 +x_0=5837287.82 +y_0=2121415.696"    

# Return pixel corners of Equi7 tile based on the tile name   
def getBounds(tile_name):
    xmin = int(tile_name[2:4])*100000
    xmax = xmin+100000
    ymin = int(tile_name[6:8])*100000
    ymax = ymin+100000
    return xmin, ymin, xmax, ymax

# Return Equi7grid tiles
def tiling (tile, filedirs):
    bounds = getBounds(tile)
    options = {
        "xRes": 10,
        "yRes": 10,
        "outputBounds": (bounds[0],bounds[1], bounds[2], bounds[3]),
        "dstSRS": equi7,
        "outputType": gdal.GDT_Int32,
        "dstNodata": -9999,
        "srcNodata": -9999,
        "resampleAlg" : gdal.GRA_Cubic,
        "creationOptions": ['COMPRESS=ZSTD', 'PREDICTOR=2']
    }
    
    for f in filedirs:
        out_f = os.path.join(r"C:\Users\Radar\Documents\EOVeg_temp",Path(f).name.replace(".tif", f"_{tile}.tif"))
        print(out_f)
        if not os.path.isfile(out_f):
            ds = gdal.Open(f)
            ds_out = gdal.Warp(out_f, ds, **options)  

            ds_out = gdal.Open(out_f)  # Check if the tile is emply
            band_out = ds_out.GetRasterBand(1)
            data_out = band_out.ReadAsArray()

            if np.all(data_out == -9999):
                print(f"Deleting file {out_f} because it contains only -9999 values")
                ds_out=None
                os.remove(out_f) 
            else:
                print(f"Tile {tile} processed and saved to {out_f}")
                ds_out = None  
                ds = None  

# Data
path = r"D:\Data\EOVegetation\Processing\Cal_TF_TC_df_cubic_rename_noData\*.tif"
data = glob.glob(path, recursive = True)

# Tiles list
tiles = ["E048N017T1", "E049N017T1", "E050N017T1", "E051N017T1", "E052N017T1", "E053N017T1"]

if __name__ == '__main__':   # Required in Window
    jobs = list() 
    for t in tiles:
        jobs.append(Process(target = tiling, args=(t, data))) 
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
        
       
        
        
