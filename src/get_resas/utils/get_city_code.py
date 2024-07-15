import pandas as pd


def get_city_code() -> list[str]:
    cities = pd.read_csv("cities.csv")
    return cities["cityCode"].tolist()
