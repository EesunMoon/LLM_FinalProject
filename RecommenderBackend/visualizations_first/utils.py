# visualizations/utils.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np

# Path to the JSONL log created by recommender.py
RECOMMENDER_LOG_PATH = Path(__file__).resolve().parent.parent / "rec_log.jsonl"

# Broad genres we prefer when collapsing multi-genre labels
GENRE_PRIORITY = [
    "Comedy", "Drama", "Action", "Adventure", "Romance",
    "Horror", "Sci-Fi", "Animation", "Family", "Crime",
    "Documentary", "Thriller",
]


# ---------- genre helpers ----------

def primary_genre_from_meta(meta: dict) -> str:
    """
    Pick a single 'primary' genre from tmdb_genres or genres.
    """
    raw = meta.get("tmdb_genres") or meta.get("genres") or ""
    if not raw or not isinstance(raw, str):
        return "Unknown"

    if "," in raw:
        parts = [g.strip() for g in raw.split(",")]
    else:
        parts = [g.strip() for g in raw.split("|")]

    parts = [p for p in parts if p]
    if not parts:
        return "Unknown"

    for g in GENRE_PRIORITY:
        if g in parts:
            return g
    return parts[0]


def pca_2d(X: np.ndarray) -> np.ndarray:
    """
    Simple PCA to 2D using SVD.
    """
    X = np.asarray(X, dtype=np.float32)
    Xc = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    comps = Vt[:2]          # (2, D)
    return Xc @ comps.T     # (N, 2)


# ---------- log helpers ----------

def load_log_records(user_id: str) -> List[Dict[str, Any]]:
    """
    Load all records from rec_log.jsonl for a specific user_id,
    sorted by msg_index ascending.
    """
    if not RECOMMENDER_LOG_PATH.exists():
        raise FileNotFoundError(
            f"{RECOMMENDER_LOG_PATH} does not exist. "
            "Run the recommender at least once with logging enabled."
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
    If msg_index is None -> latest; else choose exact msg_index.
    """
    if msg_index is None:
        return records[-1]

    for r in records:
        if int(r.get("msg_index", -1)) == msg_index:
            return r

    raise ValueError(
        f"No record with msg_index={msg_index}. "
        f"Available: {[r['msg_index'] for r in records]}"
    )
