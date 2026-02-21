import json
from pathlib import Path

from countries.queries_countries import (
    ID,
    NAME,
    POPULATION,
    CONTINENT,
    CAPITAL,
    GDP,
    AREA,
    FOUNDED,
    PRESIDENT,
    FLAG_COLOR,
    LANGUAGE,
    CLIMATE,
    create,
)

BASE_DIR = Path(__file__).resolve().parent.parent
COUNTRIES_PATH = BASE_DIR / "data" / "bkup" / "countries.json"

def main():
    if COUNTRIES_PATH.open():
        with COUNTRIES_PATH.open() as f:
            countries = json.load(f)
    
    for record in countries:
        country_info = {}
        country_info[ID] = record["ID"]
        country_info[NAME] = record["NAME"]
        country_info[POPULATION] = record["POPULATION"]
        country_info[CONTINENT] = record["CONTINENT"]
        country_info[CAPITAL] = record["CAPITAL"]
        country_info[GDP] = record["GDP"]
        country_info[AREA] = record["AREA"]
        country_info[FOUNDED] = record["FOUNDED"]
        country_info[PRESIDENT] = record["PRESIDENT"]
        country_info[FLAG_COLOR] = record["FLAG_COLOR"]
        country_info[LANGUAGE] = record["LANGUAGE"]
        country_info[CLIMATE] = record["CLIMATE"]
        create(country_info)
        print(country_info)
       
if __name__ == "__main__":
    main()



