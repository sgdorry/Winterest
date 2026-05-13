import pytest
import data.geolocation as geo

def test_abc_base():
    with pytest.raises(TypeError):
        geo.GeoLocation(0.0, 0.0)

def test_construct_valid_coordinate():
    coord = geo.Coordinate(*geo.TEST_COORD_NYC)
    assert isinstance(coord, geo.Coordinate)

def test_construct_london():
    coord = geo.Coordinate(*geo.TEST_COORD_LONDON)
    assert isinstance(coord, geo.Coordinate)

def test_construct_boundary_values():
    coord = geo.Coordinate(*geo.TEST_COORD_BOUNDARY)
    assert isinstance(coord, geo.Coordinate)

def test_construct_bad_lat_type():
    with pytest.raises(TypeError):
        geo.Coordinate("40.0", -74.0)

def test_construct_bad_lon_type():
    with pytest.raises(TypeError):
        geo.Coordinate(40.0, None)

def test_construct_lat_too_high():
    with pytest.raises(ValueError):
        geo.Coordinate(91.0, 0.0)

def test_construct_lat_too_low():
    with pytest.raises(ValueError):
        geo.Coordinate(-91.0, 0.0)

def test_construct_lon_too_high():
    with pytest.raises(ValueError):
        geo.Coordinate(0.0, 181.0)

def test_construct_lon_too_low():
    with pytest.raises(ValueError):
        geo.Coordinate(0.0, -181.0)

def test_construct_equator():
    coord = geo.Coordinate(0.0, 0.0)
    assert isinstance(coord, geo.Coordinate)

def test_str_representation():
    coord = geo.Coordinate(*geo.TEST_COORD_NYC)
    assert str(coord) == '(40.7128, -74.006)'

def test_int_inputs_accepted():
    coord = geo.Coordinate(40, -74)
    assert isinstance(coord, geo.Coordinate)