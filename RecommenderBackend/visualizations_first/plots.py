# visualizations/plots.py
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from sklearn.decomposition import PCA
import textwrap

from .utils import primary_genre_from_meta


# ---------- 1) Basic global embedding map (all movies + user + recs) ----------

def plot_embedding_map(
    user_id: str,
    msg_index: int,
    movies_2d: np.ndarray,
    user_2d: np.ndarray,
    rec_indices: np.ndarray,
    rec_2d: np.ndarray,
    movie_metadata: List[Dict],
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(
        movies_2d[:, 0],
        movies_2d[:, 1],
        s=5,
        alpha=0.15,
        label="Movies (all)",
    )

    ax.scatter(
        user_2d[0],
        user_2d[1],
        s=140,
        marker="*",
        edgecolor="black",
        linewidth=1.0,
        label=f"User '{user_id}' taste (msg {msg_index})",
    )

    ax.scatter(
        rec_2d[:, 0],
        rec_2d[:, 1],
        s=70,
        marker="o",
        edgecolor="black",
        linewidth=1.0,
        label=f"Top {len(rec_indices)} recommendations",
    )

    for i, movie_idx in enumerate(rec_indices):
        x, y = rec_2d[i]
        meta = movie_metadata[movie_idx]
        title = meta.get("title") or meta.get("tmdb_title") or f"movie_{movie_idx}"
        short = (title[:22] + "…") if len(title) > 25 else title

        ax.plot(
            [user_2d[0], x],
            [user_2d[1], y],
            linestyle="--",
            linewidth=0.8,
            alpha=0.4,
        )
        ax.text(x + 0.4, y, short, fontsize=7, alpha=0.8)

    ax.set_title(f"User vs Movie Embedding Space (user='{user_id}', msg={msg_index})")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(loc="best", fontsize=8)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------- 2) Local neighborhood plot with genres (NEW, more useful) ----------

def plot_local_neighborhood_with_genres(
    user_id: str,
    msg_idx: int | None,
    user_vec: np.ndarray,
    rec_indices: List[int],
    movie_embeddings: np.ndarray,
    movie_metadata: List[Dict],
    out_path: Path,
    n_local: int = 800,
) -> None:
    """
    Local 2D view around the user embedding:

      • take N movies most similar to user_vec
      • color them by primary genre
      • overlay user taste (star) + top-K recs (green dots) with labels
    """

    # --- 1) cosine similarity + local neighborhood ---
    movie_norms = np.linalg.norm(movie_embeddings, axis=1, keepdims=True) + 1e-8
    movie_normed = movie_embeddings / movie_norms
    user_normed = user_vec / (np.linalg.norm(user_vec) + 1e-8)

    sims = movie_normed @ user_normed  # [N_movies]

    n_local = min(n_local, movie_embeddings.shape[0])
    idx_local = np.argpartition(-sims, n_local - 1)[:n_local]
    idx_local = idx_local[np.argsort(-sims[idx_local])]

    local_embs = movie_embeddings[idx_local]
    local_meta = [movie_metadata[i] for i in idx_local]

    # --- 2) PCA on (local movies + user + recs) ---
    rec_embs = movie_embeddings[rec_indices]

    X = np.vstack([local_embs, user_vec.reshape(1, -1), rec_embs])
    pca = PCA(n_components=2, random_state=0)
    X2 = pca.fit_transform(X)

    n_movies_local = local_embs.shape[0]
    movies_2d = X2[:n_movies_local]
    user_2d = X2[n_movies_local]
    recs_2d = X2[n_movies_local + 1 :]

    # --- 3) genre colors for local movies ---
    genres = [primary_genre_from_meta(m) for m in local_meta]
    unique_genres = sorted(set(genres))
    cmap = plt.get_cmap("tab20")
    color_map = {g: cmap(i % 20) for i, g in enumerate(unique_genres)}
    colors = [color_map[g] for g in genres]

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.scatter(
        movies_2d[:, 0],
        movies_2d[:, 1],
        c=colors,
        s=12,
        alpha=0.6,
        linewidths=0,
    )

    handles = []
    labels = []
    for g in unique_genres:
        handles.append(
            plt.Line2D(
                [], [], marker="o", linestyle="None",
                markerfacecolor=color_map[g], markeredgecolor="none"
            )
        )
        labels.append(g)
    genre_legend = ax.legend(
        handles, labels,
        title="Genres (local neighborhood)",
        loc="upper left",
        fontsize=8,
    )
    ax.add_artist(genre_legend)

    # --- 4) user taste + recs ---
    ax.scatter(
        user_2d[0],
        user_2d[1],
        marker="*",
        s=260,
        edgecolor="black",
        facecolor="orange",
        linewidths=1.0,
        label=f"user '{user_id}'",
        zorder=4,
    )

    ax.scatter(
        recs_2d[:, 0],
        recs_2d[:, 1],
        s=90,
        edgecolor="black",
        facecolor="limegreen",
        linewidths=1.0,
        label="top recommendations",
        zorder=5,
    )

    for idx, (x, y) in zip(rec_indices, recs_2d):
        title = movie_metadata[idx].get("title", "(unknown)")
        short = textwrap.shorten(title, width=30, placeholder="…")
        ax.text(x + 0.015, y - 0.01, short, fontsize=7, ha="left", va="top", zorder=6)

    ax.set_title(f"Local taste map (user='{user_id}', msg={msg_idx})")
    ax.set_xlabel("PC1 (local)")
    ax.set_ylabel("PC2 (local)")
    ax.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[viz] Saved {out_path}")


# ---------- 3) Genre histogram of top-K recs ----------

def plot_genre_histogram(
    rec_indices: np.ndarray,
    movie_metadata: List[Dict],
    out_path: Path,
) -> None:
    genre_counts = Counter()

    for idx in rec_indices:
        meta = movie_metadata[idx]
        raw = meta.get("tmdb_genres") or meta.get("genres") or ""
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
        print("[viz] No genres found; skipping histogram.")
        return

    labels, values = zip(*sorted(genre_counts.items(), key=lambda x: -x[1]))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_title("Genre Histogram of Top Recommendations")
    ax.set_ylabel("Count")
    ax.set_xlabel("Genre")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[viz] Saved {out_path}")
