# # visualizations/genres.py
# from __future__ import annotations

# from collections import Counter
# from typing import Dict, List

# import matplotlib.pyplot as plt

# # Broad genres we "prefer" when multiple are present
# GENRE_PRIORITY = [
#     "Comedy", "Drama", "Action", "Adventure", "Romance",
#     "Horror", "Sci-Fi", "Thriller", "Animation",
#     "Documentary", "Family", "Crime",
# ]


# def _split_genre_string(raw: str) -> List[str]:
#     """Handle both 'A|B|C' and 'A, B, C' formats."""
#     if not raw or not isinstance(raw, str):
#         return []
#     if "|" in raw:
#         parts = [g.strip() for g in raw.split("|")]
#     else:
#         parts = [g.strip() for g in raw.split(",")]
#     return [p for p in parts if p]


# def primary_genre_from_meta(meta: Dict) -> str:
#     """
#     Pick a single 'primary' genre from either tmdb_genres or genres.

#     Priority:
#       1) use tmdb_genres if present, otherwise genres
#       2) within that list, prefer anything in GENRE_PRIORITY
#       3) otherwise just take the first token
#     """
#     raw = meta.get("tmdb_genres") or meta.get("genres") or ""
#     parts = _split_genre_string(raw)
#     if not parts:
#         return "Unknown"

#     for g in GENRE_PRIORITY:
#         if g in parts:
#             return g
#     return parts[0]


# def majority_primary_genre(indices: List[int], movie_metadata: List[Dict]) -> str:
#     """
#     Given a list of movie indices, return the most common primary genre.
#     """
#     if not indices:
#         return "Unknown"
#     genres = [primary_genre_from_meta(movie_metadata[i]) for i in indices]
#     if not genres:
#         return "Unknown"
#     return Counter(genres).most_common(1)[0][0]


# def build_genre_color_map(genres: List[str]) -> Dict[str, str]:
#     """
#     Map each genre name to a matplotlib color using tab20.
#     """
#     unique = sorted(set(genres))
#     cmap = plt.get_cmap("tab20")
#     return {g: cmap(i % 20) for i, g in enumerate(unique)}

# visualizations/genres.py
from __future__ import annotations

from collections import Counter
from typing import Dict, List

import matplotlib.pyplot as plt

# Broad genres we "prefer" when multiple are present
GENRE_PRIORITY = [
    "Drama", "Comedy", "Romance", "Crime", "Thriller",
    "Horror", "Documentary", "Action", "Adventure",
    "Animation", "Sci-Fi", "Family",
]

# ---------- low-level helpers ----------

def _split_genre_string(raw: str) -> List[str]:
    """Handle both 'A|B|C' and 'A, B, C' formats."""
    if not raw or not isinstance(raw, str):
        return []
    if "|" in raw:
        parts = [g.strip() for g in raw.split("|")]
    else:
        parts = [g.strip() for g in raw.split(",")]
    return [p for p in parts if p]


def extract_clean_genres(meta: Dict) -> List[str]:
    """
    Combine tmdb_genres + genres, normalize, and apply the 'Unknown' rule:

    - If there are any real genres AND 'Unknown' is present, drop 'Unknown'.
    - If the only label is 'Unknown', keep it.
    - Normalizes "Children's" -> "Family".
    """
    tags: List[str] = []

    raw_tmdb = meta.get("tmdb_genres")
    if isinstance(raw_tmdb, str):
        tags.extend(_split_genre_string(raw_tmdb))

    raw_ml = meta.get("genres")
    if isinstance(raw_ml, str):
        tags.extend(_split_genre_string(raw_ml))

    # normalize some variants
    norm = []
    for g in tags:
        if g == "Children's":
            norm.append("Family")
        else:
            norm.append(g)
    tags = [g for g in norm if g]

    if not tags:
        return ["Unknown"]

    # If we have more than one tag, drop Unknown
    if len(tags) > 1:
        tags = [g for g in tags if g.lower() != "unknown"]
        if not tags:
            # edge case: everything was 'Unknown'
            return ["Unknown"]

    return tags


# ---------- public helpers ----------

# def primary_genre_from_meta(meta: Dict) -> str:
#     """
#     Pick a single 'primary' genre from combined tmdb_genres + genres.

#     Priority:
#       1) Prefer anything in GENRE_PRIORITY.
#       2) Otherwise, just take the first cleaned genre.
#       3) 'Unknown' is only returned if it's truly the only label.
#     """
#     tags = extract_clean_genres(meta)
#     for g in GENRE_PRIORITY:
#         if g in tags:
#             return g
#     return tags[0]

def primary_genre_from_meta(meta: Dict) -> str:
    raw = meta.get("tmdb_genres") or meta.get("genres") or ""
    parts = _split_genre_string(raw)

    # ✅ Remove 'Unknown' everywhere unless it's the ONLY thing
    parts = [g for g in parts if g.lower() != "unknown"]

    if not parts:
        return None  # ✅ RETURN NONE INSTEAD OF "Unknown"

    for g in GENRE_PRIORITY:
        if g in parts:
            return g

    return parts[0]



def majority_primary_genre(indices: List[int], movie_metadata: List[Dict]) -> str:
    """
    Given a list of movie indices, return the most common primary genre.
    Uses the cleaned primary_genre_from_meta above.
    """
    if not indices:
        return "Unknown"
    genres = [primary_genre_from_meta(movie_metadata[i]) for i in indices]
    genres = [g for g in genres if g is not None]
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
