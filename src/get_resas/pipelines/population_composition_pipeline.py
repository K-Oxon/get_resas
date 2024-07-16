import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.population_composition import (
    PopulationCompositionRequest,
    PopulationCompositionResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="population_composition",
    write_disposition="replace",
)
def get_population_composition_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = PopulationCompositionRequest.generate_req_model_list()
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=True,
        response_model=PopulationCompositionResponse,
    )
    yield response


def get_population_composition_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="population_composition",
        destination="bigquery",
        dataset_name=dlt.config.value,
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_population_composition_job)
    logger.info(load_info)
    return load_info


if __name__ == "__main__":
    get_population_composition_pipeline()
    # data = get_population_composition_job()
    # print(list(data))
