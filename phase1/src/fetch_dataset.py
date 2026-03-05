"""
Fetch Zomato restaurant recommendation dataset from Hugging Face.

Dataset: ManikaSaini/zomato-restaurant-recommendation
"""

import os
from typing import Optional, Union

from datasets import Dataset, DatasetDict, load_dataset


DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"


def fetch_dataset(
    dataset_id: str = DATASET_ID,
    use_auth_token: Optional[Union[bool, str]] = None,
    sample_size: Optional[int] = None,
) -> Union[Dataset, DatasetDict]:
    """
    Load the Zomato restaurant recommendation dataset from Hugging Face.

    Args:
        dataset_id: Hugging Face dataset repo id. Defaults to
            ManikaSaini/zomato-restaurant-recommendation.
        use_auth_token: HF token for gated/private datasets. If None, uses
            HF_TOKEN env var when set; pass True to use cached login.
        sample_size: If set, return only the first N rows (for faster runs).
            Applied to the 'train' split if the dataset is a DatasetDict.

    Returns:
        Dataset or DatasetDict from Hugging Face. If the dataset has a single
        split (e.g. 'train'), you may get a DatasetDict with one key.

    Raises:
        Exception: On load or network errors.
    """
    token = use_auth_token
    if token is None and os.environ.get("HF_TOKEN"):
        token = os.environ["HF_TOKEN"]

    dataset = load_dataset(dataset_id, token=token)

    if sample_size is not None and sample_size > 0:
        dataset = _take_sample(dataset, sample_size)

    return dataset


def _take_sample(
    dataset: Union[Dataset, DatasetDict], n: int
) -> Union[Dataset, DatasetDict]:
    """Return first n rows. Works for Dataset or DatasetDict with 'train' split."""
    if isinstance(dataset, Dataset):
        return dataset.select(range(min(n, len(dataset))))
    if isinstance(dataset, DatasetDict):
        out = {}
        for split_name, split_ds in dataset.items():
            out[split_name] = split_ds.select(range(min(n, len(split_ds))))
        return DatasetDict(out)
    return dataset


def dataset_to_rows(dataset: Union[Dataset, DatasetDict], split: str = "train") -> list:
    """
    Convert a HuggingFace Dataset or DatasetDict to a list of dicts for Phase 2.

    Args:
        dataset: Output from fetch_dataset().
        split: Split name to use when dataset is a DatasetDict (e.g. "train").

    Returns:
        List of dicts, one per row (column names as keys).
    """
    if isinstance(dataset, DatasetDict):
        ds = dataset.get(split)
        if ds is None:
            ds = list(dataset.values())[0]
    else:
        ds = dataset
    return [dict(row) for row in ds]
