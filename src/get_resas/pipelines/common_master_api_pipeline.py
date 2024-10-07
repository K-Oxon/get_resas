from typing import Iterator

import dlt
from dlt.extract.resource import DltResource
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources

from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.source
def get_common_master_api_source() -> Iterator[DltResource]:
    """
    共通マスタ取得
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://opendata.resas-portal.go.jp/api/v1/",
            "headers": {
                "X-API-KEY": API_KEY,
            },
        },
        "resource_defaults": {
            "endpoint": {
                "data_selector": "result",
            },
            "write_disposition": "replace",
        },
        "resources": [
            {
                "name": "industries_broad",
                "table_name": "resas_industries_broad",
                "endpoint": {
                    "path": "industries/broad",
                },
            },
            {
                "name": "industries_middle",
                "table_name": "resas_industries_middle",
                "endpoint": {
                    "path": "industries/middle?sicCode={sicCode}",
                    "params": {
                        "sicCode": {
                            "type": "resolve",
                            "resource": "industries_broad",
                            "field": "sicCode",
                        },
                    },
                },
            },
        ],
    }

    yield from rest_api_resources(config)


def load_common_master_api_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="common_master_api",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_common_master_api_source())
    logger.info(load_info)
    return pipeline


if __name__ == "__main__":
    load_common_master_api_pipeline()
