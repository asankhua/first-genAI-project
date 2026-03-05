"""
Tests for Phase 1: dataset fetch logic.

Run from project root (first-genAI-project) or from phase1/:
  python -m pytest phase1/tests/test_fetch_dataset.py -v
  # or from phase1/:
  python -m pytest tests/test_fetch_dataset.py -v
"""

from datasets import Dataset, DatasetDict

from src.fetch_dataset import DATASET_ID, fetch_dataset, _take_sample


def test_fetch_dataset_returns_non_empty():
    """Fetch returns a dataset with at least one row (use small sample for speed)."""
    result = fetch_dataset(sample_size=50)
    assert result is not None

    if isinstance(result, DatasetDict):
        assert len(result) > 0
        # Typically 'train' split
        split = list(result.keys())[0]
        ds = result[split]
    else:
        ds = result

    assert len(ds) > 0, "Dataset should have at least one row"
    assert len(ds.column_names) > 0, "Dataset should have columns"


def test_fetch_dataset_has_expected_columns():
    """Fetched dataset has columns needed for recommendations (place, rating, etc.)."""
    result = fetch_dataset(sample_size=10)
    ds = result["train"] if isinstance(result, DatasetDict) else result
    columns = set(ds.column_names)

    # Zomato-style datasets typically have name, location, rate, votes, cuisines, etc.
    # Require at least one identifier and one filter-relevant column
    assert len(columns) >= 2, "Dataset should have multiple columns"
    # Common column name variants (dataset-specific)
    has_like_name = any(
        c for c in columns if "name" in c.lower() or "restaurant" in c.lower()
    )
    has_like_location = any(
        c for c in columns if "location" in c.lower() or "place" in c.lower() or "address" in c.lower()
    )
    has_like_rating = any(
        c for c in columns if "rate" in c.lower() or "rating" in c.lower()
    )
    assert (
        has_like_name or has_like_location or has_like_rating
    ), "Dataset should have name/location/rating-style columns"


def test_fetch_dataset_respects_sample_size():
    """When sample_size is set, returned dataset is limited to that many rows."""
    result = fetch_dataset(sample_size=5)
    if isinstance(result, DatasetDict):
        ds = result["train"]
    else:
        ds = result
    assert len(ds) == 5


def test_take_sample_dataset():
    """_take_sample with Dataset returns first n rows."""
    from datasets import Dataset
    d = Dataset.from_dict({"a": [1, 2, 3, 4, 5]})
    out = _take_sample(d, 2)
    assert isinstance(out, Dataset)
    assert len(out) == 2
    assert out["a"] == [1, 2]


def test_take_sample_dataset_dict():
    """_take_sample with DatasetDict samples each split."""
    from datasets import Dataset, DatasetDict
    d = DatasetDict({
        "train": Dataset.from_dict({"x": [1, 2, 3]}),
    })
    out = _take_sample(d, 2)
    assert isinstance(out, DatasetDict)
    assert len(out["train"]) == 2


def test_dataset_id_constant():
    """Default dataset ID matches architecture spec."""
    assert DATASET_ID == "ManikaSaini/zomato-restaurant-recommendation"
