import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.population_future import (
    PopulationFutureRequest,
    PopulationFutureResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_population_future",
    table_name="resas_population_future",
    write_disposition="replace",
)
def get_population_future_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = PopulationFutureRequest.generate_req_model_list()
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=True,
        response_model=PopulationFutureResponse,
    )
    yield response


def get_population_future_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="population_future",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_population_future_job)
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    get_population_future_pipeline()
    # data = get_medical_analysis_job()
    # print(list(data))
