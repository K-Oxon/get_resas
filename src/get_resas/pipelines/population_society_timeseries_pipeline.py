import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.population_society_timeseries import (
    PopulationSocietyTimeseriesRequest,
    PopulationSocietyTimeseriesResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_population_society_timeseries",
    write_disposition="replace",
)
def get_population_society_timeseries_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = PopulationSocietyTimeseriesRequest.generate_req_model_list()
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=True,
        response_model=PopulationSocietyTimeseriesResponse,
    )
    yield response


def load_population_society_timeseries_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="population_society_timeseries",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_population_society_timeseries_job)
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    load_population_society_timeseries_pipeline()
    # data = get_population_society_timeseries_job()
    # print(list(data))
