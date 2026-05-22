"""Export helpers for CSV/JSON report artifacts."""

import json
from pathlib import Path
from typing import Any

import pandas as pd


def export_dataframe(df: pd.DataFrame, path: str) -> None:
    """Export dataframe to CSV file path, creating parent directories."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)


def export_json(payload: dict[str, Any], path: str) -> None:
    """Export dictionary payload to pretty-printed JSON file."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)

