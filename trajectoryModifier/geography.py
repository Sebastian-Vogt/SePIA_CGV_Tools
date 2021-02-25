import math

import rasterio
from pyproj import Transformer, CRS
from scipy.interpolate import interp2d
import time

R_earth = 6378100


class GeoHandler:
    def __init__(self, elevation_paths=[]):
        self.datasets = [rasterio.open(path) for path in elevation_paths]
        start = time.process_time()
        elevations = [ds.read(1) for ds in self.datasets]
        end = time.process_time()
        print("Read: "+str(end-start))
        xs = [[ds.bounds.left + x * (1 / ds.width) for x in range(ds.width)] for ds in self.datasets]
        ys = [[ds.bounds.top - y * (1 / ds.height) for y in range(ds.height)] for ds in self.datasets]
        start = time.process_time()
        self.ds_interpolations = [interp2d(x, y, z, kind="quintic") for x, y, z in zip(xs, ys, elevations)]
        end = time.process_time()
        print("Interpolation: "+str(end-start))
        self.d2m = Transformer.from_crs(CRS("EPSG:4326"), CRS("EPSG:32633"))  # 3394 or 3857 or 2545
        self.m2d = Transformer.from_crs(CRS("EPSG:32633"), CRS("EPSG:4326"))

    def get_elevation(self, lat, long):
        for ds, inter in zip(self.datasets, self.ds_interpolations):
            if lat < ds.bounds.bottom or lat > ds.bounds.top or long < ds.bounds.left or long > ds.bounds.right:
                continue
            else:
                return inter(long, lat)[0]
        raise UserWarning("No elevation data available.")

    def rel_lat_long(self, original_lat, original_long, d_lat, d_long):
        d_lat_deg = math.copysign(math.degrees(math.atan(abs(d_lat) / R_earth)), d_lat)
        d_long_deg = math.copysign(math.degrees(math.atan(abs(d_long) / R_earth)), d_long)
        lat = original_lat + d_lat_deg
        long = original_long + d_long_deg
        return lat, long

    def lat_long_to_meter(self, lat, long):
        x, y = self.d2m.transform(lat, long)
        return x, y

    def meter_to_lat_long(self, x, y):
        lat, long = self.m2d.transform(x, y)
        return lat, long
