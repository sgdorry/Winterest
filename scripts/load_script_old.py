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

FIELDS = [
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
    CLIMATE
    ]

def load_country(record: dict) -> dict:
    country_info = {}
    for field in FIELDS:
        country_info[field] = record.get(field.upper())
    return country_info


def main():

    if not COUNTRIES_PATH.exists():
        print(f"[ERROR] file not found: {COUNTRIES_PATH}")
        return

    with COUNTRIES_PATH.open() as f:
        countries = json.load(f)

    for record in countries:
            try:
                country_info = load_country(record)
                data_missing = []
                for field, data in country_info.items():
                    if data is None:
                        data_missing.append(field)

                if data_missing:
                    print(f"[WARNING] {record.get('NAME')} is missing fields: {data_missing}")

                create(country_info)
                print(f"Successfully inserted: {country_info}")

            except Exception as e:
                print(f"[ERROR] Failed to insert {record.get('NAME')}: {e}")
       
if __name__ == "__main__":
    main()



