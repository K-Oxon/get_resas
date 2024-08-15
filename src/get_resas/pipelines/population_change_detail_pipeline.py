import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.population_change_detail import (
    PopulationChangeDetailRequest,
    PopulationChangeDetailResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_population_change_detail",
    primary_key=["pref_code", "city_code"],
    write_disposition="merge",
)
def get_population_change_detail_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = PopulationChangeDetailRequest.generate_req_model_list()
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=True,
        response_model=PopulationChangeDetailResponse,
    )
    yield response


def get_population_change_detail_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="population_change_detail",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_population_change_detail_job)
    logger.info(load_info)
    return load_info


if __name__ == "__main__":
    get_population_change_detail_pipeline()
    # data = get_population_change_detail_job()
    # print(list(data))
