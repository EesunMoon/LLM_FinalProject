# visualizations/genres.py
from __future__ import annotations

from collections import Counter
from typing import Dict, List

import matplotlib.pyplot as plt

# Broad genres we prefer when multiple are present
GENRE_PRIORITY = [
    "Comedy", "Drama", "Action", "Adventure", "Romance",
    "Horror", "Sci-Fi", "Thriller", "Animation",
    "Documentary", "Family", "Crime",
]


def _split_genre_string(raw: str) -> List[str]:
    """Handle both 'A|B|C' and 'A, B, C' formats."""
    if not raw or not isinstance(raw, str):
        return []
    if "|" in raw:
        parts = [g.strip() for g in raw.split("|")]
    else:
        parts = [g.strip() for g in raw.split(",")]
    return [p for p in parts if p]


def primary_genre_from_meta(meta: Dict) -> str:
    """
    Pick a single 'primary' genre from either tmdb_genres or genres.
    Priority order:
      1. Use tmdb_genres if present, else genres
      2. Within that set, prefer anything in GENRE_PRIORITY
      3. Otherwise just take the first token
    """
    raw = meta.get("tmdb_genres") or meta.get("genres") or ""
    parts = _split_genre_string(raw)
    if not parts:
        return "Unknown"

    for g in GENRE_PRIORITY:
        if g in parts:
            return g
    return parts[0]


def majority_primary_genre(indices: List[int], movie_metadata: List[Dict]) -> str:
    """
    Given a list of movie indices, return the single most common primary genre.
    """
    if not indices:
        return "Unknown"

    genres = [primary_genre_from_meta(movie_metadata[i]) for i in indices]
    if not genres:
        return "Unknown"
    return Counter(genres).most_common(1)[0][0]


def build_genre_color_map(genres: List[str]) -> Dict[str, str]:
    """
    Map each genre name to a matplotlib color using tab20.
    """
    unique = sorted(set(genres))
    cmap = plt.get_cmap("tab20")
    return {g: cmap(i % 20) for i, g in enumerate(unique)}
