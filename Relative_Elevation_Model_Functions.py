# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 07:48:53 2019

@author: Colin.Dowey
"""

# This script defines three functions for creating relative elevation models (REMs). 
# REMs are commonly used to visualize river meanders, abandoned channels, and fluvial terraces.
# However, they can also be used in other erosional/depositional environments as well (ie, kame deposits, lateral moraines)

# A great source of information on these three methods can be found here https://fortress.wa.gov/ecy/publications/documents/1406025.pdf
# These functions closely follow the steps outlined in Appendix E.
# Writing these steps out as functions allows for quick refinement of the search radius, cross-sections, and other parameters

# This script uses ArcGIS tools through the arcpy module, I also hope to write this using open source tools in the future

# Each function starts by selecting a flowline by name from the USGS National Hydrography Dataset.
# If you want to use a different or more accurate river channel trace replace these 3 steps and read in your river channel trace 

import arcpy
from arcpy.sa import *
from arcpy.ddd import *
from pathlib import Path

# Kernel Density Method

def Kernel_Density_REM(DEM, NHDFlowline, RiverName, PointDistance_meters, SearchRadius, Output_gdb_path):
    
    # Set environment
    arcpy.env.workspace = Output_gdb_path
    
    # Names for selecting and saving
    rivername = RiverName.replace(' ','')
        
    # Create path object for Output_gdb_path
    Output_gdb_filepath = Path(Output_gdb_path)
    
    # Create Output_gdb if it does not already exist
    if not Output_gdb_filepath.exists():
        arcpy.CreateFileGDB_management(str(Output_gdb_filepath.parent), str(Output_gdb_filepath.name))
    
    # Define River Channel and create feature class with single line feature
    river_flowline = arcpy.SelectLayerByAttribute_management(NHDFlowline, 'New_Selection', "GNIS_Name = '" + RiverName + "'")
    
    river_name_path = str(Output_gdb_filepath / rivername)
    arcpy.CopyFeatures_management(river_flowline, river_name_path)
    
    diss_river_name_path = str(Output_gdb_filepath / str(rivername + '_diss'))
    arcpy.Dissolve_management(river_name_path, diss_river_name_path)
    
    # Generate points along channel line
    river_points_path = str(Output_gdb_filepath / str(rivername + '_points'))
    arcpy.GeneratePointsAlongLines_management(diss_river_name_path, river_points_path, 'DISTANCE', Distance = (str(PointDistance_meters) + ' meters'))
    
    # Extract elevation to points
    river_points_elev = str(Output_gdb_filepath / str(rivername + '_elev'))
    arcpy.sa.ExtractValuesToPoints(river_points_path, DEM, river_points_elev)
    
    # Kernel Density Point
    PointKernel = str(Output_gdb_filepath / str(rivername + '_PntKernel'))
    DEM_cellsize = float(str(arcpy.GetRasterProperties_management (DEM, "CELLSIZEX")))
    PointKernelDensity = arcpy.sa.KernelDensity(river_points_elev, "NONE", DEM_cellsize, SearchRadius, "SQUARE_METERS")
    PointKernelDensity.save(PointKernel)
    
    # Kernel Density Elevation
    StreamKernel = str(Output_gdb_filepath / str(rivername + '_StreamKernel'))
    StreamElevKernelDensity = arcpy.sa.KernelDensity(river_points_elev, "RASTERVALU", DEM_cellsize, SearchRadius, "SQUARE_METERS")
    StreamElevKernelDensity.save(StreamKernel)
    
    # Create the detrended DEM by dividing the cumulative stream elevation raster by the point density raster
    det_DEM = str(Output_gdb_filepath / str(rivername + '_DetDEM'))
    detrended_DEM = arcpy.sa.Divide(StreamElevKernelDensity, PointKernelDensity)
    detrended_DEM.save(det_DEM)

    # Create Relative Elevation Model
    relative_elevation_model = str(str(Output_gdb_filepath / str(rivername + '_RelElevModel')))
    REM = arcpy.sa.Minus(DEM, detrended_DEM)
    REM.save(relative_elevation_model)

        
# Inverse Distance Weighted Method

def IDW_REM(DEM, NHDFlowline, RiverName, PointDistance_meters, SearchRadius, Output_gdb_path):

    # Set environment
    arcpy.env.workspace = Output_gdb_path
    
    # Names for selecting and saving
    rivername = RiverName.replace(' ','')
        
    # Create path object for Output_gdb_path
    Output_gdb_filepath = Path(Output_gdb_path)
    
    # Create Output_gdb if it does not already exist
    if not Output_gdb_filepath.exists():
        arcpy.CreateFileGDB_management(str(Output_gdb_filepath.parent), str(Output_gdb_filepath.name))
    
    # Define River Channel and create feature class with single line feature
    river_flowline = arcpy.SelectLayerByAttribute_management(NHDFlowline, 'New_Selection', "GNIS_Name = '" + RiverName + "'")
    
    river_name_path = str(Output_gdb_filepath / rivername)
    arcpy.CopyFeatures_management(river_flowline, river_name_path)
    
    diss_river_name_path = str(Output_gdb_filepath / str(rivername + '_diss'))
    arcpy.Dissolve_management(river_name_path, diss_river_name_path)
    
    # Generate points along channel line
    river_points_path = str(Output_gdb_filepath / str(rivername + '_points'))
    arcpy.GeneratePointsAlongLines_management(diss_river_name_path, river_points_path, 'DISTANCE', Distance = (str(PointDistance_meters) + ' meters'))
    
    # Extract elevation to points
    river_points_elev = str(Output_gdb_filepath / str(rivername + '_elev'))
    arcpy.sa.ExtractValuesToPoints(river_points_path, DEM, river_points_elev)
    
    # IDW to create detrended DEM
    idw_detrended = str(Output_gdb_filepath / str(rivername + '_IDW_detrend'))
    DEM_cellsize = float(str(arcpy.GetRasterProperties_management (DEM, "CELLSIZEX")))
    idw = arcpy.sa.Idw(river_points_elev, 'RASTERVALU', DEM_cellsize, 2, RadiusFixed(SearchRadius, 0))
    idw.save(idw_detrended)
    
    # Create Relative Elevation Model
    relative_elevation_model = str(str(Output_gdb_filepath / str(rivername + '_RelElevModel')))
    REM = arcpy.sa.Minus(DEM, idw_detrended)
    REM.save(relative_elevation_model)

# Cross-Section Method

def Cross_Section_REM(DEM, NHDFlowline, RiverName, CrossSectionLines, Output_gdb_path):
    
    # Set environment
    arcpy.env.workspace = Output_gdb_path
    
    # Names for selecting and saving
    rivername = RiverName.replace(' ','')
        
    # Create path object for Output_gdb_path
    Output_gdb_filepath = Path(Output_gdb_path)
    
    # Create Output_gdb if it does not already exist
    if not Output_gdb_filepath.exists():
        arcpy.CreateFileGDB_management(str(Output_gdb_filepath.parent), str(Output_gdb_filepath.name))
    
    # Define River Channel and create feature class with single line feature
    river_flowline = arcpy.SelectLayerByAttribute_management(NHDFlowline, 'New_Selection', "GNIS_Name = '" + RiverName + "'")
    
    river_name_path = str(Output_gdb_filepath / rivername)
    arcpy.CopyFeatures_management(river_flowline, river_name_path)
    
    diss_river_name_path = str(Output_gdb_filepath / str(rivername + '_diss'))
    arcpy.Dissolve_management(river_name_path, diss_river_name_path)
    
    # Create points at cross-section / river intersections
    river_xs_int = str(Output_gdb_filepath / str(rivername + '_int'))
    arcpy.Intersect_analysis([diss_river_name_path, CrossSectionLines], river_xs_int, "ALL", "", "POINT")
    
    # Convert from multipoint to point
    river_xs_intpt = str(Output_gdb_filepath / str(rivername + '_intpt'))
    arcpy.FeatureToPoint_management(river_xs_int, river_xs_intpt, "CENTROID")
    
    # Extract Values to Points to get elevations at these intersections points
    river_points_elev = str(Output_gdb_filepath / str(rivername + '_elev'))
    arcpy.sa.ExtractValuesToPoints(river_xs_intpt, DEM, river_points_elev)
    
    # Join field to join elevation value to cross-section lines
    cross_sect_fc = CrossSectionLines.split('\\')[-1]
    arcpy.JoinField_management(CrossSectionLines, 'OBJECTID', river_points_elev, 'FID_' + cross_sect_fc, ['RASTERVALU'])
    
    # Create TIN from cross-sections lines with elevation
    TIN_detrended = str(Output_gdb_filepath.parent / str(rivername + '_TIN'))
    CrossSection_path_value_table = "'" + CrossSectionLines + "'"
    sr = arcpy.Describe(DEM).spatialReference
    arcpy.ddd.CreateTin(TIN_detrended, sr, CrossSection_path_value_table + " RASTERVALU Hard_Line OBJECTID", "DELAUNAY")
    
    # Convert TIN to detrended raster
    Raster_detrended = str(Output_gdb_filepath / str(rivername + '_detrended'))
    arcpy.ddd.TinRaster(TIN_detrended, Raster_detrended, "FLOAT", "LINEAR", "OBSERVATIONS", 1, 250)
    
    # Resample detrended raster to match the cell size of the DEM and snap to DEM raster
    Raster_detrend_res = str(Output_gdb_filepath / str(rivername + '_detrend_res'))
    DEM_cellsize_X = float(str(arcpy.GetRasterProperties_management (DEM, "CELLSIZEX")))
    DEM_cellsize_Y = float(str(arcpy.GetRasterProperties_management (DEM, "CELLSIZEY")))
    DEM_cellsize = str(DEM_cellsize_X) + ' ' + str(DEM_cellsize_Y)
    
    # Set Snap Raster environment
    arcpy.env.snapRaster = DEM
    
    arcpy.management.Resample(Raster_detrended, Raster_detrend_res, DEM_cellsize, "BILINEAR")
    
    # Create Relative Elevation Model
    relative_elevation_model = str(str(Output_gdb_filepath / str(rivername + '_RelElevModel')))
    REM = arcpy.sa.Minus(DEM, Raster_detrend_res)
    REM.save(relative_elevation_model)
    