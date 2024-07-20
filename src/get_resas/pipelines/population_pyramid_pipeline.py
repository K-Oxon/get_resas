"""
TODO:
いくつかのデータに欠損有り
市町村によってはyear_left__yearがnullが返ってくるため
"""

import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.population_pyramid import (
    PopulationPyramidRequest,
    PopulationPyramidResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_population_pyramid",
    primary_key=["pref_code", "city_code", "year"],
    write_disposition="merge",
)
def get_population_pyramid_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = PopulationPyramidRequest.generate_req_model_list()
    logger.info(f"req_model_list: {len(req_model_list)}")  # 27000
    response = api_client.fetch_iter(
        request_models=req_model_list[2000:7000],  # 多すぎないように調整
        with_params=True,
        exclude_params_keys=[
            "yearLeft",
            "yearRight",
        ],  # レスポンスのキーが上書きされてしまうので除外
        response_model=PopulationPyramidResponse,
    )
    yield response


def get_population_pyramid_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="population_pyramid",
        destination="bigquery",
        # dataset_name=dlt.config.value,
        dataset_name="dl_localgov_kpi_database",
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_population_pyramid_job)
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    get_population_pyramid_pipeline()
    # data = get_population_pyramid_job()
    # print(list(data))
