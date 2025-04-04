# Correct setting of NoData values (-9999) and tif compression

import os
import glob
import numpy as np
from osgeo import gdal
import multiprocessing as mp 
import concurrent.futures
gdal.DontUseExceptions()


def nodata(f):
    outname = f.replace("Cal_TF_TC_db_cubic_rename", "Cal_TF_TC_df_cubic_rename_noData").split(".")[0]+"_noData.tif"
    if not os.path.isfile(outname):
        img = gdal.Open(f)
        vh = img.GetRasterBand(1).ReadAsArray()
        vv = img.GetRasterBand(2).ReadAsArray()
        li = img.GetRasterBand(3).ReadAsArray()

        def mod (band):
            newband = np.where(band==0, -9999, band*100)
            return newband
            
        vv_mask = mod(vv)
        vh_mask = mod(vh)
        li_mask = mod(li) 
        gt=img.GetGeoTransform()
        proj= img.GetProjection()

        # Create new file
        driver = gdal.GetDriverByName("GTiff")
        driver.Register()
        options = ['COMPRESS=ZSTD', 'PREDICTOR=2'] 
        print(outname)           
        outds = driver.Create(outname,
            xsize=vv.shape[1],
            ysize=vv.shape[0],
            bands=3, 
            eType=gdal.GDT_Int32,
            options = options)
        
        outds.SetGeoTransform(gt)
        outds.SetProjection(proj)
        
        outband=outds.GetRasterBand(1)
        outband.WriteArray(vv_mask)
        outband.SetNoDataValue(-9999)
        
        outband=outds.GetRasterBand(2)
        outband.WriteArray(vh_mask)
        outband.SetNoDataValue(-9999)
        
        outband=outds.GetRasterBand(3)
        outband.WriteArray(li_mask)
        outband.SetNoDataValue(-9999)
        
        outband.FlushCache()   
        outband=None
        outds=None


# Path and files
path = r"D:\Data\EOVegetation\Processing\Cal_TF_TC_db_cubic_rename\*.tif"
filesdir = glob.glob(path, recursive=True)

# Parallel processing
if __name__ == '__main__':  # Required in Window
    with concurrent.futures.ProcessPoolExecutor(mp.cpu_count()) as executor:
        futures = [executor.submit(nodata, file) for file in filesdir]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
