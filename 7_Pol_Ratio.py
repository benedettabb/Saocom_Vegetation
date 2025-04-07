# This is to add a pol ratio (VV/VH) band

import glob 
from osgeo import gdal 
import numpy as np
import os 
from pathlib import Path 
import concurrent.futures 


# Crea una mascher per layover e shadow sulla base della slope e del projected local incidence angle
def pol_ratio(d):
    outdir = os.path.join(r"C:\Users\Radar\Documents\EOVeg_temp", Path(d).name.replace(".tif", "_ratio.tif"))
    if not os.path.isfile(outdir):
        print("Processing {}".format(outdir))
        # Open SAR image
        ds = gdal.Open(d)
        gamma_vh = ds.GetRasterBand(1).ReadAsArray()
        gamma_vv = ds.GetRasterBand(2).ReadAsArray()
        pol_ratio = gamma_vv/gamma_vv
        
         # Create new tif with the mask
        driver = gdal.GetDriverByName("GTiff")
        driver.Register()
        # Compress option
        options = ['COMPRESS=ZSTD', 'PREDICTOR=2'] 
        outds = driver.Create(outdir,
            xsize=gamma_vv.shape[1],
            ysize=gamma_vv.shape[0],
            bands=5, 
            eType=gdal.GDT_Int32,
            options = options)
        outds.SetGeoTransform(ds.GetGeoTransform())
        outds.SetProjection(ds.GetProjection())
        # VH
        outband=outds.GetRasterBand(1)
        outband.WriteArray(gamma_vh)
        # VV
        outband=outds.GetRasterBand(2)
        outband.WriteArray(gamma_vv)
        # Pol ratio
        outband=outds.GetRasterBand(3)
        outband.WriteArray(pol_ratio)
        # PLIA
        outband=outds.GetRasterBand(4)
        outband.WriteArray(ds.GetRasterBand(3).ReadAsArray())
        # MASK      
        outband=outds.GetRasterBand(5)
        outband.WriteArray(ds.GetRasterBand(4).ReadAsArray())
        outband.SetNoDataValue(-9999)
        
        outband.FlushCache()   
        outband=None
        outds=None
        
dirs = glob.glob(r"D:\Data\EOVegetation\Processing\Cal_TF_TC_df_cubic_rename_noData_equi7_LS\*.tif")


# Parallel processing
if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(10) as executor:
        futures = [executor.submit(pol_ratio, d) for d in dirs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
