from io import BytesIO
import logging

from PIL.WebPImagePlugin import WebPImageFile
from PIL.JpegImagePlugin import JpegImageFile
import numpy as np

from montilecarlo.async_get import process_urls


log = logging.getLogger(__name__)


drivers = {'jpg': JpegImageFile, 'webp': WebPImageFile}


def load_tile(contents, fmt='webp'):
    """Read webp tile bytes to an ndarray."""
    # If contents is not WebP, this will raise SyntaxError.
    if not contents:
        raise ValueError("Empty contents can't be loaded.")
    with BytesIO(contents) as src:
        return np.array(drivers[fmt](src))[:, :, :3]


def process_tiles(tiles, access_token, calculators, fmt='webp', mapid='mapbox.satellite'):
    """Yields (tile, result * calculators) tuples"""
    for tile, (url, contents) in zip(tiles, process_urls(
            make_urls(tiles, access_token, fmt=fmt, mapid=mapid), concurrent=5, pause=0.1)):
        try:
            img = load_tile(contents, fmt=fmt)
            yield tile, [f(img) for f in calculators]
            log.debug("Processed tile: %r, URL: %r", tile, url)
        except SyntaxError:
            log.warn("Contents of tile %r are not %r encoded: %r",
                     url, fmt, contents[:20])
        except ValueError:
            log.warn("Non-existent tile %r", url)


def make_urls(tiles, access_token, mapid='mapbox.satellite', fmt='webp'):
    base_url = ('https://a.tiles.mapbox.com/v4/{0}'
                '/{{2}}/{{0}}/{{1}}.{2}?access_token={1}').format(
                    mapid, access_token, fmt)
    for t in tiles:
        yield base_url.format(*t)
