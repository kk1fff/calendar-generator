import argparse
from typing import Dict, Callable, List

import yaml

from mode import weekly, monthly
from importer import build_importers, IImporter

MODE_GENERATORS: Dict[str, Callable[[str, str, List[IImporter]], None]] = {
    "weekly": weekly.generate,
    "monthly": monthly.generate,
}


def _load_preset(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Preset file must define a mapping of options")
    return {str(k): v for k, v in data.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a calendar PDF.")
    parser.add_argument("--preset", required=True, help="Path to YAML preset file")
    parser.add_argument("--start_date", required=True, help="Start date in YYYY/MM/DD format")
    parser.add_argument("--end_date", required=True, help="End date in YYYY/MM/DD format")
    args = parser.parse_args()

    config = _load_preset(args.preset)
    importers = build_importers(config.get("importers", []))
    for imp in importers:
        imp.Load()
    mode_name = config.get("mode")
    generator = MODE_GENERATORS.get(mode_name)
    if generator is None:
        raise ValueError(f"Unsupported mode: {mode_name}")

    generator(args.start_date, args.end_date, importers)


if __name__ == "__main__":
    main()
