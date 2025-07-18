from __future__ import annotations

import csv
import io
import json
from typing import Iterable, List, Dict

try:
    import boto3  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    boto3 = None  # type: ignore


def to_csv(items: List[Dict[str, str]]) -> str:
    """Serialize a list of dicts to CSV."""
    if not items:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(items[0].keys()))
    writer.writeheader()
    writer.writerows(items)
    return output.getvalue()


def to_jsonl(items: Iterable[Dict[str, str]]) -> str:
    """Serialize ``items`` to JSON Lines format."""
    return "\n".join(json.dumps(item) for item in items)


def upload_to_s3(items: List[Dict[str, str]], bucket: str, key: str) -> str:
    """Upload JSON Lines data to S3 and return the object URL."""
    if boto3 is None:
        raise RuntimeError("boto3 is not installed")
    data = to_jsonl(items)
    client = boto3.client("s3")
    client.put_object(Bucket=bucket, Key=key, Body=data.encode("utf-8"))
    return f"s3://{bucket}/{key}"
