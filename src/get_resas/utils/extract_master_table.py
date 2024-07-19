"""
htmlのtableに直接書かれているマスター系の取得
ヘッダーは手動でsnake_caseの英名に変換する

TODO:
  - Warningが出てるのでStringIOを使った方がいいらしい
    `dfs = pd.read_html(StringIO(html_str))`
"""

from pathlib import Path

import pandas as pd


def main(
    url: str,
    output_path: str | Path,
    target_table_order: int,
    header_name_map: dict | None = None,
) -> None:
    df = pd.read_html(url, encoding="utf-8")[target_table_order]
    converters = {c: lambda x: str(x) for c in df.columns}
    df = pd.read_html(url, encoding="utf-8", converters=converters)[target_table_order]
    df.rename(columns=header_name_map, inplace=True)
    print(df.head())
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")


OUTPUT_BASE_PATH = Path(__file__).parent / "data"

HEADER_NAME_MAP_MST_INSURER = {
    "都道府県コード": "prefCode",
    "都道府県名": "prefName",
    "市区町村コード": "cityCode",
    "市区町村名": "cityName",
    "保険者コード": "insuranceCode",
    "保険者名": "insurerName",
}

HEADER_NAME_MAP_MST_LTC_SERVICE_CATEGORY = {
    # APIのparameter名と揃えている
    "大分類コード": "broad_category_cd",
    "大分類名": "broad_category_name",
    "中分類コード": "middle_category_cd",
    "中分類名": "middle_category_name",
}

EXTRACT_CONFIG: list[dict] = [
    {
        "url": "https://opendata.resas-portal.go.jp/docs/api/v1/codes/insurance.html",
        "output_path": OUTPUT_BASE_PATH / "mst_insurer_code_list.csv",
        "target_table_order": 0,
        "header_name_map": HEADER_NAME_MAP_MST_INSURER,
    },
    {
        # 分類コード（介護需給） 介護サービス種
        "url": "https://opendata.resas-portal.go.jp/docs/api/v1/codes/medicalWelfareCareAnalysis.html",
        "output_path": OUTPUT_BASE_PATH / "mst_ltc_service_category_list.csv",
        "target_table_order": 0,
        "header_name_map": HEADER_NAME_MAP_MST_LTC_SERVICE_CATEGORY,
    },
    {
        # 分類コード（介護需給） 要介護度区分
        "url": "https://opendata.resas-portal.go.jp/docs/api/v1/codes/medicalWelfareCareAnalysis.html",
        "output_path": OUTPUT_BASE_PATH / "mst_ltc_required_class_list.csv",
        "target_table_order": 2,
        "header_name_map": HEADER_NAME_MAP_MST_LTC_SERVICE_CATEGORY,
    },
]

if __name__ == "__main__":
    for config in EXTRACT_CONFIG:
        main(
            config["url"],
            config["output_path"],
            config["target_table_order"],
            config["header_name_map"],
        )
