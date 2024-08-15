import sys
from typing import Any, Callable, Iterator

import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.population_natural import (
    PopulationNaturalRequest,
    PopulationNaturalResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


def default_slicer(lst: list) -> list:
    """何もしない関数"""
    return lst


@dlt.resource(
    name="resas_population_natural",
    table_name="resas_population_natural",
    primary_key=["pref_code", "city_code", "age_from", "age_to"],
    write_disposition="merge",
)
def get_population_natural_job(
    slicer: Callable[[list], list] = default_slicer,
) -> Iterator[Any]:
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = PopulationNaturalRequest.generate_req_model_list()
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=slicer(req_model_list),
        with_params=True,
        response_model=PopulationNaturalResponse,
    )
    yield response


def load_population_natural_pipeline(jobs: list[Callable[[list[Any]], Iterator[Any]]]):
    pipeline = dlt.pipeline(
        pipeline_name="population_natural",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(jobs)
    logger.info(load_info)
    return load_info


if __name__ == "__main__":

    def batch_slicer(start: int, end: int) -> Callable[[list], list]:
        return lambda lst: lst[start:end]

    start = 0
    batch_size = 1000
    max_requests = 10000 + start
    for list_start in range(start, max_requests, batch_size):
        list_end = min(list_start + batch_size, max_requests)
        jobs = [get_population_natural_job(batch_slicer(list_start, list_end))]
        try:
            load_population_natural_pipeline(jobs)
            logger.info(f"completed: list_start: {list_start}, list_end: {list_end}")
        except Exception as e:
            logger.error(e)
            logger.error(f"failed: list_start: {list_start}, list_end: {list_end}")
            sys.exit(1)
    # data = get_population_natural_job()
    # print(list(data))
