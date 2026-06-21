# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pydantic>=2.12.5",
#     "pyyaml>=6.0.3",
#     "typer>=0.24.1",
# ]
# ///
import json
from pathlib import Path
from time import perf_counter
from typing import Annotated, Any

import typer
from pydantic import RootModel
from yaml import safe_load

from eve_static_data.models.yaml_format import yaml_datasets_dc

app = typer.Typer()

YAML_DATASET_CASES: list[tuple[str, type[RootModel[Any]]]] = [
    ("agentsInSpace.yaml", yaml_datasets_dc.AgentsInSpaceRoot),
    ("agentTypes.yaml", yaml_datasets_dc.AgentTypesRoot),
    ("ancestries.yaml", yaml_datasets_dc.AncestriesRoot),
    ("bloodlines.yaml", yaml_datasets_dc.BloodlinesRoot),
    ("blueprints.yaml", yaml_datasets_dc.BlueprintsRoot),
    ("categories.yaml", yaml_datasets_dc.CategoriesRoot),
    ("certificates.yaml", yaml_datasets_dc.CertificatesRoot),
    ("characterAttributes.yaml", yaml_datasets_dc.CharacterAttributesRoot),
    ("cloneGrades.yaml", yaml_datasets_dc.CloneGradesRoot),
    ("compressibleTypes.yaml", yaml_datasets_dc.CompressibleTypesRoot),
    ("contrabandTypes.yaml", yaml_datasets_dc.ContrabandTypesRoot),
    ("controlTowerResources.yaml", yaml_datasets_dc.ControlTowerResourcesRoot),
    ("corporationActivities.yaml", yaml_datasets_dc.CorporationActivitiesRoot),
    ("dbuffCollections.yaml", yaml_datasets_dc.DbuffCollectionsRoot),
    ("dogmaAttributeCategories.yaml", yaml_datasets_dc.DogmaAttributeCategoriesRoot),
    ("dogmaAttributes.yaml", yaml_datasets_dc.DogmaAttributesRoot),
    ("dogmaEffects.yaml", yaml_datasets_dc.DogmaEffectsRoot),
    ("dogmaUnits.yaml", yaml_datasets_dc.DogmaUnitsRoot),
    ("dynamicItemAttributes.yaml", yaml_datasets_dc.DynamicItemAttributesRoot),
    ("factions.yaml", yaml_datasets_dc.FactionsRoot),
    ("freelanceJobSchemas.yaml", yaml_datasets_dc.FreelanceJobSchemasRoot),
    ("graphics.yaml", yaml_datasets_dc.GraphicsRoot),
    ("groups.yaml", yaml_datasets_dc.GroupsRoot),
    ("icons.yaml", yaml_datasets_dc.IconsRoot),
    ("landmarks.yaml", yaml_datasets_dc.LandmarksRoot),
    ("mapAsteroidBelts.yaml", yaml_datasets_dc.MapAsteroidBeltsRoot),
    ("mapConstellations.yaml", yaml_datasets_dc.MapConstellationsRoot),
    ("mapMoons.yaml", yaml_datasets_dc.MapMoonsRoot),
    ("mapPlanets.yaml", yaml_datasets_dc.MapPlanetsRoot),
    ("mapRegions.yaml", yaml_datasets_dc.MapRegionsRoot),
    ("mapSecondarySuns.yaml", yaml_datasets_dc.MapSecondarySunsRoot),
    ("mapSolarSystems.yaml", yaml_datasets_dc.MapSolarSystemsRoot),
    ("mapStargates.yaml", yaml_datasets_dc.MapStargatesRoot),
    ("mapStars.yaml", yaml_datasets_dc.MapStarsRoot),
    ("marketGroups.yaml", yaml_datasets_dc.MarketGroupsRoot),
    ("masteries.yaml", yaml_datasets_dc.MasteriesRoot),
    ("metaGroups.yaml", yaml_datasets_dc.MetaGroupsRoot),
    (
        "mercenaryTacticalOperations.yaml",
        yaml_datasets_dc.MercenaryTacticalOperationsRoot,
    ),
    ("npcCharacters.yaml", yaml_datasets_dc.NpcCharactersRoot),
    ("npcCorporationDivisions.yaml", yaml_datasets_dc.NpcCorporationDivisionsRoot),
    ("npcCorporations.yaml", yaml_datasets_dc.NpcCorporationsRoot),
    ("npcStations.yaml", yaml_datasets_dc.NpcStationsRoot),
    ("planetResources.yaml", yaml_datasets_dc.PlanetResourcesRoot),
    ("planetSchematics.yaml", yaml_datasets_dc.PlanetSchematicsRoot),
    ("races.yaml", yaml_datasets_dc.RacesRoot),
    ("skinLicenses.yaml", yaml_datasets_dc.SkinLicensesRoot),
    ("skinMaterials.yaml", yaml_datasets_dc.SkinMaterialsRoot),
    ("skins.yaml", yaml_datasets_dc.SkinsRoot),
    ("_sde.yaml", yaml_datasets_dc.SdeInfoRoot),
    ("sovereigntyUpgrades.yaml", yaml_datasets_dc.SovereigntyUpgradesRoot),
    ("stationOperations.yaml", yaml_datasets_dc.StationOperationsRoot),
    ("stationServices.yaml", yaml_datasets_dc.StationServicesRoot),
    ("translationLanguages.yaml", yaml_datasets_dc.TranslationLanguagesRoot),
    ("typeBonus.yaml", yaml_datasets_dc.TypeBonusRoot),
    ("typeDogma.yaml", yaml_datasets_dc.TypeDogmaRoot),
    ("typeMaterials.yaml", yaml_datasets_dc.TypeMaterialsRoot),
    ("types.yaml", yaml_datasets_dc.EveTypesRoot),
]


@app.command()
def main(
    sde_path: Annotated[Path, typer.Argument(..., help="Path to the SDE directory")],
    output_path: Annotated[
        Path, typer.Argument(..., help="Path to output the JSON files to")
    ],
) -> None:
    """Script to test YAML fixture round-tripping through JSON."""
    for (
        sde_file,
        root_model,
    ) in yaml_datasets_dc.datasets_to_root_model_lookup().items():
        yaml_file_path = sde_path / sde_file.as_yaml()
        print(f"Processing {yaml_file_path}...")
        with yaml_file_path.open(encoding="utf-8") as file_handle:
            start = perf_counter()
            loaded: Any = safe_load(file_handle)
            print(
                f"\tLoaded {sde_file} with pyyaml in {perf_counter() - start:.2f} seconds, now validating against {root_model.__name__}..."
            )

        assert isinstance(loaded, dict)
        start = perf_counter()
        model_instance = root_model.model_validate(loaded)
        print(
            f"\tValidated {sde_file} against {root_model.__name__} in {perf_counter() - start:.2f} seconds, now dumping to JSON..."
        )
        json_output = model_instance.model_dump_json(indent=2)

        output_file_path = output_path / sde_file.as_json()
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        start = perf_counter()
        output_file_path.write_text(json_output, encoding="utf-8")
        print(
            f"\tDumped {sde_file} to JSON via pydantic in {perf_counter() - start:.2f} seconds at {output_file_path}."
        )
        start = perf_counter()
        with open(output_file_path, encoding="utf-8") as file_handle:
            reloaded = root_model.model_validate_json(file_handle.read())
        print(
            f"\tReloaded {sde_file} from JSON via pydantic in {perf_counter() - start:.2f} seconds."
        )
        start = perf_counter()
        with open(output_file_path, encoding="utf-8") as file_handle:
            reloaded_json = json.load(file_handle)
        print(
            f"\tReloaded {sde_file} from JSON using standard json.load in {perf_counter() - start:.2f} seconds, final validation successful."
        )


if __name__ == "__main__":
    app()
