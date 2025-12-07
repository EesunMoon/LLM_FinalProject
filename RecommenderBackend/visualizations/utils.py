# visualizations/utils.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

RECOMMENDER_LOG_PATH = Path(__file__).resolve().parent.parent / "rec_log.jsonl"


def pca_2d(X: np.ndarray) -> np.ndarray:
    """
    Project embeddings X (N x D) into 2D using PCA via SVD.
    Returns X_2d: (N x 2)
    """
    X = np.asarray(X, dtype=np.float32)
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    components = Vt[:2]  # (2, D)
    return X_centered @ components.T  # (N, 2)


def load_log_records(user_id: str) -> List[Dict[str, Any]]:
    """
    Load all records from rec_log.jsonl for a specific user_id,
    sorted by msg_index ascending.
    """
    if not RECOMMENDER_LOG_PATH.exists():
        raise FileNotFoundError(
            f"{RECOMMENDER_LOG_PATH} does not exist. "
            "Run the recommender first so it writes rec_log.jsonl."
        )

    records: List[Dict[str, Any]] = []
    with open(RECOMMENDER_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("user_id") != user_id:
                continue
            if "msg_index" not in rec or "user_vec" not in rec:
                continue
            records.append(rec)

    if not records:
        raise ValueError(
            f"No log records found for user_id='{user_id}' in {RECOMMENDER_LOG_PATH}"
        )

    records.sort(key=lambda r: int(r.get("msg_index", 0)))
    return records


def pick_record_for_visualization(
    records: List[Dict[str, Any]],
    msg_index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    From a list of log records for a user, pick a specific one.

    If msg_index is None: return the latest (max msg_index).
    Otherwise: return the record with that msg_index, or raise.
    """
    if msg_index is None:
        return records[-1]

    for rec in records:
        if int(rec.get("msg_index", -1)) == msg_index:
            return rec

    raise ValueError(
        f"No record with msg_index={msg_index} found. "
        f"Available: {[r['msg_index'] for r in records]}"
    )
