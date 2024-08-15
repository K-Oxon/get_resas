import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.medical_analysis import (
    MedicalAnalysisRequest,
    MedicalAnalysisResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_medical_analysis",
    table_name="resas_medical_analysis",
    primary_key=[
        "disp_type",
        "matter2",
        "broad_category_code",
        "middle_category_code",
        "year",
        "prefecture_cd",
        "municipality_cd",
        "secondary_medical_cd",
    ],
    write_disposition="merge",
)
def get_medical_analysis_job(matter2: int):
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = MedicalAnalysisRequest.generate_req_model_list(matter2=matter2)
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=False,  # responseに含まれるので不要
        response_model=MedicalAnalysisResponse,
    )
    yield response


@dlt.resource(
    name="resas_medical_analysis_secondary_medical_area",
    table_name="resas_medical_analysis_secondary_medical_area",
    write_disposition="replace",
)
def get_medical_analysis_secondary_medical_area_job(matter2: int):
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = (
        MedicalAnalysisRequest.generate_req_model_list_secondary_medical_code(
            matter2=matter2
        )
    )
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=False,
        response_model=MedicalAnalysisResponse,
    )
    yield response


def get_medical_analysis_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="medical_analysis",
        destination="bigquery",
        dataset_name=dlt.config["destination.bigquery.dataset_name"],
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(
        [
            get_medical_analysis_job(matter2=201),
            get_medical_analysis_job(matter2=202),
            get_medical_analysis_job(matter2=203),
            # get_medical_analysis_job(matter2=204),
            # get_medical_analysis_job(matter2=205),
            # get_medical_analysis_job(matter2=206),
            # get_medical_analysis_job(matter2=208),
            # get_medical_analysis_secondary_medical_area_job(matter2=102),
        ]
    )
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    get_medical_analysis_pipeline()
    # data = get_medical_analysis_job()
    # print(list(data))
