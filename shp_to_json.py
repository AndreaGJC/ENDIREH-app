from urllib.request import urlopen
import json
import geopandas as gpd
import numpy as np

# Cargar el shapefile
map_df = gpd.read_file('data/raw/MGN/00ent.shp')

# 3. Exportar como GeoJSON con encoding UTF-8
map_df.to_file("data/raw/MGN/00ent.json", driver='GeoJSON', encoding='utf-8')

#Leerlo con geopandas
map_df = gpd.read_file("data/raw/MGN/00ent.json")

map_df.crs = """
PROJCS["MEXICO_ITRF_2008_LCC",
    GEOGCS["MEXICO_ITRF_2008",
        DATUM["D_ITRF_2008",
            SPHEROID["GRS_1980",6378137.0,298.257222101]
        ],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]
    ],
    PROJECTION["Lambert_Conformal_Conic"],
    PARAMETER["False_Easting",2500000.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",-102.0],
    PARAMETER["Standard_Parallel_1",17.5],
    PARAMETER["Standard_Parallel_2",29.5],
    PARAMETER["Latitude_Of_Origin",12.0],
    UNIT["Meter",1.0]
]
"""

# Reproyecta a WGS84 (lat/lon)
map_df = map_df.to_crs(epsg=4326)

# Verificar que las coordenadas sean lat-lon
print(map_df.geometry.head())

# Ahora si guardarlo como Json
map_df.geometry = map_df.geometry.simplify(tolerance=0.001)  # Ajusta la tolerancia
map_df.to_file("data/raw/MGN/00ent.json", driver="GeoJSON")

print(f"Archivo GeoJSON exportado con éxito")
