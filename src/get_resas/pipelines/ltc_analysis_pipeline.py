from typing import Iterator

import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.ltc_analysis import (
    LtcAnalysisRequest,
    LtcAnalysisResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_ltc_analysis_city",
    table_name="resas_ltc_analysis_city",
    primary_key=[
        "disp_type",
        "matter2",
        "broad_category_code",
        "middle_category_code",
        "year",
        "prefecture_cd",
        "municipality_cd",
        "insurance_cd",
        "code",
    ],
    write_disposition="merge",
)
def get_ltc_analysis_job_city(matter_2: int) -> Iterator[any]:
    """市町村単位のデータ取得(地域単位ごとにテーブルを分ける)

    Args:
        matter_2 (int): 表示内容(中分類)
    Returns:
        Iterator[any]: LtcAnalysisResponse.result
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = LtcAnalysisRequest.generate_req_model_list(matter_2=matter_2)
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=req_model_list[10000:14000],
        with_params=False,  # responseに含まれるので不要
        response_model=LtcAnalysisResponse,
    )
    yield response


@dlt.resource(
    name="resas_ltc_analysis_insurer",
    table_name="resas_ltc_analysis_insurer",
    primary_key=[
        "disp_type",
        "matter2",
        "broad_category_code",
        "middle_category_code",
        "year",
        "prefecture_cd",
        "municipality_cd",
        "insurance_cd",
        "code",
    ],
    write_disposition="merge",
)
def get_ltc_analysis_job_insurer(matter_2: int) -> Iterator[any]:
    """保険会社単位のデータ取得

    Args:
        matter_2 (int): 表示内容(中分類)

    Returns:
        Iterator[any]: LtcAnalysisResponse.result
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = LtcAnalysisRequest.generate_req_model_list_by_insurer(
        matter_2=matter_2
    )
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=req_model_list[0:4000],
        with_params=False,  # responseに含まれるので不要
        response_model=LtcAnalysisResponse,
    )
    yield response


def load_ltc_analysis_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="ltc_analysis",
        destination="bigquery",
        # dataset_name=dlt.config.value,
        dataset_name="dl_localgov_kpi_database",
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(
        [
            # get_ltc_analysis_job_city(matter_2=201),
            get_ltc_analysis_job_city(matter_2=202),
            # get_ltc_analysis_job_insurer(matter_2=102),
            # get_ltc_analysis_job_insurer(matter_2=301),
            # get_ltc_analysis_job_insurer(matter_2=302),
        ]
    )
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    load_ltc_analysis_pipeline()
    # data = get_ltc_analysis_job_city(matter_2=201)
    # print(list(data))
