"""
Pipeline orchestrator: apply cleaning rules to raw rows and output valid records.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .cleaners import clean_cuisines, clean_price, clean_rating

# Default mapping from logical field names to typical dataset column names.
# Callers can override when column names differ (e.g. HF dataset uses "rate", "cuisines").
DEFAULT_COLUMN_MAP = {
    "price": "approx_cost(for two people)",
    "rating": "rate",
    "cuisines": "cuisines",
}


def run_pipeline(
    raw_rows: List[Dict[str, Any]],
    column_map: Optional[Dict[str, str]] = None,
    required_columns: Optional[List[str]] = None,
    drop_invalid: bool = True,
) -> List[Dict[str, Any]]:
    """
    Apply cleaning rules to each row and return valid clean records.

    Args:
        raw_rows: List of dicts (e.g. from Phase 1 dataset rows).
        column_map: Mapping from logical names (price, rating, cuisines) to
            actual column names in raw_rows. If None, uses DEFAULT_COLUMN_MAP.
        required_columns: Logical names that must be present and clean for a
            row to be kept. Default: ["rating"] (rating is mandatory per spec).
        drop_invalid: If True, drop rows that fail validation; if False, keep
            them but with None for failed fields (not recommended).

    Returns:
        List of dicts with standardized keys: price (int|None), rating (float|None),
        cuisines (list), plus all original keys preserved. Rows that fail
        required_columns validation are omitted when drop_invalid is True.
    """
    column_map = column_map or DEFAULT_COLUMN_MAP.copy()
    required_columns = required_columns or ["rating"]
    result: List[Dict[str, Any]] = []

    for row in raw_rows:
        clean = _clean_row(row, column_map)
        if drop_invalid:
            if not _row_satisfies_required(clean, required_columns):
                continue
        result.append(clean)

    return result


def _clean_row(row: Dict[str, Any], column_map: Dict[str, str]) -> Dict[str, Any]:
    """Build one clean record from a raw row."""
    out: Dict[str, Any] = dict(row)

    price_col = column_map.get("price")
    if price_col and price_col in row:
        out["price"] = clean_price(row[price_col])
    else:
        out["price"] = None

    rating_col = column_map.get("rating")
    if rating_col and rating_col in row:
        out["rating"] = clean_rating(row[rating_col])
    else:
        out["rating"] = None

    cuisines_col = column_map.get("cuisines")
    if cuisines_col and cuisines_col in row:
        out["cuisines"] = clean_cuisines(row[cuisines_col])
    else:
        out["cuisines"] = []

    return out


def _row_satisfies_required(clean_row: Dict[str, Any], required: List[str]) -> bool:
    """Return True if all required logical fields are present and valid."""
    for key in required:
        if key == "rating":
            if clean_row.get("rating") is None:
                return False
        elif key == "price":
            if clean_row.get("price") is None:
                return False
        elif key == "cuisines":
            # cuisines is optional; we only require it to be a list (always set)
            pass
    return True


def save_cleaned(
    clean_rows: List[Dict[str, Any]],
    path: Union[str, Path],
    format: str = "csv",
) -> Path:
    """
    Persist cleaned records to disk (optional Phase 2.4).

    Args:
        clean_rows: Output from run_pipeline().
        path: File path (e.g. data/cleaned.csv or data/cleaned.parquet).
        format: "csv" or "parquet".

    Returns:
        Resolved path to the written file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if format == "csv":
        import csv
        if not clean_rows:
            path.write_text("")
            return path.resolve()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(clean_rows[0].keys()), extrasaction="ignore")
            writer.writeheader()
            for row in clean_rows:
                # Serialize list fields for CSV
                out = {}
                for k, v in row.items():
                    if isinstance(v, list):
                        out[k] = ",".join(str(x) for x in v)
                    else:
                        out[k] = v
                writer.writerow(out)
        return path.resolve()

    if format == "parquet":
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("parquet format requires pandas and pyarrow. pip install pandas pyarrow")
        df = pd.DataFrame(clean_rows)
        df.to_parquet(path, index=False)
        return path.resolve()

    raise ValueError(f"Unsupported format: {format}. Use 'csv' or 'parquet'.")
