# Code adapted from: 
# Vollrath, A., Mullissa, A., & Reiche, J. (2020). Angular-Based Radiometric Slope Correction for Sentinel-1 on Google Earth Engine. Remote Sensing, 12(11), 1867. https://doi.org/10.3390/rs12111867

import numpy as np 
import glob
from osgeo import gdal 
from pathlib import Path 
import os 

def get_tile (dirs, tile):
    outdir = list()
    for d in dirs:
        if tile in d:
            outdir.append(d)
    return outdir

def get_identical (dirs, name):
    outdir2 = list()
    for i in dirs:
        if Path(i).stem == name:
            outdir2.append(i) 
        else:
            pass
    return outdir2
        
def get_slope_in_range(phii, alphas, phis):
    phir = phii - phis 
    # Slope in range direction
    alphar = np.arctan(np.tan(alphas) * np.cos(phir))   
    return alphar

        
def main (dirs_backscatter, dirs_ia, dirs_slope, dirs_aspect, tile, name):
    bs = get_tile(get_identical(dirs_backscatter, name),tile)
    ia = get_tile(get_identical(dirs_ia, name),tile)
    try:
        bs = bs[0]
        ia = ia[0]
        slope = get_tile(dirs_slope, tile)[0]
        aspect = get_tile(dirs_aspect, tile)[0]
        print("Tile", tile)
        print("Name", name)
        print(bs, ia)
        print(aspect, slope)

        # Open with gdal
        ds_bs = gdal.Open(bs)
        ds_ia = gdal.Open(ia)
        ds_slope = gdal.Open(slope)
        ds_aspect = gdal.Open(aspect)    
        # # Backscatter
        vv = ds_bs.GetRasterBand(1).ReadAsArray()
        vh = ds_bs.GetRasterBand(2).ReadAsArray()
        lpia = ds_bs.GetRasterBand(3).ReadAsArray()


        # Radar angles
        thetai = ds_ia.GetRasterBand(1).ReadAsArray()
        if "ASC" in name:
            phii_rad = np.deg2rad(100) # change with real aspect
        elif "DES" in name:
            phii_rad = np.deg2rad(100)


        # Terrain angles
        alphas = ds_slope.GetRasterBand(1).ReadAsArray()
        phis = ds_aspect.GetRasterBand(1).ReadAsArray()

        thetai = np.where (thetai<-100, np.nan, thetai/100) # -> ricordati di dividereee
        alphas = np.where (alphas<-100, np.nan, alphas)
        phis = np.where (phis<-100, np.nan, phis)

        # radiants
        thetai_rad = np.deg2rad(thetai)    
        alphas_rad = np.deg2rad(alphas)    
        phis_rad = np.deg2rad(phis)

        # get slope in range
        alphar_rad = get_slope_in_range(phii_rad, alphas_rad, phis_rad)

        #layover and shadow mask
        layover = np.where(alphar_rad > thetai_rad, 2, np.nan) 
        shadow = np.where((thetai_rad-alphar_rad) > np.deg2rad(90), 1, np.nan)
        
        lpia_mask = np.where(np.isnan(layover), shadow, layover)

        # Create new tif with the mask
        driver = gdal.GetDriverByName("GTiff")
        driver.Register()
        options = ['COMPRESS=ZSTD', 'PREDICTOR=2'] # Compress option
        outds = driver.Create(os.path.join(r"D:\EOVeg\Data_final_lsmask", f"{name}.tif"),
            xsize=vv.shape[1],
            ysize=vv.shape[0],
            bands=4, 
            eType=gdal.GDT_Float32,
            options = options)
        outds.SetGeoTransform(ds_bs.GetGeoTransform())
        outds.SetProjection(ds_bs.GetProjection())
        # vv
        outband=outds.GetRasterBand(1)
        outband.WriteArray(vv)
        outband.SetNoDataValue(-9999)
        # vh
        outband=outds.GetRasterBand(2)
        outband.WriteArray(vh)
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

    except Exception as e:
        print(e)





# directories
dirs_ia = glob.glob(r"D:\EOVeg\ellipsoid_incidence_angle\incidence_angle_equi7\ia\**\*tif")
dirs_backscatter = glob.glob(r"D:\EOVeg\Data_final\*tif")
dirs_slope = glob.glob(r"D:\EOVeg\ellipsoid_incidence_angle\incidence_angle_equi7\DEM\slope*.tif")
dirs_aspect = glob.glob(r"D:\EOVeg\ellipsoid_incidence_angle\incidence_angle_equi7\DEM\aspect*.tif")
names = [Path(d).stem for d in dirs_backscatter]

# Equi7grid tiles
tiles = ["E048N017T1", "E049N017T1", "E050N017T1", "E051N017T1", "E052N017T1", "E053N017T1",
        "E048N016T1", "E049N016T1", "E050N016T1", "E051N016T1", "E052N016T1", "E053N016T1",
        "E048N015T1", "E049N015T1", "E050N015T1", "E051N015T1", "E052N015T1", "E053N015T1",
        "E048N014T1", "E049N014T1", "E050N014T1", "E051N014T1", "E052N014T1", "E053N014T1"]

for n in names:
    main(dirs_backscatter, dirs_ia, dirs_slope, dirs_aspect, "E048N015T1", n)
