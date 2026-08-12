import json
from functools import lru_cache
from pathlib import Path

CATALOG_PATH = Path(__file__).parent / "data" / "catalog.json"

VALID_UNITS = {"reps", "seconds", "taps"}
REQUIRED_LEVEL_KEYS = {"sets", "reps", "unit", "perSide"}


def _validate(data: dict) -> None:
    if "schedule" not in data or "families" not in data:
        raise ValueError("catalog.json must have 'schedule' and 'families' keys")

    families = data["families"]
    if not isinstance(families, dict) or not families:
        raise ValueError("catalog 'families' must be a non-empty object")

    for family_name, exercises in families.items():
        if not isinstance(exercises, list) or not exercises:
            raise ValueError(f"family '{family_name}' must have a non-empty exercise list")
        for exercise in exercises:
            if "name" not in exercise:
                raise ValueError(f"exercise in family '{family_name}' missing 'name'")
            for level_key in ("level1", "level2", "level3"):
                if level_key not in exercise:
                    raise ValueError(
                        f"exercise '{exercise.get('name')}' in family '{family_name}' missing '{level_key}'"
                    )
                level = exercise[level_key]
                missing = REQUIRED_LEVEL_KEYS - level.keys()
                if missing:
                    raise ValueError(
                        f"{family_name}/{exercise.get('name')}/{level_key} missing keys: {missing}"
                    )
                if level["unit"] not in VALID_UNITS:
                    raise ValueError(
                        f"{family_name}/{exercise.get('name')}/{level_key} has invalid unit '{level['unit']}'"
                    )

    schedule = data["schedule"]
    for day, families_for_day in schedule.items():
        for family_name in families_for_day:
            if family_name not in families:
                raise ValueError(f"schedule day '{day}' references unknown family '{family_name}'")


@lru_cache(maxsize=1)
def load_catalog() -> dict:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    _validate(data)
    return data


def get_families() -> dict:
    return load_catalog()["families"]


def get_schedule() -> dict:
    return load_catalog()["schedule"]


def get_exercise_list(family: str) -> list[dict]:
    families = get_families()
    if family not in families:
        raise KeyError(f"unknown family '{family}'")
    return families[family]


def get_exercise_at_index(family: str, index: int) -> dict:
    exercises = get_exercise_list(family)
    if index < 0 or index >= len(exercises):
        raise IndexError(f"exercise index {index} out of range for family '{family}'")
    return exercises[index]


def family_names() -> list[str]:
    return list(get_families().keys())
