from hypothesis import given
from hypothesis.strategies import composite, integers
from mercantile import Tile


from montilecarlo.tiles import MonteCarloTiles


@composite
def tiles(draw):
    """Return a Mercator Tile with maximum zoom level 10"""
    z = draw(integers(min_value=1, max_value=10))
    x = draw(integers(min_value=0, max_value=2 ** z - 1))
    y = draw(integers(min_value=0, max_value=2 ** z - 1))
    return Tile(x, y, z)


def expected_xy_limits(bounding_tile, child_depth, tile_buffer):
    """Expected limits"""
    minx = bounding_tile.x * (2 ** child_depth) - tile_buffer
    maxx = minx + 2 ** child_depth - 1 + 2 * tile_buffer
    miny = bounding_tile.y * (2 ** child_depth) - tile_buffer
    maxy = miny + 2 ** child_depth - 1 + 2 * tile_buffer
    return (minx, maxx, miny, maxy)


# TODO: consolidate duplicate code, meanwhile watch for failures due
# to accidentally edited expectations.

@given(tiles(), integers(min_value=0, max_value=8),
       integers(min_value=0, max_value=10))
def test_generate_random_tiles_with_corners(bounding_tile, child_depth,
                                            tile_buffer):
    """Randomly sampled tiles with corners included"""

    # These are our invariants.
    minx, maxx, miny, maxy = expected_xy_limits(bounding_tile, child_depth,
                                                tile_buffer)

    zoom = bounding_tile.z + child_depth
    mct = MonteCarloTiles(bounding_tile, zoom, tilebuffer=tile_buffer)
    tiles = mct.generate_tiles()

    # Assert x invariants hold.
    assert (tiles[:, 0] >= minx).all()
    assert (tiles[:, 0] <= maxx).all()
    assert tiles[:, 0].min() == minx
    assert tiles[:, 0].max() == maxx

    # Assert y invariants hold.
    assert (tiles[:, 1] >= miny).all()
    assert (tiles[:, 1] <= maxy).all()
    assert tiles[:, 1].min() == miny
    assert tiles[:, 1].max() == maxy

    # Assert z values.
    assert (tiles[:, 2] == zoom).all()


@given(tiles(), integers(min_value=1, max_value=8),
       integers(min_value=0, max_value=10))
def test_generate_boxed_tiles_with_corners(bounding_tile, child_depth,
                                           tile_buffer):
    """Semi-randomly sampled tiles with corners included"""

    # These are our invariants.
    minx, maxx, miny, maxy = expected_xy_limits(bounding_tile, child_depth,
                                                tile_buffer)

    zoom = bounding_tile.z + child_depth
    mct = MonteCarloTiles(bounding_tile, zoom, tilebuffer=tile_buffer)
    tiles = mct.generate_tiles(method='boxed')

    # Assert x invariants hold.
    assert (tiles[:, 0] >= minx).all()
    assert (tiles[:, 0] <= maxx).all()
    assert tiles[:, 0].min() == minx
    assert tiles[:, 0].max() == maxx

    # Assert y invariants hold.
    assert (tiles[:, 1] >= miny).all()
    assert (tiles[:, 1] <= maxy).all()
    assert tiles[:, 1].min() == miny
    assert tiles[:, 1].max() == maxy

    # Assert z values.
    assert (tiles[:, 2] == zoom).all()


@given(tiles(), integers(min_value=0, max_value=8),
       integers(min_value=0, max_value=10))
def test_generate_random_tiles_without_corners(bounding_tile, child_depth,
                                               tile_buffer):
    """Randomly sampled tiles with corners not necessarily included"""

    # These are our invariants.
    minx, maxx, miny, maxy = expected_xy_limits(bounding_tile, child_depth,
                                                tile_buffer)

    zoom = bounding_tile.z + child_depth
    mct = MonteCarloTiles(bounding_tile, zoom, tilebuffer=tile_buffer)
    tiles = mct.generate_tiles(corners=False)

    # Assert x invariants hold.
    assert (tiles[:, 0] >= minx).all()
    assert (tiles[:, 0] <= maxx).all()

    # Assert y invariants hold.
    assert (tiles[:, 1] >= miny).all()
    assert (tiles[:, 1] <= maxy).all()

    # Assert z values.
    assert (tiles[:, 2] == zoom).all()

