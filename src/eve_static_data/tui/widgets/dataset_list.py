"""Dataset list widget for the browser screen."""

from pathlib import Path

from textual.widgets import OptionList

from eve_static_data.models.dataset_filenames import SdeDatasetFiles


class DatasetList(OptionList):
    """Option list that marks files known to the ``SdeDatasetFiles`` enum."""

    def set_files(self, files: list[Path]) -> None:
        """Populate list entries from dataset files.

        Args:
            files: File paths to display.
        """
        self.clear_options()
        known_stems = {dataset.value for dataset in SdeDatasetFiles}
        for file in sorted(files, key=lambda item: item.name.lower()):
            stem = file.stem
            if stem in known_stems:
                self.add_option(stem)
            else:
                self.add_option(f"{stem} [unknown]")
