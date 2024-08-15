from pathlib import Path

import dlt
import pandas as pd

from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)
CSV_BASE_DIR = Path(__file__).parent.parent / "utils" / "data"
table_mapping = [
    {
        "table_name": "mst_insurer_code_list",
        "csv_path": CSV_BASE_DIR / "mst_insurer_code_list.csv",
    },
    {
        "table_name": "mst_ltc_required_class_list",
        "csv_path": CSV_BASE_DIR / "mst_ltc_required_class_list.csv",
    },
    {
        "table_name": "mst_ltc_service_category_list",
        "csv_path": CSV_BASE_DIR / "mst_ltc_service_category_list.csv",
    },
]


@dlt.source
def get_common_master_source():
    def get_master_table(csv_path: Path):
        if not csv_path.exists():
            raise FileNotFoundError(f"File not found: {csv_path}")
        # 全て文字列で読む
        return pd.read_csv(csv_path, dtype=str)

    # mappingごとにテーブル(dlt.resource)を作成する
    for table in table_mapping:
        yield dlt.resource(
            get_master_table(table["csv_path"]),
            name=table["table_name"],
            table_name=table["table_name"],
            write_disposition="replace",
        )


def load_common_master_tables():
    pipeline = dlt.pipeline(
        pipeline_name="common_master_tables",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
    )
    load_info = pipeline.run(get_common_master_source())
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    # 確認用
    # for table in table_mapping:
    #     print(table["csv_path"], table["csv_path"].exists())
    # data = get_common_master_source()
    # print(list(data)[0])

    # ロード
    load_common_master_tables()
