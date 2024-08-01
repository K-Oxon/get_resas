import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.medical_patient_flow import (
    MedicalPatientFlowRequest,
    MedicalPatientFlowResponse,
)
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="resas_medical_patient_flow",
    table_name="resas_medical_patient_flow",
    primary_key=[
        "broad_category_code",
        "year",
        "pref_code",
        "secondary_medical_area_code",
    ],
    write_disposition="merge",
)
def get_medical_patient_flow_secondary_medical_area_job():
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = (
        MedicalPatientFlowRequest.generate_req_model_list_secondary_medical_code()
    )
    logger.info(f"req_model_list: {len(req_model_list)}")
    response = api_client.fetch_iter(
        request_models=req_model_list,
        with_params=True,
        exclude_params_keys=["prefCode", "secondaryMedicalCode"],
        response_model=MedicalPatientFlowResponse,
    )
    yield response


def load_medical_patient_flow_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="medical_patient_flow",
        destination="bigquery",
        # dataset_name=dlt.config.value,
        dataset_name="dl_localgov_kpi_database",
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_medical_patient_flow_secondary_medical_area_job)
    logger.info(load_info)
    logger.info(f"loaded row counts: {pipeline.last_trace.last_normalize_info}")
    return load_info


if __name__ == "__main__":
    load_medical_patient_flow_pipeline()
    # data = get_medical_patient_flow_job()
    # print(list(data))
