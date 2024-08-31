import sys
from typing import Callable, Iterator

import dlt
from dlt.common.pipeline import LoadInfo

from get_resas.api_client import RESASAPIClient
from get_resas.config.ltc_analysis import (
    LtcAnalysisRequest,
    LtcAnalysisResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


def default_slicer(lst: list) -> list:
    """何もしない関数"""
    return lst


@dlt.resource(
    name="resas_ltc_analysis_pref",
    table_name="resas_ltc_analysis_pref",
    primary_key=[
        "disp_type",
        "matter2",
        "broad_category_code",
        "middle_category_code",
        "year",
    ],
    write_disposition="merge",
)
def get_ltc_analysis_job_pref(
    matter_2: int, slicer: Callable[[list], list] = default_slicer
) -> Iterator[any]:
    """都道府県単位のデータ取得

    Args:
        matter_2 (int): 表示内容(中分類)
        slicer (Callable[[list], list], optional): リストを分割する関数. Defaults to default_slicer.

    Returns:
        Iterator[any]: LtcAnalysisResponse.result
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = LtcAnalysisRequest.generate_req_model_list_by_pref(
        matter_2=matter_2
    )
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=slicer(req_model_list),
        with_params=False,  # responseに含まれるので不要
        response_model=LtcAnalysisResponse,
    )
    yield response


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
    ],
    write_disposition="merge",
)
def get_ltc_analysis_job_city(
    matter_2: int, slicer: Callable[[list], list] = default_slicer
) -> Iterator[any]:
    """市町村単位のデータ取得(地域単位ごとにテーブルを分ける)

    Args:
        matter_2 (int): 表示内容(中分類)
        slicer (Callable[[list], list], optional): リストを分割する関数. Defaults to default_slicer.

    Returns:
        Iterator[any]: LtcAnalysisResponse.result
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = LtcAnalysisRequest.generate_req_model_list(matter_2=matter_2)
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=slicer(req_model_list),
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
    ],
    write_disposition="merge",
)
def get_ltc_analysis_job_insurer(
    matter_2: int, slicer: Callable[[list], list] = default_slicer
) -> Iterator[any]:
    """保険会社単位のデータ取得

    Args:
        matter_2 (int): 表示内容(中分類)
        slicer (Callable[[list], list], optional): リストを分割する関数. Defaults to default_slicer.

    Returns:
        Iterator[any]: LtcAnalysisResponse.result
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = LtcAnalysisRequest.generate_req_model_list_by_insurer(
        matter_2=matter_2
    )
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=slicer(req_model_list),
        with_params=False,  # responseに含まれるので不要
        response_model=LtcAnalysisResponse,
    )
    yield response


def load_ltc_analysis_pipeline(jobs: list[Callable[[int], Iterator[any]]]) -> LoadInfo:
    """パイプラインを実行する

    Args:
        jobs (list[Callable[[int], Iterator[any]]]): パイプラインのジョブ

    Returns:
        LoadInfo: ロード情報
    """
    # load to destination
    pipeline = dlt.pipeline(
        pipeline_name="ltc_analysis",
        destination="bigquery",
        staging="filesystem",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(
        jobs,
        loader_file_format="parquet",
    )
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")

    # localにもロード -> 二度APIを叩いてしまうので一旦ステイ
    # logger.debug("localにもロード")
    # pipeline_local = dlt.pipeline(
    #     pipeline_name="ltc_analysis_local",
    #     destination=filesystem(bucket_url="~/resas_api_data"),
    #     dataset_name="resas_api_data",
    # )
    # pipeline_local.run(jobs, loader_file_format="parquet")
    # logger.debug("localにもロード完了")

    return load_info


if __name__ == "__main__":

    def batch_slicer(start: int, end: int) -> Callable[[list], list]:
        return lambda lst: lst[start:end]

    start = 0  # 前回の途中から
    batch_size = 1000  # 1000件ずつloadする
    max_requests = 10000 + start  # 24時間のrate limit

    # TODO: 作りが微妙なので見直したい
    for list_start in range(start, max_requests, batch_size):
        list_end = min(list_start + batch_size, max_requests)
        jobs = [
            get_ltc_analysis_job_pref(
                matter_2=301, slicer=batch_slicer(list_start, list_end)
            ),
            get_ltc_analysis_job_pref(
                matter_2=302, slicer=batch_slicer(list_start, list_end)
            ),
            # get_ltc_analysis_job_city(
            #     matter_2=201, slicer=batch_slicer(list_start, list_end)
            # ),
            # get_ltc_analysis_job_city(
            #     matter_2=202, slicer=batch_slicer(list_start, list_end)
            # ),
            # get_ltc_analysis_job_insurer(
            #     matter_2=102, slicer=batch_slicer(list_start, list_end)
            # ),
            # get_ltc_analysis_job_insurer(
            #     matter_2=301, slicer=batch_slicer(list_start, list_end)
            # ),
            # get_ltc_analysis_job_insurer(
            #     matter_2=302, slicer=batch_slicer(list_start, list_end)
            # ),
        ]
        try:
            load_ltc_analysis_pipeline(jobs=jobs)
            logger.info(f"completed: list_start: {list_start}, list_end: {list_end}")
        except Exception as e:
            logger.error(e)
            logger.error(f"failed: list_start: {list_start}, list_end: {list_end}")
            sys.exit(1)

    # data = get_ltc_analysis_job_city(matter_2=201)
    # data = get_ltc_analysis_job_insurer(matter_2=102)
    # print(list(data))
