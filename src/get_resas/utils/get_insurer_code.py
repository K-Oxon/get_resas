from pathlib import Path

import pandas as pd


def get_insurer_code() -> list[tuple[str, str, str]]:
    """
    都道府県コードと市町村コードと保険者コードの組み合わせを出力
    """
    csv_path = Path(__file__).parent / "data" / "mst_insurer_code_list.csv"
    insurers = pd.read_csv(csv_path, dtype=str)
    return list(
        zip(insurers["prefCode"], insurers["cityCode"], insurers["insurerCode"])
    )
