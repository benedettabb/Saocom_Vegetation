import numpy as np 
import glob
from osgeo import gdal, ogr
from pathlib import Path 
import pandas as pd 
import os
from multiprocessing import Process


def rasterize (shp_in, ds_in):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapefile = driver.Open(shp_in)
    layer = shapefile.GetLayer()
    driver = gdal.GetDriverByName('MEM')
    mask_raster = driver.Create('', ds_in.RasterXSize, ds_in.RasterYSize, 1, gdal.GDT_Byte)
    mask_raster.SetGeoTransform(ds_in.GetGeoTransform())
    mask_raster.SetProjection(ds_in.GetProjection())
    gdal.RasterizeLayer(mask_raster, [1], layer, burn_values=[1])
    mask_array = mask_raster.GetRasterBand(1).ReadAsArray()
    return mask_array


def getTrend (dirs, shps, site):

    data = {"values_vv": [], "values_vh": [], "nan_percentage":[], "values_plia":[],
            "DateTime":[], "subswath":[], "orbit":[], "tile":[]}
            
    outnames = list()
    for d in dirs:
        name = Path(d).stem
        if sites_dic[site] in name:
            outnames.append(d)
    print("{} N. of files: {}".format(site, len(outnames)))

    for shp in shps:
        if site in Path(shp).stem:
            for out in outnames:
                date = Path(out).stem.split("_")[9]
                try:
                    ds = gdal.Open(out)
                    #get mask depending on shp file
                    mask_array = rasterize(shp, ds)
                    # get vv and vh and mask
                    vv = ds.GetRasterBand(1).ReadAsArray()                 
                    vh = ds.GetRasterBand(2).ReadAsArray()
                    plia = ds.GetRasterBand(3).ReadAsArray()
                    ls_mask = ds.GetRasterBand(4).ReadAsArray() 
                    
                    # Mask for shape file
                    def mod (band):
                        masked = np.where(mask_array == 1, band, -9999)
                        return masked
                    
                    # Mask for layover and shadow
                    def lsmask (band):
                        ls_masked = np.where(ls_mask==0, band, -9999)
                        return ls_masked
                    
                    # Set no data 
                    def nodata (band):
                        nodata_band = np.where(band==-9999, np.nan, band)
                        return nodata_band
                    
                    # Shape total pixels
                    vv_m = nodata(mod(vv))
                    shp_size = np.count_nonzero(~np.isnan(vv_m))
                    
                    # Outbands
                    vv_ls = nodata(lsmask(mod(vv)))
                    vh_ls = nodata(lsmask(mod(vh)))
                    plia_ls = nodata(lsmask(mod(plia)))
                                      
                    # get mean vv and vh
                    mean_vv = np.nanmean(vv_ls)
                    mean_vh = np.nanmean(vh_ls)
                    mean_plia = np.nanmean(plia_ls)

                    # Shape valid pixels after lsmask
                    valid = np.count_nonzero(~np.isnan(vv_ls))
                    valid_percentage = (valid*100)/shp_size

                    print(mean_vv, mean_vh, mean_plia, valid_percentage)

                    data["values_vv"].append(mean_vv)
                    data["values_vh"].append(mean_vh)
                    data["values_plia"].append(mean_plia)
                    data["nan_percentage"].append(valid_percentage)
                    data["DateTime"].append(date)
                    data["subswath"].append(Path(out).stem.split("_")[-3])
                    data["orbit"].append(Path(out).stem.split("_")[-2])
                    data["tile"].append(Path(out).stem.split("_")[-1])
                    
                except:
                    print("Passed: {}".format(out))
                    for key, _ in data.items():
                        data[key].append(np.nan)
                    
    df = pd.DataFrame(data)

    df["DateTime"] = pd.to_datetime(df["DateTime"], format = "%Y%m%dT%H%M%S")
    df.to_csv(
        os.path.join(r"D:\EOVeg\timeSeries\final_ls_mask","{}.csv".format(site)),
        sep=',', 
        encoding='utf-8'
    )


sites_dic = {
    "HOAL":"E051N016T1",  
    "Klausen_Leopoldsdorf":"E052N016T1", 
    "Lake_Neusiedl":"E052N015T1",
    "Puergschachen_Moor":"E051N015T1",
    "Raumberg_Gumpenstein":"E050N015T1",
    "Rosalia":"E052N015T1",
    "Stubai":"E048N015T1", 
    "Zoebelboden":"E051N015T1", 
}


dirs = glob.glob(r"D:\EOVeg\Data_final_lsmask\*tif", recursive=True)
shps = glob.glob(r"D:\EOVeg\timeSeries\final_ls_mask\*_Equi7.shp", recursive = True)


if __name__ == '__main__':   # Required in Window
    jobs = list() 
    for key, _ in sites_dic.items():
        jobs.append(Process(target = getTrend, args=(dirs, shps, key)))
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
        
