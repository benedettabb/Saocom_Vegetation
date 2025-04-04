
from pathlib import Path
from osgeo import gdal
import os
import glob 
from multiprocessing import Process, pool
import numpy as np 
from concurrent.futures import ThreadPoolExecutor

equi7 = "+proj=aeqd +lat_0=53 +lon_0=24 +x_0=5837287.82 +y_0=2121415.696"    

              
def getBounds(tile_name):
    xmin = int(tile_name[2:4])*100000
    xmax = xmin+100000
    ymin = int(tile_name[6:8])*100000
    ymax = ymin+100000
    return xmin, ymin, xmax, ymax


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
    
    files = glob.glob(filedirs, recursive = True)
    
    for f in files:
        out_f = os.path.join(r"C:\Users\Radar\Documents\EOVeg_temp",Path(f).name.replace(".tif", f"_{tile}.tif"))
        print(out_f)
        if not os.path.isfile(out_f):
            ds = gdal.Open(f)
            ds_out = gdal.Warp(out_f, ds, **options)  

            ds_out = gdal.Open(out_f)  # Riapri il file appena scritto
            band_out = ds_out.GetRasterBand(1)
            data_out = band_out.ReadAsArray()

            if np.all(data_out == -9999):
                print(f"Deleting file {out_f} because it contains only -9999 values")
                ds_out=None
                os.remove(out_f)  # Cancella il file se contiene solo -9999
            else:
                print(f"Tile {tile} processed and saved to {out_f}")
                ds_out = None  
                ds = None  

data = r"D:\Data\EOVegetation\Processing\Cal_TF_TC_df_cubic_rename_noData\*.tif"

if __name__ == '__main__':  
    jobs = list()
    
    jobs.append(Process(target = tiling, args=("E048N017T1", data))) 
    jobs.append(Process(target = tiling, args=("E049N017T1", data))) 
    jobs.append(Process(target = tiling, args=("E050N017T1", data))) 
    jobs.append(Process(target = tiling, args=("E051N017T1", data))) 
    jobs.append(Process(target = tiling, args=("E052N017T1", data))) 
    jobs.append(Process(target = tiling, args=("E053N017T1", data)))

    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
        
        
# if __name__ == '__main__':  
#     jobs = list()
    
#     jobs.append(Process(target = tiling, args=("E048N016T1", data))) 
#     jobs.append(Process(target = tiling, args=("E049N016T1", data))) 
#     jobs.append(Process(target = tiling, args=("E050N016T1", data))) 
#     jobs.append(Process(target = tiling, args=("E051N016T1", data))) 
#     jobs.append(Process(target = tiling, args=("E052N016T1", data))) 
#     jobs.append(Process(target = tiling, args=("E053N016T1", data)))

#     for j in jobs:
#         j.start()
#     for j in jobs:
#         j.join()
        


# if __name__ == '__main__':  
#     jobs = list()
    
#     jobs.append(Process(target = tiling, args=("E048N015T1", data))) 
#     jobs.append(Process(target = tiling, args=("E049N015T1", data))) 
#     jobs.append(Process(target = tiling, args=("E050N015T1", data))) 
#     jobs.append(Process(target = tiling, args=("E051N015T1", data))) 
#     jobs.append(Process(target = tiling, args=("E052N015T1", data))) 
#     jobs.append(Process(target = tiling, args=("E053N015T1", data)))

#     for j in jobs:
#         j.start()
#     for j in jobs:
#         j.join()
        
        
# if __name__ == '__main__':  
#     jobs = list()
    
#     jobs.append(Process(target = tiling, args=("E048N014T1", data))) 
#     jobs.append(Process(target = tiling, args=("E049N014T1", data))) 
#     jobs.append(Process(target = tiling, args=("E050N014T1", data))) 
#     jobs.append(Process(target = tiling, args=("E051N014T1", data))) 
#     jobs.append(Process(target = tiling, args=("E052N014T1", data))) 
#     jobs.append(Process(target = tiling, args=("E053N014T1", data)))

#     for j in jobs:
#         j.start()
#     for j in jobs:
#         j.join()
        
        