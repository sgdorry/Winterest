from copy import deepcopy
from unittest.mock import patch
import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import queries_countries as qry

def create_temp_country():
    return deepcopy(qry.SAMPLE_COUNTRY)

@pytest.fixture(scope='function')
def temp_country():
    temp_county = create_temp_country()
    new_id = qry.create(create_temp_country())
    yield new_id
    try:
        qry.delete(new_id)
    except ValueError:
        print('The record has already been deleted.')

def test_create_bad_name():
    old_count = qry.num_countries()  #current count of countries
    with pytest.raises(Exception):
        qry.create(None)
    #ensuring no invalid country was created
    assert qry.num_countries() == old_count

def test_create_bad_population():
    old_count = qry.num_countries()  #current count of countries
    with pytest.raises(Exception):
        qry.create({
            'name': 'Test Country',
            'population': 'not a number',
            'continent': 'Europe',
            'capital': 'Test City',
            'gdp': '1.2 T',
            'area': '1000 sq mi',
            'founded': '1900',
            'president': 'Test Person'
        })
    #ensuring no invalid country was created
    assert qry.num_countries() == old_count

def test_create_bad_capital():
    old_count = qry.num_countries()  #current count of countries
    with pytest.raises(Exception):
        #try creating a country with an int as the value for capital
        qry.create({'name': 'United States of America', 'population': 100 , 'continent': 'North America', 'capital': 45, 'gdp': '1.2 T', 'area': '1000 sq mi', 'founded': '1900', 'president': 'Test Person'})
    assert qry.num_countries() == old_count 

def test_create_bad_president():
    old_count = qry.num_countries()  #current count of countries
    with pytest.raises(Exception):
        #try creating a country with an int as the value for president
        qry.create({'name': 'United States of America', 'population': 100 , 'continent': 'North America', 'capital': 'DC', 'gdp': '1.2 T', 'area': '1000 sq mi', 'founded': '1900', 'president': 55})
    assert qry.num_countries() == old_count

def test_create_bad_gdp():
    old_count = qry.num_countries()  #current count of countries
    with pytest.raises(Exception):
        #try creating a country with an int as the value for gdp
        qry.create({'name': 'United States of America', 'population': 100 , 'contentient': 'North America', 'capital': 'DC', 'gdp': 12000000, 'area': '1000 sq mi', 'founded': '1900', 'president': 'Test Person'})
    assert qry.num_countries() == old_count

def test_create_bad_area():
    old_count = qry.num_countries()  #current count of countries
    with pytest.raises(Exception):
        #try creating a country with an int as the value for area
        qry.create({'name': 'United States of America', 'population': 100 , 'contentient': 'North America', 'capital': 'DC', 'gdp': '1.2 T', 'area': 3810000, 'founded': '1900', 'president': 'Test Person'})
    assert qry.num_countries() == old_count

def test_create_bad_flag_color():
    old_count = qry.num_countries() #current count of counties
    with pytest.raises(Exception):
        #try creating a country with an int value for flag color
        qry.create({'name': 'United States of America', 'population': 100 , 'contentient': 'North America', 'capital': 'DC', 'gdp': '1.2 T', 'area': 3810000, 'founded': '1900', 'president': 'Test Person', 'flag_color': 999})
    assert qry.num_countries() == old_count