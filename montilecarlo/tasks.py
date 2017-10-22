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
