import glob 
from osgeo import gdal 
import numpy as np
import os 
from pathlib import Path 

#########################################################################################################################

# Salva in memoria un resampling del DEM adattato alla risoluzione e estensione dell'immagine SAR
def resample_dem(dem_path, target_ds):
    dem_ds = gdal.Open(dem_path)
    geo_transform = target_ds.GetGeoTransform()
    x_min = geo_transform[0]
    x_max = x_min + geo_transform[1] * target_ds.RasterXSize
    y_max = geo_transform[3]
    y_min = y_max + geo_transform[5] * target_ds.RasterYSize
    resampled_dem = gdal.Warp('', dem_ds, format='MEM', 
                                 xRes=geo_transform[1], 
                                 yRes=-geo_transform[5], 
                                 outputBounds=(x_min, y_max, x_max, y_min),  # Usa i limiti calcolati
                                 resampleAlg=gdal.GRA_Bilinear)
    return resampled_dem

#######################################################################################################################


# Crea una mascher per layover e shadow sulla base della slope e del projected local incidence angle
def mask_layover_shadow(d, dem_dirs):
    outdir = d.replace(".tif", "_ls.tif")
    if not os.path.isfile(outdir):
        # Get corresponding DEM based on tile name 
        tile = Path(d).stem.split("_")[-1]
        for d in dem_dirs:
            if tile in d:
                dem = d
                
        # Open SAR image
        ds = gdal.Open(d)
        lpia = ds.GetRasterBand(3).ReadAsArray()
        x_min, x_res, _ , y_max, _, y_res = ds.GetGeoTransform()    
            
        # Open DEM 
        dem_ds = gdal.Open(dem)
        slope = dem_ds.GetRasterBand(1).ReadAsArray()

        print(lpia.shape, slope.shape)
        
    
        # Mask for layover and shadow
        layover_mask = np.where(slope>lpia, 1, np.nan) 
        shadow_mask = np.where(slope>(90-lpia), 2, np.nan)
        lpia_mask = np.where(np.isnan(layover_mask), shadow_mask, layover_mask)
        
        dem_ds=None
        
        # Create new tif with the mask
        driver = gdal.GetDriverByName("GTiff")
        driver.Register()
        # Compress option
        options = ['COMPRESS=ZSTD', 'PREDICTOR=2'] 
        outds = driver.Create(outdir,
            xsize=lpia.shape[1],
            ysize=lpia.shape[0],
            bands=1, 
            eType=gdal.GDT_Int16,
            options = options)
        outds.SetGeoTransform(ds.GetGeoTransform())
        outds.SetProjection(ds.GetProjection())
        outband=outds.GetRasterBand(1)
        outband.WriteArray(lpia_mask)
        outband.SetNoDataValue(np.nan)
        outband.FlushCache()   
        outband=None
        outds=None


dirs = glob.glob(r"D:\Data\EOVegetation\Processing\Cal_TF_TC_df_cubic_rename_noData_equi7\*.tif")
dem_dirs = r"D:\Data\EOVegetation\Utils\slope_equi7_10m\*tif"
[mask_layover_shadow(d, dem_dirs) for d in dirs]

