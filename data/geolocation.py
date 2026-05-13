from abc import ABC, abstractmethod

class GeoLocation(ABC):
    @abstractmethod
    def __init__(self, lat: float, lon: float):
        pass

    def __str__(self):
        return f'({self.lat}, {self.lon})'


MIN_LAT = -90.0
MAX_LAT = 90.0
MIN_LON = -180.0
MAX_LON = 180.0


class Coordinate(GeoLocation):
    def __init__(self, lat: float, lon: float):
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise TypeError(f'Coordinates must be numbers, got lat={type(lat)}, lon={type(lon)}')
        if lat < MIN_LAT or lat > MAX_LAT:
            raise ValueError(f'Latitude must be between {MIN_LAT} and {MAX_LAT}, got {lat}')
        if lon < MIN_LON or lon > MAX_LON:
            raise ValueError(f'Longitude must be between {MIN_LON} and {MAX_LON}, got {lon}')
        self.lat = lat
        self.lon = lon


TEST_COORD_NYC = (40.7128, -74.0060)
TEST_COORD_LONDON = (51.5074, -0.1278)
TEST_COORD_BOUNDARY = (90.0, 180.0)