from pathlib import Path

import pandas as pd

OUTPUT_BASE_PATH = Path(__file__).parent / "data"


def main():
    # データ取得
    df = pd.read_excel(
        "https://data.e-gov.go.jp/data/uploads/resource/%E4%BA%8C%E6%AC%A1%E5%8C%BB%E7%99%82%E5%9C%8F.xlsx",
        sheet_name="二次医療圏",
        header=4,
        usecols=[1, 2, 3, 4, 5],
        dtype=str,
    )
    print(df.head())
    print("============")
    # カラム名を変更
    df.columns = [
        "pref_name",
        "secondary_medical_code",
        "secondary_medical_name",
        "city_code",
        "city_name",
    ]
    # 謎の全角スペースを除去
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    print(df.head())
    df.to_csv(OUTPUT_BASE_PATH / "mst_secondary_medical_code_list.csv", index=False)


if __name__ == "__main__":
    main()
