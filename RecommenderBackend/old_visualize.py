#!/usr/bin/env python
"""
Visualization tools for the taste-based movie recommender.

Uses rec_log.jsonl (created by recommender.py) so you can visualize
recommendations over time, per user and per message.

Usage examples:
    cd RecommenderBackend

    # latest message for this user
    python visualize.py --user-id emily

    # specific message index (e.g., "msg 3" for that user)
    python visualize.py --user-id emily --msg-index 3

    # specify output directory
    python visualize.py --user-id emily --out-dir figures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Optional

import numpy as np
import matplotlib.pyplot as plt

from embedding_loader import load_movie_embeddings
from vector_index import MovieIndex  # not strictly needed, but nice to keep symmetry
from config import MOVIE_EMBED_PATH

from matplotlib.patches import Patch
from sklearn.decomposition import PCA
import textwrap


from collections import defaultdict
from sklearn.decomposition import PCA
import textwrap

GENRE_PRIORITY = [
    "Comedy", "Drama", "Action", "Adventure", "Romance",
    "Horror", "Sci-Fi", "Animation", "Family", "Crime",
    "Documentary", "Thriller"
]

def primary_genre_from_meta(meta: dict) -> str:
    """
    Pick a single 'primary' genre from tmdb_genres or genres.
    """
    raw = meta.get("tmdb_genres") or meta.get("genres") or ""
    if not raw or not isinstance(raw, str):
        return "Unknown"

    # tmdb_genres: "Family, Comedy, Animation, Adventure"
    # genres:      "Animation|Children's|Comedy"
    if "," in raw:
        parts = [g.strip() for g in raw.split(",")]
    else:
        parts = [g.strip() for g in raw.split("|")]

    parts = [p for p in parts if p]
    if not parts:
        return "Unknown"

    # Prefer broad genres to reduce fragmentation
    for g in GENRE_PRIORITY:
        if g in parts:
            return g

    return parts[0]


def compute_genre_centroids(
    movie_embeddings: np.ndarray,
    movie_metadata: list[dict],
    min_count: int = 30,
):
    """
    Returns:
        centroids: np.ndarray [G, D]
        genres:    list[str] length G
        sizes:     np.ndarray [G] (number of movies per genre)
    Only genres with >= min_count movies are kept.
    """
    sums = defaultdict(lambda: np.zeros(movie_embeddings.shape[1], dtype=np.float32))
    counts = defaultdict(int)

    for emb, meta in zip(movie_embeddings, movie_metadata):
        g = primary_genre_from_meta(meta)
        sums[g] += emb
        counts[g] += 1

    centroids = []
    genres = []
    sizes = []
    for g, vec_sum in sums.items():
        c = counts[g]
        if c >= min_count:
            centroids.append(vec_sum / c)
            genres.append(g)
            sizes.append(c)

    centroids = np.stack(centroids, axis=0)
    sizes = np.asarray(sizes, dtype=np.int32)
    return centroids, genres, sizes


# --- Simple primary-genre extraction from MovieLens-style "genre1|genre2|..." ---

GENRE_PRIORITY = [
    "Comedy", "Drama", "Action", "Adventure", "Romance",
    "Horror", "Sci-Fi", "Thriller", "Animation",
    "Documentary", "Family", "Crime"
]

def primary_genre(genres_str: str) -> str:
    if not genres_str or not isinstance(genres_str, str):
        return "Unknown"
    genres = [g.strip() for g in genres_str.split("|") if g.strip()]
    if not genres:
        return "Unknown"
    # Prefer some broad genres to avoid tons of tiny categories
    for g in GENRE_PRIORITY:
        if g in genres:
            return g
    return genres[0]


def build_genre_colors(movie_metadata):
    """
    Map each movie to a primary genre and each genre to an integer color id.
    Returns:
      genre_ids: np.ndarray[int] shape (num_movies,)
      genre_to_id: dict[str, int]
    """
    genres = [primary_genre(m.get("genres", "")) for m in movie_metadata]
    unique = sorted(set(genres))
    genre_to_id = {g: i for i, g in enumerate(unique)}
    ids = np.array([genre_to_id[g] for g in genres], dtype=int)
    return ids, genre_to_id



# ----------------- Paths -----------------

RECOMMENDER_LOG_PATH = Path(__file__).parent / "rec_log.jsonl"


# ----------------- PCA helper -----------------

def pca_2d(X: np.ndarray) -> np.ndarray:
    """
    Project embeddings X (N x D) into 2D using PCA via SVD.

    Returns:
        X_2d: (N x 2) array
    """
    X = np.asarray(X, dtype=np.float32)
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    components = Vt[:2]  # (2, D)
    X_2d = X_centered @ components.T  # (N, 2)
    return X_2d


# ----------------- Log loading helpers -----------------

def load_log_records(user_id: str) -> List[Dict[str, Any]]:
    """
    Load all records from rec_log.jsonl for a specific user_id,
    sorted by msg_index ascending.
    """
    if not RECOMMENDER_LOG_PATH.exists():
        raise FileNotFoundError(
            f"{RECOMMENDER_LOG_PATH} does not exist. "
            "Make sure you've run the recommender with persistent user IDs first."
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
            # Keep only records that have msg_index and user_vec
            if "msg_index" not in rec or "user_vec" not in rec:
                continue
            records.append(rec)

    if not records:
        raise ValueError(
            f"No log records found for user_id='{user_id}' in {RECOMMENDER_LOG_PATH}"
        )

    # sort by msg_index
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
        return records[-1]  # already sorted by msg_index

    for rec in records:
        if int(rec.get("msg_index", -1)) == msg_index:
            return rec

    raise ValueError(
        f"No record with msg_index={msg_index} found for this user. "
        f"Available msg_index values: {[r['msg_index'] for r in records]}"
    )


# ----------------- Plotting helpers -----------------

def build_projection_from_log_record(
    log_rec: Dict[str, Any],
    movie_embeddings: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Given one log record, build the necessary arrays for plotting:

    Returns:
        user_vec: (D,)
        movies_2d: (N, 2)
        user_2d: (2,)
        rec_2d: (K, 2)  where K = log_rec["final_k"]
    """
    user_vec = np.array(log_rec["user_vec"], dtype=np.float32)
    candidate_indices = np.array(log_rec["candidate_indices"], dtype=int)
    final_k = int(log_rec["final_k"])
    rec_indices = candidate_indices[:final_k]

    # Project all movies + this user_vec into 2D
    X = np.vstack([movie_embeddings, user_vec[None, :]])  # (N+1, D)
    X_2d = pca_2d(X)
    movies_2d = X_2d[:-1]
    user_2d = X_2d[-1]
    rec_2d = movies_2d[rec_indices]

    return user_vec, movies_2d, user_2d, rec_2d


def plot_user_vs_movies(
    user_id: str,
    msg_index: int,
    movies_2d: np.ndarray,
    user_2d: np.ndarray,
    rec_indices: np.ndarray,
    rec_2d: np.ndarray,
    movie_metadata,
    out_path: Path,
) -> None:
    """
    Plot:
      - all movies as light points
      - user taste as star
      - top recommendations as highlighted points + text labels
      - dashed lines from user to each recommendation
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # All movies
    ax.scatter(
        movies_2d[:, 0],
        movies_2d[:, 1],
        s=5,
        alpha=0.15,
        label="Movies (all)",
    )

    # User taste vector
    ax.scatter(
        user_2d[0],
        user_2d[1],
        s=120,
        marker="*",
        edgecolor="black",
        linewidth=1.0,
        label=f"User '{user_id}' taste (msg {msg_index})",
    )

    # Top recommendations
    ax.scatter(
        rec_2d[:, 0],
        rec_2d[:, 1],
        s=60,
        marker="o",
        edgecolor="black",
        linewidth=1.0,
        label=f"Top {len(rec_indices)} recommendations",
    )

    # Lines + small text labels
    for i, movie_idx in enumerate(rec_indices):
        x, y = rec_2d[i]
        meta = movie_metadata[movie_idx]
        title = (
            meta.get("title")
            or meta.get("tmdb_title")
            or f"movie_{movie_idx}"
        )
        short_title = (title[:22] + "…") if len(title) > 25 else title

        # Line from user to rec
        ax.plot(
            [user_2d[0], x],
            [user_2d[1], y],
            linestyle="--",
            linewidth=0.8,
            alpha=0.4,
        )

        # Label
        ax.text(
            x + 0.5,
            y,
            short_title,
            fontsize=7,
            alpha=0.8,
        )

    ax.set_title(f"User vs Movie Embedding Space (user='{user_id}', msg={msg_index})")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_user_vs_movies_with_genres(
    user_id: str,
    msg_idx: int,
    user_vec: np.ndarray,
    rec_indices: list[int],
    movie_embeddings: np.ndarray,
    movie_metadata: list[dict],
    out_path: Path,
):
    """
    PCA projection of movie embedding space:

      • Movies colored by primary genre
      • User taste vector as a star
      • Top-5 recommendations as green dots with labels
    """
    # ---------- PCA to 2D ----------
    pca = PCA(n_components=2, random_state=0)
    movies_2d = pca.fit_transform(movie_embeddings)

    user_2d = pca.transform(user_vec.reshape(1, -1))[0]
    rec_2d = movies_2d[rec_indices]

    # ---------- Genre colors ----------
    genre_ids, genre_to_id = build_genre_colors(movie_metadata)
    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(10, 7))

    # All movies, colored by primary genre
    sc = ax.scatter(
        movies_2d[:, 0],
        movies_2d[:, 1],
        c=genre_ids,
        cmap=cmap,
        s=6,
        alpha=0.35,
        linewidths=0,
        label="Movies (all)",
    )

    # User taste
    ax.scatter(
        user_2d[0],
        user_2d[1],
        marker="*",
        s=220,
        edgecolor="black",
        facecolor="orange",
        linewidths=1.0,
        label=f"User '{user_id}' taste (msg {msg_idx})",
        zorder=5,
    )

    # Top-5 recommendations
    ax.scatter(
        rec_2d[:, 0],
        rec_2d[:, 1],
        s=80,
        edgecolor="black",
        facecolor="limegreen",
        linewidths=1.0,
        label="Top 5 recommendations",
        zorder=6,
    )

    # ---------- Label recommended movies (shortened titles) ----------
    for idx in rec_indices:
        x, y = movies_2d[idx]
        title = movie_metadata[idx].get("title", "(unknown)")
        short = textwrap.shorten(title, width=25, placeholder="…")
        ax.text(
            x + 0.01,
            y + 0.01,
            short,
            fontsize=7,
            ha="left",
            va="bottom",
        )

    # ---------- Genre legend (limit to first ~10 to avoid clutter) ----------
    handles = []
    for genre, gid in list(genre_to_id.items())[:10]:
        color = cmap(gid)
        handles.append(Patch(facecolor=color, label=genre, alpha=0.7))
    genre_legend = ax.legend(
        handles,
        [h.get_label() for h in handles],
        title="Primary genre",
        loc="upper left",
        fontsize=8,
    )
    ax.add_artist(genre_legend)

    # Overlay second legend for user + rec markers
    ax.legend(loc="lower right", fontsize=8)

    ax.set_title(f"User vs Movie Embedding Space (user='{user_id}', msg={msg_idx})")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[viz] Saved {out_path}")

def plot_genre_map_with_user_and_recs(
    user_id: str,
    msg_idx: int | None,
    user_vec: np.ndarray,
    rec_indices: list[int],
    movie_embeddings: np.ndarray,
    movie_metadata: list[dict],
    out_path: Path,
):
    """
    Plot in 2D:
      • one point per genre (centroid of its movies in embedding space)
      • point size ∝ # movies in the genre
      • user taste vector as a star
      • top-5 recommended movies as green dots with labels
    """

    # ---------- 1) genre centroids ----------
    genre_centroids, genres, sizes = compute_genre_centroids(
        movie_embeddings, movie_metadata, min_count=30
    )

    # top-5 rec embeddings
    rec_embs = movie_embeddings[rec_indices]

    # ---------- 2) PCA on (genre centroids + user + recs) ----------
    X = np.vstack([genre_centroids, user_vec.reshape(1, -1), rec_embs])
    pca = PCA(n_components=2, random_state=0)
    X2 = pca.fit_transform(X)

    G = genre_centroids.shape[0]
    genre_2d = X2[:G]
    user_2d = X2[G]         # single row
    rec_2d  = X2[G+1:]      # k rows

    # ---------- 3) plot ----------
    fig, ax = plt.subplots(figsize=(10, 7))

    # sizes: use sqrt so huge genres don't dominate
    size_scaled = 40 * np.sqrt(sizes / sizes.max())

    scatter = ax.scatter(
        genre_2d[:, 0],
        genre_2d[:, 1],
        s=size_scaled,
        c=np.arange(G),
        cmap="tab20",
        alpha=0.8,
        edgecolor="black",
        linewidths=0.5,
    )

    # annotate genres
    for (x, y), g in zip(genre_2d, genres):
        ax.text(
            x + 0.01,
            y + 0.01,
            g,
            fontsize=8,
            ha="left",
            va="bottom",
        )

    # user taste
    ax.scatter(
        user_2d[0],
        user_2d[1],
        marker="*",
        s=260,
        edgecolor="black",
        facecolor="orange",
        linewidths=1.0,
        label=f"user '{user_id}' taste",
        zorder=5,
    )

    # top-5 recs
    ax.scatter(
        rec_2d[:, 0],
        rec_2d[:, 1],
        s=100,
        edgecolor="black",
        facecolor="limegreen",
        linewidths=1.0,
        label="top-5 recommendations",
        zorder=6,
    )

    # label each recommended movie with a short title
    for idx, (x, y) in zip(rec_indices, rec_2d):
        title = movie_metadata[idx].get("title", "(unknown)")
        short = textwrap.shorten(title, width=30, placeholder="…")
        ax.text(
            x + 0.015,
            y - 0.01,
            short,
            fontsize=7,
            ha="left",
            va="top",
        )

    ax.set_title(f"Genre-level taste map (user='{user_id}', msg={msg_idx})")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[viz] Saved {out_path}")



def plot_genre_histogram(
    rec_indices: np.ndarray,
    movie_metadata,
    out_path: Path,
) -> None:
    """
    Build a simple histogram of genres for the recommended movies.
    Uses 'tmdb_genres' if present, otherwise falls back to 'genres'.
    """
    genre_counts = Counter()

    for idx in rec_indices:
        meta = movie_metadata[idx]
        raw = (
            meta.get("tmdb_genres")
            or meta.get("genres")
            or ""
        )

        if not raw:
            continue

        if "|" in raw:
            parts = [g.strip() for g in raw.split("|")]
        else:
            parts = [g.strip() for g in raw.split(",")]

        for g in parts:
            if g:
                genre_counts[g] += 1

    if not genre_counts:
        print("[visualize] No genres found for recommendations; skipping genre histogram.")
        return

    labels, values = zip(
        *sorted(genre_counts.items(), key=lambda x: -x[1])
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_title("Genre Histogram of Top Recommendations")
    ax.set_ylabel("Count")
    ax.set_xlabel("Genre")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ----------------- CLI entrypoint -----------------

def main():
    parser = argparse.ArgumentParser(
        description="Visualize user taste vs movie embedding space from rec_log.jsonl."
    )
    parser.add_argument(
        "--user-id",
        type=str,
        required=True,
        help="User ID to visualize (must exist in rec_log.jsonl).",
    )
    parser.add_argument(
        "--msg-index",
        type=int,
        default=None,
        help="Message index (per-user) to visualize. If omitted, uses latest.",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="figures",
        help="Output directory for plots (default: figures).",
    )

    args = parser.parse_args()
    user_id = args.user_id
    msg_index = args.msg_index
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load log records for this user
    print(f"[visualize] Loading log records for user_id='{user_id}'…")
    records = load_log_records(user_id)
    log_rec = pick_record_for_visualization(records, msg_index=msg_index)
    actual_msg_index = int(log_rec["msg_index"])

    print(f"[visualize] Using msg_index={actual_msg_index} (timestamp={log_rec['timestamp']})")

    # Load movie embeddings + metadata
    print("[visualize] Loading movie embeddings…")
    movie_embeddings, movie_metadata = load_movie_embeddings(MOVIE_EMBED_PATH)

    # Build projections
    user_vec, movies_2d, user_2d, rec_2d = build_projection_from_log_record(
        log_rec, movie_embeddings
    )

    candidate_indices = np.array(log_rec["candidate_indices"], dtype=int)
    final_k = int(log_rec["final_k"])
    rec_indices = candidate_indices[:final_k]

    # 1 & 2) Embedding map + Top-K overlay
    map_path = out_dir / f"{user_id}_msg{actual_msg_index}_embedding_map.png"
    print(f"[visualize] Saving embedding map with recommendations to {map_path}")
    plot_user_vs_movies(
        user_id=user_id,
        msg_index=actual_msg_index,
        movies_2d=movies_2d,
        user_2d=user_2d,
        rec_indices=rec_indices,
        rec_2d=rec_2d,
        movie_metadata=movie_metadata,
        out_path=map_path,
    )

    out_path = out_dir / f"{user_id}_msg{msg_index}_genre_map.png"

    plot_genre_map_with_user_and_recs(
        user_id=user_id,
        msg_idx=msg_index,
        user_vec=user_vec,          # from log
        rec_indices=rec_indices,    # from log
        movie_embeddings=movie_embeddings,
        movie_metadata=movie_metadata,
        out_path=out_path,
    )


    # After you’ve loaded:
    #   movie_embeddings, movie_metadata = load_movie_embeddings(...)
    #   log_entry = ...  # from your rec_log.json
    #   user_vec = np.array(log_entry["user_vec"], dtype=np.float32)
    #   rec_indices = log_entry["rec_indices"]

    out_path = out_dir / f"{user_id}_msg{msg_index}_embedding_genres.png"
    plot_user_vs_movies_with_genres(
        user_id=user_id,
        msg_idx=msg_index,
        user_vec=user_vec,
        rec_indices=rec_indices,
        movie_embeddings=movie_embeddings,
        movie_metadata=movie_metadata,
        out_path=out_path,
    )


    # 3) Genre histogram
    hist_path = out_dir / f"{user_id}_msg{actual_msg_index}_genre_hist.png"
    print(f"[visualize] Saving genre histogram to {hist_path}")
    plot_genre_histogram(
        rec_indices=rec_indices,
        movie_metadata=movie_metadata,
        out_path=hist_path,
    )

    print("[visualize] Done.")


if __name__ == "__main__":
    main()
