from pathlib import Path

import pandas as pd


def get_medical_injury_classification() -> list[tuple[str, str]]:
    """傷病分類の大分類と中分類コードの組み合わせを出力
    https://opendata.resas-portal.go.jp/docs/api/v1/codes/medicalWelfareMedicalAnalysis.html#injuries

    04,内分泌，栄養及び代謝疾患,044,その他の内分泌，栄養及び代謝疾患
    は結果が返ってこないので除く

    Returns:
        list[tuple[str, str]]: 大分類と中分類コードの組み合わせ
    """
    csv_path = Path(__file__).parent / "data" / "mst_medical_injury_classification.csv"
    df = pd.read_csv(csv_path, dtype=str)
    df = df[df["middleCategoryCode"] != "044"]

    return list(
        zip(
            df["broadCategoryCode"],
            df["middleCategoryCode"],
        )
    )
