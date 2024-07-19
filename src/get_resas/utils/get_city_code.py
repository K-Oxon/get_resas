from pathlib import Path

import pandas as pd


def get_city_code() -> list[tuple[str, str]]:
    """
    都道府県コードと市町村コードの組み合わせを出力
    """
    csv_path = Path(__file__).parent / "data" / "mst_cities.csv"
    cities = pd.read_csv(csv_path, dtype={"prefCode": str, "cityCode": str})
    return list(zip(cities["prefCode"], cities["cityCode"]))
