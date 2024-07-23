from pathlib import Path

import pandas as pd


def get_secondary_medical_code() -> list[tuple[str, str]]:
    """
    都道府県コードと二次医療コードの組み合わせを出力
    """
    csv_path = Path(__file__).parent / "data" / "mst_secondary_medical_code_list.csv"
    df = pd.read_csv(csv_path, dtype=str)
    # 二次医療圏の頭2桁を使用
    df["pref_code"] = df["secondary_medical_code"].str[0:2]
    # pref_codeとsecondary_medical_codeの組み合わせでユニークにする
    df_unique_code = df.drop_duplicates(subset=["pref_code", "secondary_medical_code"])
    return list(
        zip(df_unique_code["pref_code"], df_unique_code["secondary_medical_code"])
    )


if __name__ == "__main__":
    secondary_medical_code_list = get_secondary_medical_code()
    print(secondary_medical_code_list)
    print(len(secondary_medical_code_list))
