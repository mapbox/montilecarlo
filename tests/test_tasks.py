import json
import os
import pytest

from montilecarlo.tasks import load_tile


@pytest.fixture(scope="module")
def mapbox_satellite_001_webp_data():
    """Bytes of the mapbox.satellite 1/0/0.webp tile"""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/0-0-1.webp')
    with open(path, 'rb') as f:
        data = f.read()
    return data


def test_load_tile_success(mapbox_satellite_001_webp_data):
    """Read bytes of a webp tile"""
    assert load_tile(mapbox_satellite_001_webp_data).shape == (256, 256, 3)


@pytest.mark.xfail(reason="Truncated contents can't be loaded")
def test_load_tile_truncated(mapbox_satellite_001_webp_data):
    """Read bytes of a webp tile"""
    load_tile(mapbox_satellite_001_webp_data[:200]).shape == (256, 256, 3)


@pytest.mark.xfail(reason="JSON error message can't be loaded")
def test_load_tile_fail():
    """Fail to read bytes of a JSON file"""
    data = json.dumps({'oh': 'no'}).encode('utf-8')
    load_tile(data).shape == (256, 256, 3)
