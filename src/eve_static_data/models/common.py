"""Common type definitions for the EVE static data models."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Literal, TypedDict

from eve_static_data.models.dataset_filenames import SdeDatasets

TRANSLATION_MISSING = "NOT_AVAILABLE"

type Lang = Literal["en", "de", "fr", "ja", "ru", "zh", "ko", "es"]
"""A type representing the supported languages for localization."""

PossibleTranslationLanguages = {"en", "de", "fr", "ja", "ru", "zh", "ko", "es"}


class LangEnum(StrEnum):
    """An enum representing the supported languages for localization."""

    EN = "en"
    DE = "de"
    FR = "fr"
    JA = "ja"
    RU = "ru"
    ZH = "zh"
    KO = "ko"
    ES = "es"


def lang_check(lang: Lang) -> None:
    """Helper function to check if a language is valid."""
    if lang not in PossibleTranslationLanguages:
        raise ValueError(
            f"Invalid language: {lang}. Must be one of {PossibleTranslationLanguages}."
        )


class LocalizedString(TypedDict, total=False):
    """The shape of a localized string.

    The languages are defined in the SDE file: translationLanguages.jsonl
    """

    en: str
    de: str
    fr: str
    ja: str
    zh: str
    ru: str
    ko: str
    es: str


class LocalizableRecord:
    def localized_fields(self, lang: Lang | None) -> dict[Any, str | None]:
        """Returns a dict of the localized fields in the model.

        Args:
            lang: The language to return the localized fields for. If None, returns {field_name: None}.

        Returns:
            A dict of the localized fields in the model, with the field name as the key
                and the `lang` localized string as the value.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


ACTIVITIES: set[str] = {
    "copying",
    "invention",
    "manufacturing",
    "reaction",
    "research_material",
    "research_time",
}
"""Industrial activities from blueprints."""


def narrow_localizable_json_dict(
    json_record: dict[str, Any], langs: set[Lang]
) -> dict[str, Any]:
    """Narrow a JSON dict representing a LocalizableRecord to a specific language.

    This is used for the CLI export, to avoid the overhead of converting to the Pydantic models
    and then back to JSON.

    must detect which fields are localized by checking if the value is a LocalizedString,
    and then narrow those fields to the specified languages.

    Args:
        json_record: The JSON dict representing the record. It should have the same shape as the Pydantic model,
            but with all fields as dicts of {lang: value}.
        langs: The set of languages to narrow to.

    Returns:
        A new JSON dict containing the record with only the translation for the target language.
    """
    if not langs:
        raise ValueError("At least one language must be specified.")
    for key, value in json_record.items():
        if isinstance(value, dict) and set(value.keys()).issubset(
            PossibleTranslationLanguages
        ):
            # This is a localized field, narrow it to the specified languages
            json_record[key] = {
                lang: value.get(lang, TRANSLATION_MISSING) for lang in langs
            }
        elif isinstance(value, dict):
            # This is a nested record, recursively narrow it
            json_record[key] = narrow_localizable_json_dict(value, langs)
        elif isinstance(value, list):
            # This is a list of records, recursively narrow each item if it's a dict
            json_record[key] = [
                narrow_localizable_json_dict(item, langs)
                if isinstance(item, dict)
                else item
                for item in value
            ]
    return json_record


@dataclass(slots=True, kw_only=True)
class DatasetRecordBase:
    """The base class for all dataset records."""

    dataset: ClassVar[SdeDatasets]
