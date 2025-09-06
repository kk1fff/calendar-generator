import argparse
from typing import Dict, Callable

import yaml

from mode import weekly

MODE_GENERATORS: Dict[str, Callable[[str, str], None]] = {
    "weekly": weekly.generate,
}


def _load_preset(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Preset file must define a mapping of options")
    return {str(k): str(v) for k, v in data.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a calendar PDF.")
    parser.add_argument("--preset", required=True, help="Path to YAML preset file")
    parser.add_argument("--start_date", required=True, help="Start date in YYYY/MM/DD format")
    parser.add_argument("--end_date", required=True, help="End date in YYYY/MM/DD format")
    args = parser.parse_args()

    config = _load_preset(args.preset)
    mode_name = config.get("mode")
    generator = MODE_GENERATORS.get(mode_name)
    if generator is None:
        raise ValueError(f"Unsupported mode: {mode_name}")

    generator(args.start_date, args.end_date)


if __name__ == "__main__":
    main()
