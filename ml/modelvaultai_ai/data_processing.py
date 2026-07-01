from collections.abc import Iterable


def validate_required_columns(columns: Iterable[str], required_columns: Iterable[str]) -> list[str]:
    available = set(columns)
    return [column for column in required_columns if column not in available]


def build_dataset_profile(row_count: int, feature_count: int) -> dict[str, int]:
    return {"row_count": row_count, "feature_count": feature_count}
