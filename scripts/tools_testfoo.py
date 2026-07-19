# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
import asyncio
from pathlib import Path

from pfmsoft.eve_sd.sde_tools import SDETools

DOWNLOAD_DIR = Path("~/tmp/tools_test").expanduser()


def main() -> None:
    esd_tools = SDETools()
    try:
        sde_file, build_number = get_sde_file_path()
    except FileNotFoundError:
        print("No SDE file found in the download directory. Downloading...")
        sde_info = asyncio.run(esd_tools.latest_sde_info())
        build_number = sde_info["buildNumber"]
        sde_file = test_download(build_number=build_number)
    test_process(sde_file=sde_file, build_number=build_number)


def test_download(build_number: int) -> Path:
    esd_tools = SDETools()
    sde_file = asyncio.run(
        esd_tools.download(
            build_number=build_number, output_path=DOWNLOAD_DIR, overwrite=False
        )
    )
    print(f"Downloaded SDE file to {sde_file}")
    return sde_file


def get_sde_file_path() -> tuple[Path, int]:
    sde_file = next(iter(DOWNLOAD_DIR.glob("eve-online-static-data-*.zip")), None)
    if sde_file is None:
        raise FileNotFoundError("No SDE file found in the download directory.")
    print(f"Found SDE file {sde_file} in the download directory.")
    build_number = int(sde_file.stem.split("-")[-2])
    return sde_file, build_number


def test_process(sde_file: Path | None, build_number: int) -> None:
    esd_tools = SDETools()

    process_dir = DOWNLOAD_DIR / "processed"
    if sde_file is None:
        sde_file, build_number = get_sde_file_path()
    print(f"Processing SDE file {sde_file} to {process_dir}")
    asyncio.run(
        esd_tools.process(
            input_path=sde_file,
            output_path=process_dir,
            build_number=build_number,
            lang=["en"],
        )
    )


if __name__ == "__main__":
    main()
