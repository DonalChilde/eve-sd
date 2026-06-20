from collections.abc import Iterable
from dataclasses import dataclass

from httpx2 import Client

from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.sde_metadata import SdeMetadata
from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_datasets import datasets_to_root_model_lookup
from eve_static_data.sde_tools import SDETools
from eve_static_data.validation.models import (
    DatasetInput,
    DatasetValidationResult,
    EnhancedValidationResults,
    FailedRecordValidation,
    SdeValidationSummary,
)


@dataclass
class NetworkArtifacts:
    schema_changes: str
    data_changes: str


def _fetch_changes(
    build_number: int, sde_tools: SDETools, session: Client
) -> NetworkArtifacts:
    """Fetch schema changelog for a given dataset and source format."""

    schema_changes = sde_tools.fetch_schema_changelog(build_number, session=session)
    data_changes = sde_tools.fetch_data_changes(build_number, session=session)

    return NetworkArtifacts(
        schema_changes=schema_changes if schema_changes else "",
        data_changes=data_changes if data_changes else "",
    )


def validate_yaml_datasets(
    datasets: Iterable[DatasetInput],
    sde_metadata: SdeMetadata,
    *,
    sde_tools: SDETools | None = None,
    session: Client | None = None,
) -> SdeValidationSummary:
    if sde_tools is None:
        sde_tools = SDETools()
    if session is None:
        session = config_http_client()
    network_artifacts = _fetch_changes(
        build_number=sde_metadata.buildNumber,
        sde_tools=sde_tools,
        session=session,
    )
    for dataset_input in datasets:
        dataset_name = dataset_input["dataset_name"]
        dataset_data = dataset_input["dataset_data"]
        dataset_enum = SdeDatasets(dataset_name)
        root_model_lookup = datasets_to_root_model_lookup()
        root_model_class = root_model_lookup.get(dataset_enum)
        if root_model_class is None:
            raise ValueError(f"No RootModel class found for dataset {dataset_name}")

        try:
            root_model_class.model_validate(dataset_data)
            validation_result = DatasetValidationResult(
                dataset=dataset_name,
                source_format="yaml-model",
                record_count=len(dataset_data),
            )
        except Exception as e:
            validation_result = DatasetValidationResult(
                dataset=dataset_name,
                source_format="yaml-model",
                record_count=len(dataset_data),
                parse_error=str(e),
            )
        yield validation_result


# for yaml record models, add record_key to each top level model.
# When loading from file, add record_key to each top level record, using the key from the dict.
# Check logic for change w/ db load.
# make a yaml loader that inserts the record_key into each top level record when loading from file.
