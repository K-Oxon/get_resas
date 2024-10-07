import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.wages_by_age_industry import (
    WagesByAgeIndustryRequest,
    WagesByAgeIndustryResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_wages_by_age_industry_pref",
    table_name="resas_wages_by_age_industry_pref",
    primary_key=["prefCode", "simcCode", "wagesAge"],
    write_disposition="merge",
)
def get_wages_by_age_industry_pref_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = WagesByAgeIndustryRequest.generate_req_model_list()
    logger.info(f"len(req_model_list): {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=req_model_list[40000:45000],
        with_params=True,
        exclude_params_keys=["prefCode", "sicCode", "simcCode"],
        response_model=WagesByAgeIndustryResponse,
    )
    yield response


def load_wages_by_age_industry_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="wages_by_age_industry",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_wages_by_age_industry_pref_job)
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    load_wages_by_age_industry_pipeline()

    # data = get_wages_by_age_industry_pref_job()
    # print(list(data))
