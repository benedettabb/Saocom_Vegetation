import os
import glob
import numpy as np
from osgeo import gdal
import gc #garbage collector
from multiprocessing import Process
import multiprocessing as mp 
import time
gdal.DontUseExceptions()


#path and files
path = r"D:\Data\EOVegetation\Processing\Cal_TF_TC_db_cubic_rename\*.tif"
filesdir = glob.glob(path, recursive=True)


# function to calculate percentile - the image is splitted in 4 subset to avoid memory error
def nodata(files):
    for f in files: 
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


nodata(filesdir)