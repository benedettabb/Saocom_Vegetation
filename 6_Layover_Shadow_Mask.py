# This is to add a layover and shadow mask band to each scene.
# Slope rasters in degrees are needed, at the same resolution of the data, and into Equi7grid T01 tiles
# Projected Local Incidence Angle is needed
# Naming of the slope rasters i.e. slope_equi7_10m_2018_E048N015T1.tif

# Layover:
    # (Slope - Local Projected Incidence Angle)>20
# Shadow:
    # Slope > (90-Local Projected Incidence Angle)

import glob 
from osgeo import gdal 
import numpy as np
import os 
from pathlib import Path 
import multiprocessing as mp 
import concurrent.futures 
from scipy.ndimage import binary_erosion


# Erode
def erode_mask(mask, kernel_size):
    binary_mask = np.where(mask > 0, 1, 0)
    eroded_mask = binary_erosion(binary_mask, structure=np.ones((kernel_size, kernel_size))).astype(np.float32)
    return mask * eroded_mask


# Mask
def mask_layover_shadow(d, dem_dirs):
    outdir = os.path.join(r"C:\Users\Radar\Documents\EOVeg_temp", Path(d).name.replace(".tif", "_ls.tif"))
    if not os.path.isfile(outdir):
        print("Processing {}".format(outdir))
        # Get corresponding DEM based on tile name 
        tile = Path(d).stem.split("_")[-1]
        dem = None
        for dem_dir in dem_dirs:
            if tile in dem_dir:
                dem = dem_dir

        # Open SAR image
        ds = gdal.Open(d)
        lpia = ds.GetRasterBand(3).ReadAsArray()
        gamma_vh = ds.GetRasterBand(1).ReadAsArray()
        gamma_vv = ds.GetRasterBand(2).ReadAsArray()
        lpia = lpia/100
            
        # Open SLOpe 
        dem_ds = gdal.Open(dem)
        slope = dem_ds.GetRasterBand(1).ReadAsArray()

        # print(lpia.shape, slope.shape) # Make sure they have the same shape       
    
        # Mask for layover and shadow     
        layover_mask = np.where((slope-lpia)>20, 2, np.nan) 
        shadow_mask = np.where(slope>(90-lpia), 1, np.nan)
        lpia_mask = np.where(np.isnan(layover_mask), shadow_mask, layover_mask)
        
        # No data
        def mod (band):
            return np.where(gamma_vh<-3000, -9999, band)
        
        lpia_mask = mod(lpia_mask)
        gamma_vv = mod(gamma_vv)
        lpia = mod(lpia)
        gamma_vh = mod(gamma_vh)  
              
        # Erode
        lpia_mask = erode_mask(lpia_mask, 2)
        lpia_mask = np.where(lpia_mask==0, -9999, lpia_mask)     
           
        # Close Slope raster
        dem_ds=None
        
        # Create new tif with the mask
        driver = gdal.GetDriverByName("GTiff")
        driver.Register()
        # Compress option
        options = ['COMPRESS=ZSTD', 'PREDICTOR=2'] 
        outds = driver.Create(outdir,
            xsize=lpia.shape[1],
            ysize=lpia.shape[0],
            bands=4, 
            eType=gdal.GDT_Int32,
            options = options)
        outds.SetGeoTransform(ds.GetGeoTransform())
        outds.SetProjection(ds.GetProjection())
        # VH
        outband=outds.GetRasterBand(1)
        outband.WriteArray(gamma_vh)
        outband.SetNoDataValue(-9999)
        # VV
        outband=outds.GetRasterBand(2)
        outband.WriteArray(gamma_vv)
        outband.SetNoDataValue(-9999)
        # PLIA
        outband=outds.GetRasterBand(3)
        outband.WriteArray(lpia)
        outband.SetNoDataValue(-9999)
        # MASK      
        outband=outds.GetRasterBand(4)
        outband.WriteArray(lpia_mask)
        outband.SetNoDataValue(-9999)
        outband.FlushCache()   
        outband=None
        outds=None


dirs = glob.glob(r"D:\Data\EOVegetation\Processing\Cal_TF_TC_df_cubic_rename_noData_equi7\*.tif")
dem_dirs = glob.glob(r"D:\Data\EOVegetation\Utils\slope_equi7_10m\*tif")


# Parallel processing
if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(10) as executor:
        futures = [executor.submit(mask_layover_shadow, d, dem_dirs) for d in dirs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        

