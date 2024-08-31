from pathlib import Path

import pandas as pd


def get_ltc_service_category() -> list[tuple[str, str]]:
    """介護サービス種の大分類と中分類コードの組み合わせを出力
    1,在宅サービス,118,地域密着型通所介護 だけ値が返ってこないので除く

    Returns:
        list[tuple[str, str]]: 大分類と中分類コードの組み合わせ
    """
    csv_path = Path(__file__).parent / "data" / "mst_ltc_service_category_list.csv"
    df = pd.read_csv(csv_path, dtype=str)
    df = df[df["middle_category_cd"] != "118"]
    return list(
        zip(
            df["broad_category_cd"],
            df["middle_category_cd"],
        )
    )
