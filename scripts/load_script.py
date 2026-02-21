import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "bkup" / "countries.json"

def main():
    if INPUT_PATH.open():
        with INPUT_PATH.open() as f:
            countries = json.load(f)
    
    for record in countries.items():
        name = record["NAME"]
        population = record["POPULATION"]
        continent = record["CONTINENT"]
        capital = record["CAPITAL"]
        gdp = record["GDP"]
        area = record["AREA"]
        founded = record["FOUNDED"]
        president = record["PRESIDENT"]
        flag_color = record["FLAG_COLOR"]
        language = record["LANGUAGE"]
        climate = record["CLIMATE"]
        
        query = f"{name}, {population}, {continent}, {capital}, {gdp}, {area}, {founded}, {president}, {flag_color}, {language}, {climate}"

        print("Countries:", query)
        time.sleep(1)  # respect Nominatim rate limits

    with OUTPUT_PATH.open("w") as f:
        json.dump(countries, f, ensure_ascii=True, indent=2)
        
if __name__ == "__main__":
    main()