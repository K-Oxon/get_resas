from pathlib import Path

import pandas as pd


def get_industries_code() -> list[tuple[str, str]]:
    """
    産業大分類コードと中分類コードの組み合わせを出力
    """
    csv_path = Path(__file__).parent / "data" / "mst_industries.csv"
    industries = pd.read_csv(csv_path, dtype={"simc_code": str, "sic_code": str})
    return list(zip(industries["sic_code"], industries["simc_code"]))
