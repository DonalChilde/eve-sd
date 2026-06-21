"""Loader for SDE YAML datasets."""

import json
from pathlib import Path
from typing import Any

from yaml import safe_load

from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format import yaml_datasets_dc as YD


def _load_file(file_path: Path) -> dict[str, Any]:
    with open(file_path) as f:
        if file_path.suffix == ".json":
            return json.load(f)
        elif file_path.suffix in [".yaml", ".yml"]:
            return safe_load(f)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")


class SdeYamlDatasetLoader:
    def __init__(self, sde_path: Path):
        """Loader for SDE YAML datasets.

        This loader will check the SDE path for a _sde file to determine the file type
        and load the build number and release date from it. This allows the same loader
        to be used for both YAML and JSON files of the YAML SDE data.

        Note that loading from yaml files is VERY slow with pyyaml.
        """
        self.sde_path = sde_path
        self.file_type: str = ""
        self.buildNumber: int = -1
        self.releaseDate: str = ""
        self._check_file_type()

    def _check_file_type(self):
        sde_file = list(self.sde_path.glob("_sde.*"))
        if len(sde_file) == 0:
            raise ValueError("No _sde file found in the provided path")
        if len(sde_file) > 1:
            raise ValueError("Multiple _sde files found in the provided path")
        self.file_type = sde_file[0].suffix
        if self.file_type not in [".yaml", ".yml", ".json"]:
            raise ValueError(f"Unsupported file type: {self.file_type}")
        data = _load_file(sde_file[0])
        sde_info = YD.SdeInfoRoot.model_validate(data)
        self.buildNumber = sde_info.root["sde"].buildNumber
        self.releaseDate = sde_info.root["sde"].releaseDate

    def _narrow_file_path(self, dataset_file: SdeDatasets) -> Path:
        file_name = (
            dataset_file.as_yaml()
            if self.file_type in [".yaml", ".yml"]
            else dataset_file.as_json()
        )
        file_path = self.sde_path / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_name} not found in the provided path")
        return file_path

    def agent_types(self) -> YD.AgentTypesRoot:
        """Load the agent types dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.AGENT_TYPES)
        data = _load_file(file_path)
        return YD.AgentTypesRoot.model_validate(data)

    def agents_in_space(self) -> YD.AgentsInSpaceRoot:
        """Load the agents in space dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.AGENTS_IN_SPACE)
        data = _load_file(file_path)
        return YD.AgentsInSpaceRoot.model_validate(data)

    def ancestries(self) -> YD.AncestriesRoot:
        """Load the ancestries dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.ANCESTRIES)
        data = _load_file(file_path)
        return YD.AncestriesRoot.model_validate(data)

    def archetypes(self) -> YD.ArchetypesRoot:
        """Load the archetypes dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.ARCHETYPES)
        data = _load_file(file_path)
        return YD.ArchetypesRoot.model_validate(data)

    def bloodlines(self) -> YD.BloodlinesRoot:
        """Load the bloodlines dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.BLOODLINES)
        data = _load_file(file_path)
        return YD.BloodlinesRoot.model_validate(data)

    def blueprints(self) -> YD.BlueprintsRoot:
        """Load the blueprints dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.BLUEPRINTS)
        data = _load_file(file_path)
        return YD.BlueprintsRoot.model_validate(data)

    def categories(self) -> YD.CategoriesRoot:
        """Load the categories dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CATEGORIES)
        data = _load_file(file_path)
        return YD.CategoriesRoot.model_validate(data)

    def certificates(self) -> YD.CertificatesRoot:
        """Load the certificates dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CERTIFICATES)
        data = _load_file(file_path)
        return YD.CertificatesRoot.model_validate(data)

    def character_attributes(self) -> YD.CharacterAttributesRoot:
        """Load the character attributes dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CHARACTER_ATTRIBUTES)
        data = _load_file(file_path)
        return YD.CharacterAttributesRoot.model_validate(data)

    def clone_grades(self) -> YD.CloneGradesRoot:
        """Load the clone grades dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CLONE_GRADES)
        data = _load_file(file_path)
        return YD.CloneGradesRoot.model_validate(data)

    def compressible_types(self) -> YD.CompressibleTypesRoot:
        """Load the compressible types dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.COMPRESSIBLE_TYPES)
        data = _load_file(file_path)
        return YD.CompressibleTypesRoot.model_validate(data)

    def contraband_types(self) -> YD.ContrabandTypesRoot:
        """Load the contraband types dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CONTRABAND_TYPES)
        data = _load_file(file_path)
        return YD.ContrabandTypesRoot.model_validate(data)

    def control_tower_resources(self) -> YD.ControlTowerResourcesRoot:
        """Load the control tower resources dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CONTROL_TOWER_RESOURCES)
        data = _load_file(file_path)
        return YD.ControlTowerResourcesRoot.model_validate(data)

    def corporation_activities(self) -> YD.CorporationActivitiesRoot:
        """Load the corporation activities dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.CORPORATION_ACTIVITIES)
        data = _load_file(file_path)
        return YD.CorporationActivitiesRoot.model_validate(data)

    def debuff_collections(self) -> YD.DbuffCollectionsRoot:
        """Load the debuff collections dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DBUFF_COLLECTIONS)
        data = _load_file(file_path)
        return YD.DbuffCollectionsRoot.model_validate(data)

    def dogma_attribute_categories(self) -> YD.DogmaAttributeCategoriesRoot:
        """Load the dogma attribute categories dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DOGMA_ATTRIBUTE_CATEGORIES)
        data = _load_file(file_path)
        return YD.DogmaAttributeCategoriesRoot.model_validate(data)

    def dogma_attributes(self) -> YD.DogmaAttributesRoot:
        """Load the dogma attributes dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DOGMA_ATTRIBUTES)
        data = _load_file(file_path)
        return YD.DogmaAttributesRoot.model_validate(data)

    def dogma_effects(self) -> YD.DogmaEffectsRoot:
        """Load the dogma effects dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DOGMA_EFFECTS)
        data = _load_file(file_path)
        return YD.DogmaEffectsRoot.model_validate(data)

    def dogma_units(self) -> YD.DogmaUnitsRoot:
        """Load the dogma units dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DOGMA_UNITS)
        data = _load_file(file_path)
        return YD.DogmaUnitsRoot.model_validate(data)

    def dungeons(self) -> YD.DungeonsRoot:
        """Load the dungeons dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DUNGEONS)
        data = _load_file(file_path)
        return YD.DungeonsRoot.model_validate(data)

    def dynamic_item_attributes(self) -> YD.DynamicItemAttributesRoot:
        """Load the dynamic item attributes dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.DYNAMIC_ITEM_ATTRIBUTES)
        data = _load_file(file_path)
        return YD.DynamicItemAttributesRoot.model_validate(data)

    def factions(self) -> YD.FactionsRoot:
        """Load the factions dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.FACTIONS)
        data = _load_file(file_path)
        return YD.FactionsRoot.model_validate(data)

    def freelance_job_schemas(self) -> YD.FreelanceJobSchemasRoot:
        """Load the freelance job schemas dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.FREELANCE_JOB_SCHEMAS)
        data = _load_file(file_path)
        return YD.FreelanceJobSchemasRoot.model_validate(data)

    def graphics(self) -> YD.GraphicsRoot:
        """Load the graphics dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.GRAPHICS)
        data = _load_file(file_path)
        return YD.GraphicsRoot.model_validate(data)

    def groups(self) -> YD.GroupsRoot:
        """Load the groups dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.GROUPS)
        data = _load_file(file_path)
        return YD.GroupsRoot.model_validate(data)

    def icons(self) -> YD.IconsRoot:
        """Load the icons dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.ICONS)
        data = _load_file(file_path)
        return YD.IconsRoot.model_validate(data)

    def landmarks(self) -> YD.LandmarksRoot:
        """Load the landmarks dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.LANDMARKS)
        data = _load_file(file_path)
        return YD.LandmarksRoot.model_validate(data)

    def map_asteroid_belts(self) -> YD.MapAsteroidBeltsRoot:
        """Load the map asteroid belts dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_ASTEROID_BELTS)
        data = _load_file(file_path)
        return YD.MapAsteroidBeltsRoot.model_validate(data)

    def map_constellations(self) -> YD.MapConstellationsRoot:
        """Load the map constellations dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_CONSTELLATIONS)
        data = _load_file(file_path)
        return YD.MapConstellationsRoot.model_validate(data)

    def map_moons(self) -> YD.MapMoonsRoot:
        """Load the map moons dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_MOONS)
        data = _load_file(file_path)
        return YD.MapMoonsRoot.model_validate(data)

    def map_planets(self) -> YD.MapPlanetsRoot:
        """Load the map planets dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_PLANETS)
        data = _load_file(file_path)
        return YD.MapPlanetsRoot.model_validate(data)

    def map_regions(self) -> YD.MapRegionsRoot:
        """Load the map regions dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_REGIONS)
        data = _load_file(file_path)
        return YD.MapRegionsRoot.model_validate(data)

    def map_secondary_suns(self) -> YD.MapSecondarySunsRoot:
        """Load the map secondary suns dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_SECONDARY_SUNS)
        data = _load_file(file_path)
        return YD.MapSecondarySunsRoot.model_validate(data)

    def map_solar_systems(self) -> YD.MapSolarSystemsRoot:
        """Load the map solar systems dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_SOLAR_SYSTEMS)
        data = _load_file(file_path)
        return YD.MapSolarSystemsRoot.model_validate(data)

    def map_stargates(self) -> YD.MapStargatesRoot:
        """Load the map stargates dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_STARGATES)
        data = _load_file(file_path)
        return YD.MapStargatesRoot.model_validate(data)

    def map_stars(self) -> YD.MapStarsRoot:
        """Load the map stars dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MAP_STARS)
        data = _load_file(file_path)
        return YD.MapStarsRoot.model_validate(data)

    def market_groups(self) -> YD.MarketGroupsRoot:
        """Load the market groups dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MARKET_GROUPS)
        data = _load_file(file_path)
        return YD.MarketGroupsRoot.model_validate(data)

    def masteries(self) -> YD.MasteriesRoot:
        """Load the masteries dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MASTERIES)
        data = _load_file(file_path)
        return YD.MasteriesRoot.model_validate(data)

    def mercenary_tactical_operations(self) -> YD.MercenaryTacticalOperationsRoot:
        """Load the mercenary tactical operations dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.MERCENARY_TACTICAL_OPERATIONS)
        data = _load_file(file_path)
        return YD.MercenaryTacticalOperationsRoot.model_validate(data)

    def meta_groups(self) -> YD.MetaGroupsRoot:
        """Load the meta groups dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.META_GROUPS)
        data = _load_file(file_path)
        return YD.MetaGroupsRoot.model_validate(data)

    def npc_characters(self) -> YD.NpcCharactersRoot:
        """Load the NPC characters dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.NPC_CHARACTERS)
        data = _load_file(file_path)
        return YD.NpcCharactersRoot.model_validate(data)

    def npc_corporation_divisions(self) -> YD.NpcCorporationDivisionsRoot:
        """Load the NPC corporation divisions dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.NPC_CORPORATION_DIVISIONS)
        data = _load_file(file_path)
        return YD.NpcCorporationDivisionsRoot.model_validate(data)

    def npc_corporations(self) -> YD.NpcCorporationsRoot:
        """Load the NPC corporations dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.NPC_CORPORATIONS)
        data = _load_file(file_path)
        return YD.NpcCorporationsRoot.model_validate(data)

    def npc_stations(self) -> YD.NpcStationsRoot:
        """Load the NPC stations dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.NPC_STATIONS)
        data = _load_file(file_path)
        return YD.NpcStationsRoot.model_validate(data)

    def planet_resources(self) -> YD.PlanetResourcesRoot:
        """Load the planet resources dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.PLANET_RESOURCES)
        data = _load_file(file_path)
        return YD.PlanetResourcesRoot.model_validate(data)

    def planet_schematics(self) -> YD.PlanetSchematicsRoot:
        """Load the planet schematics dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.PLANET_SCHEMATICS)
        data = _load_file(file_path)
        return YD.PlanetSchematicsRoot.model_validate(data)

    def races(self) -> YD.RacesRoot:
        """Load the races dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.RACES)
        data = _load_file(file_path)
        return YD.RacesRoot.model_validate(data)

    def sde_info(self) -> YD.SdeInfoRoot:
        """Load the SDE info dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.SDE_INFO)
        data = _load_file(file_path)
        return YD.SdeInfoRoot.model_validate(data)

    def skin_licenses(self) -> YD.SkinLicensesRoot:
        """Load the skin licenses dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.SKIN_LICENSES)
        data = _load_file(file_path)
        return YD.SkinLicensesRoot.model_validate(data)

    def skin_materials(self) -> YD.SkinMaterialsRoot:
        """Load the skin materials dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.SKIN_MATERIALS)
        data = _load_file(file_path)
        return YD.SkinMaterialsRoot.model_validate(data)

    def skins(self) -> YD.SkinsRoot:
        """Load the skins dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.SKINS)
        data = _load_file(file_path)
        return YD.SkinsRoot.model_validate(data)

    def sovereignty_upgrades(self) -> YD.SovereigntyUpgradesRoot:
        """Load the sovereignty upgrades dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.SOVEREIGNTY_UPGRADES)
        data = _load_file(file_path)
        return YD.SovereigntyUpgradesRoot.model_validate(data)

    def station_operations(self) -> YD.StationOperationsRoot:
        """Load the station operations dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.STATION_OPERATIONS)
        data = _load_file(file_path)
        return YD.StationOperationsRoot.model_validate(data)

    def station_services(self) -> YD.StationServicesRoot:
        """Load the station services dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.STATION_SERVICES)
        data = _load_file(file_path)
        return YD.StationServicesRoot.model_validate(data)

    def translation_languages(self) -> YD.TranslationLanguagesRoot:
        """Load the translation languages dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.TRANSLATION_LANGUAGES)
        data = _load_file(file_path)
        return YD.TranslationLanguagesRoot.model_validate(data)

    def type_bonus(self) -> YD.TypeBonusRoot:
        """Load the type bonus dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.TYPE_BONUS)
        data = _load_file(file_path)
        return YD.TypeBonusRoot.model_validate(data)

    def type_dogma(self) -> YD.TypeDogmaRoot:
        """Load the type dogma dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.TYPE_DOGMA)
        data = _load_file(file_path)
        return YD.TypeDogmaRoot.model_validate(data)

    def type_lists(self) -> YD.TypeListsRoot:
        """Load the type lists dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.TYPE_LISTS)
        data = _load_file(file_path)
        return YD.TypeListsRoot.model_validate(data)

    def type_materials(self) -> YD.TypeMaterialsRoot:
        """Load the type materials dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.TYPE_MATERIALS)
        data = _load_file(file_path)
        return YD.TypeMaterialsRoot.model_validate(data)

    def eve_types(self) -> YD.EveTypesRoot:
        """Load the EVE types dataset from the SDE."""
        file_path = self._narrow_file_path(SdeDatasets.TYPES)
        data = _load_file(file_path)
        return YD.EveTypesRoot.model_validate(data)
