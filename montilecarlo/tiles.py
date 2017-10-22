import logging

import affine
import mercantile

import numpy as np
from scipy.interpolate import griddata as sci_grid


log = logging.getLogger(__name__)


class MonteCarloTiles:
    """
    Use a monte-carlo type analysis to randomly sample tile data
    """
    def __init__(self, bounding_tile, zoom, tilebuffer=2):
        self.bounding_tile = bounding_tile
        self.zoom = zoom
        self.zshift = zoom - bounding_tile[-1]
        self.tileshape = 2 ** self.zshift
        self.tilebuffer = tilebuffer

        self.sampleshape = (
            self.tileshape + tilebuffer * 2, self.tileshape + tilebuffer * 2)

        self.xyzs = np.dstack(
            list(np.indices(self.sampleshape, dtype=np.int64)) +
            [np.zeros(self.sampleshape, dtype=np.int64) + self.zoom])

        # QUESTION: I think this is actuall the upper left, so should
        # be ul not ur?
        self.urxy = np.array([b * self.tileshape for b in bounding_tile[:2]])

        self.xyzs[:, :, :2] += (self.urxy)
        self.xyzs[:, :, :2] -= self.tilebuffer

    def generate_tiles(self, rate=0.25, corners=True, method='random'):
        """
        Create an array of [x, y, z] tiles based on a sampling rate
        """

        if method == 'random':
            rand_arr = np.random.rand(*self.sampleshape)

            if corners:
                rand_arr[0, 0] = 0
                rand_arr[0, -1] = 0
                rand_arr[-1, -1] = 0
                rand_arr[-1, 0] = 0

            return self.xyzs[rand_arr < rate]

        elif method == 'boxed':
            # This is an elaborate but hopefully clear way of
            # dividing a tile into n nearly equal rectangles
            # and sampling once in each rectangle. The complexity
            # comes from making sure that int rounding doesn't
            # leave gaps at the edges.

            pseudotile = np.zeros(self.sampleshape)
            tile_width, tile_height = pseudotile.shape[:2]
            n_samples = (tile_width * tile_height) * rate

            if corners:
                pseudotile[0, 0] = 1
                pseudotile[0, -1] = 1
                pseudotile[-1, -1] = 1
                pseudotile[-1, 0] = 1

            x_bins = int(n_samples ** 0.5)
            y_bins = int(n_samples / x_bins)

            right = 0
            for x_bin in range(x_bins):
                left = right
                width = int((tile_width - right) / (x_bins - x_bin))
                right = left + width

                bottom = 0
                for y_bin in range(y_bins):
                    top = bottom
                    height = int((tile_height - bottom) / (y_bins - y_bin))
                    bottom = top + height

                    rand_x = int(np.random.uniform(left, right))
                    rand_y = int(np.random.uniform(top, bottom))

                    pseudotile[rand_x, rand_y] = 1

            return self.xyzs[pseudotile > 0]

    def reinterpolate_tiles(self, tiles, sampled_var):
        """
        Given a set of sampled points, interpolate into a full
        2D array of data
        """
        grid_x, grid_y = np.mgrid[
            self.urxy[0] - self.tilebuffer:(self.urxy[0] + self.tileshape + self.tilebuffer),
            self.urxy[1] - self.tilebuffer:(self.urxy[1] + self.tileshape + self.tilebuffer)]

        grid = sci_grid(tiles[:, :2], sampled_var, (grid_x, grid_y),
                        method='nearest')

        return np.rot90(grid.reshape(self.sampleshape))[
            self.tilebuffer:self.sampleshape[0] - self.tilebuffer,
            self.tilebuffer:self.sampleshape[0] - self.tilebuffer][::-1, :]

    def get_opts(self, count):
        """Return rasterio dataset creation options for the bounding tile."""
        w, s, e, n = list(mercantile.bounds(*self.bounding_tile))

        w, s = mercantile.xy(w, s)
        e, n = mercantile.xy(e, n)

        xcell = ((e - w) / self.tileshape)
        ycell = ((n - s) / self.tileshape)

        return {
            'dtype': np.float32,
            'driver': 'GTiff',
            'height': self.tileshape,
            'width': self.tileshape,
            'count': count,
            'compress': 'lzw',
            'transform': affine.Affine(xcell, 0, w, 0, -ycell, n),
            'crs': 'epsg:3857'}

    def get_geojson(self):
        """Return geojson of the bounding tile."""
        w, s, e, n = list(mercantile.bounds(*self.bounding_tile))

        return {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [w, s],
                        [e, s],
                        [e, n],
                        [w, n],
                        [w, s]
                    ]
                ]
            }
        }

