from __future__ import annotations
from typing import Any, Dict, Iterable, Optional
from google.cloud import bigquery

from app.settings import settings


_client: Optional[bigquery.Client] = None


def _bq() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client()
    return _client


def insert_rows(table: str, rows: Iterable[Dict[str, Any]]) -> None:
    """
    Best-effort insert. Failures should not break user flow.
    table: table name without dataset (e.g., "route_request")
    """
    rows = list(rows)
    if not rows:
        return
    table_id = f"{_bq().project}.{settings.BQ_DATASET}.{table}"
    errors = _bq().insert_rows_json(table_id, rows)
    # Best-effort: ignore errors at MVP; log if you want
    if errors:
        # You can emit structured logs here
        pass
