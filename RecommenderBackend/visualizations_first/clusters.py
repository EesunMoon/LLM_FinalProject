# from __future__ import annotations

# from collections import Counter, defaultdict
# from pathlib import Path
# from typing import List, Dict

# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.cluster import MiniBatchKMeans
# from sklearn.decomposition import PCA
# import textwrap

# from .utils import primary_genre_from_meta


# def cluster_movies(
#     movie_embeddings: np.ndarray,
#     movie_metadata: List[Dict],
#     n_clusters: int = 25,
#     random_state: int = 0,
# ):
#     """
#     Run k-means on movie embeddings and compute per-cluster genre summaries.

#     Returns:
#         labels:        np.ndarray [N_movies] cluster index per movie
#         centers:       np.ndarray [K, D]     cluster centroids
#         cluster_names: dict[int, str]        human label (major genre(s))
#         cluster_sizes: np.ndarray [K]        #movies in each cluster
#     """
#     print(f"[clusters] Running MiniBatchKMeans with K={n_clusters}…")
#     kmeans = MiniBatchKMeans(
#         n_clusters=n_clusters,
#         random_state=random_state,
#         batch_size=2048,
#         n_init="auto",
#     )
#     labels = kmeans.fit_predict(movie_embeddings)
#     centers = kmeans.cluster_centers_

#     # Build genre histograms per cluster
#     genre_counts_by_cluster: Dict[int, Counter] = defaultdict(Counter)
#     for lbl, meta in zip(labels, movie_metadata):
#         g = primary_genre_from_meta(meta)
#         genre_counts_by_cluster[int(lbl)][g] += 1

#     cluster_names: Dict[int, str] = {}
#     cluster_sizes = np.zeros(n_clusters, dtype=int)

#     for k in range(n_clusters):
#         counter = genre_counts_by_cluster.get(k, Counter())
#         cluster_sizes[k] = sum(counter.values())
#         if not counter:
#             cluster_names[k] = "Unknown"
#             continue
#         top = counter.most_common(3)
#         main = top[0][0]
#         # Optional: show up to 2 co-dominant genres
#         others = [g for g, _ in top[1:3]]
#         if others:
#             cluster_names[k] = main + " / " + ", ".join(others)
#         else:
#             cluster_names[k] = main

#     print(f"[clusters] Done. Cluster sizes (min/max): "
#           f"{cluster_sizes.min()} / {cluster_sizes.max()}")
#     return labels, centers, cluster_names, cluster_sizes


# def plot_cluster_overview_with_user(
#     user_id: str,
#     msg_idx: int | None,
#     user_vec: np.ndarray,
#     rec_indices: List[int],
#     movie_embeddings: np.ndarray,
#     movie_metadata: List[Dict],
#     out_path: Path,
#     n_clusters: int = 25,
# ):
#     """
#     2D cluster-level view:

#       • Each point = cluster centroid (colored dot, size ∝ #movies)
#       • Cluster label = majority genre(s) in that cluster
#       • User taste = star
#       • Top-K recommendations = green dots, placed using same PCA,
#         with a line from user to each rec and cluster id in the label.
#     """
#     labels, centers, cluster_names, cluster_sizes = cluster_movies(
#         movie_embeddings, movie_metadata, n_clusters=n_clusters
#     )

#     # Which cluster does each recommended movie belong to?
#     rec_labels = labels[rec_indices]

#     # PCA on cluster centers + user + recs (aggregated view)
#     rec_embs = movie_embeddings[rec_indices]
#     X = np.vstack([centers, user_vec.reshape(1, -1), rec_embs])
#     pca = PCA(n_components=2, random_state=0)
#     X2 = pca.fit_transform(X)

#     K = centers.shape[0]
#     centers_2d = X2[:K]
#     user_2d = X2[K]
#     recs_2d = X2[K + 1 :]

#     # Sizes: sqrt so so-huge clusters don't dominate visually
#     size_scaled = 50 * np.sqrt(cluster_sizes / cluster_sizes.max().clip(min=1))

#     cmap = plt.get_cmap("tab20")

#     fig, ax = plt.subplots(figsize=(10, 7))

#     # Clusters as colored bubbles
#     for k in range(K):
#         x, y = centers_2d[k]
#         color = cmap(k % 20)
#         ax.scatter(
#             x,
#             y,
#             s=size_scaled[k],
#             color=color,
#             alpha=0.8,
#             edgecolor="black",
#             linewidths=0.5,
#             zorder=1,
#         )
#         # Shorten label a bit
#         label = textwrap.shorten(cluster_names[k], width=20, placeholder="…")
#         ax.text(
#             x + 0.01,
#             y + 0.01,
#             label,
#             fontsize=7,
#             ha="left",
#             va="bottom",
#             alpha=0.9,
#         )

#     # User taste
#     ax.scatter(
#         user_2d[0],
#         user_2d[1],
#         marker="*",
#         s=260,
#         edgecolor="black",
#         facecolor="orange",
#         linewidths=1.0,
#         label=f"user '{user_id}' taste",
#         zorder=3,
#     )

#     # Recommendations
#     ax.scatter(
#         recs_2d[:, 0],
#         recs_2d[:, 1],
#         s=120,
#         edgecolor="black",
#         facecolor="limegreen",
#         linewidths=1.0,
#         label="top recommendations",
#         zorder=4,
#     )

#     # Lines & labels for recs showing their cluster id/name
#     for (x, y), midx, cl in zip(recs_2d, rec_indices, rec_labels):
#         meta = movie_metadata[midx]
#         title = meta.get("title") or meta.get("tmdb_title") or f"movie_{midx}"
#         short_title = textwrap.shorten(title, width=25, placeholder="…")
#         cluster_label = textwrap.shorten(cluster_names[int(cl)], width=18, placeholder="…")

#         ax.plot(
#             [user_2d[0], x],
#             [user_2d[1], y],
#             linestyle="--",
#             linewidth=0.8,
#             alpha=0.5,
#             color="gray",
#             zorder=2,
#         )

#         ax.text(
#             x + 0.02,
#             y - 0.01,
#             f"{short_title}\n(c{int(cl)}: {cluster_label})",
#             fontsize=7,
#             ha="left",
#             va="top",
#             zorder=5,
#         )

#     ax.set_title(f"Cluster-level taste map (user='{user_id}', msg={msg_idx})")
#     ax.set_xlabel("PC1 (clusters)")
#     ax.set_ylabel("PC2 (clusters)")
#     ax.legend(loc="lower right", fontsize=8)

#     fig.tight_layout()
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     fig.savefig(out_path, dpi=200)
#     plt.close(fig)
#     print(f"[clusters] Saved {out_path}")

# visualizations/clusters.py
from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA

from .genres import primary_genre_from_meta, majority_primary_genre, build_genre_color_map


def _cluster_movies(
    movie_embeddings: np.ndarray,
    movie_metadata: List[dict],
    n_clusters: int = 25,
):
    """
    Cluster all movies and attach a majority primary genre to each cluster.

    Returns:
      labels:        (N,) int array, cluster id for each movie
      centroids:     (C, D) array, cluster centers in embedding space
      cluster_genre: list[str] length C, majority primary genre per cluster
      cluster_sizes: (C,) int array, #movies per cluster
    """
    N, D = movie_embeddings.shape

    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        batch_size=min(8192, N),
        random_state=0,
        verbose=False,
    )
    labels = kmeans.fit_predict(movie_embeddings)
    centroids = kmeans.cluster_centers_

    cluster_genre: List[str] = []
    cluster_sizes: List[int] = []

    for cid in range(n_clusters):
        idxs = np.where(labels == cid)[0].tolist()
        cluster_sizes.append(len(idxs))
        if not idxs:
            cluster_genre.append("Unknown")
        else:
            g = majority_primary_genre(idxs, movie_metadata)
            cluster_genre.append(g)

    return labels, centroids, np.asarray(cluster_sizes, dtype=int), cluster_genre


def plot_cluster_overview_with_user(
    user_id: str,
    msg_idx: int | None,
    user_vec: np.ndarray,
    rec_indices: List[int],
    movie_embeddings: np.ndarray,
    movie_metadata: List[dict],
    out_path: Path,
    n_clusters: int = 25,
) -> None:
    """
    Cluster-level taste map:

      • One point per cluster (centroid in embedding space)
      • Cluster colored by its majority primary genre (from tmdb_genres/genres)
      • User taste vector as an orange star
      • Top-K recommendations as green points with labels
        (each labelled with its cluster's majority genre)

    Distances here are only approximate because we compress to 2D with PCA,
    but it should give an intuitive 'which regions of taste space' you live in.
    """
    user_vec = np.asarray(user_vec, dtype=np.float32)

    # ---- 1) cluster movies ----
    labels, centroids, cluster_sizes, cluster_genre = _cluster_movies(
        movie_embeddings, movie_metadata, n_clusters=n_clusters
    )

    # ---- 2) build 2D PCA projection on centroids + user + recs ----
    rec_indices = np.asarray(rec_indices, dtype=int)
    rec_embs = movie_embeddings[rec_indices]

    X = np.vstack([centroids, user_vec[None, :], rec_embs])
    pca = PCA(n_components=2, random_state=0)
    X2 = pca.fit_transform(X)

    C = centroids.shape[0]
    centroids_2d = X2[:C]
    user_2d = X2[C]
    rec_2d = X2[C + 1 :]

    # ---- 3) genre colors for clusters ----
    # cluster_genre is already one primary genre per cluster
    color_map = build_genre_color_map(cluster_genre)

    cluster_colors = [color_map[g] for g in cluster_genre]

    # ---- 4) plot ----
    fig, ax = plt.subplots(figsize=(10, 7))

    # cluster centroids
    sc = ax.scatter(
        centroids_2d[:, 0],
        centroids_2d[:, 1],
        s=30 + 10 * np.sqrt(cluster_sizes / cluster_sizes.max()),
        c=cluster_colors,
        alpha=0.8,
        edgecolor="black",
        linewidths=0.5,
        label="Clusters",
        zorder=1,
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
        zorder=3,
    )

    # recommendations
    ax.scatter(
        rec_2d[:, 0],
        rec_2d[:, 1],
        s=120,
        edgecolor="black",
        facecolor="limegreen",
        linewidths=1.0,
        label="top recommendations",
        zorder=4,
    )

    # dashed lines from user to recs + labels
    for idx, (x, y) in zip(rec_indices, rec_2d):
        # link from user to recommendation
        ax.plot(
            [user_2d[0], x],
            [user_2d[1], y],
            linestyle="--",
            color="gray",
            linewidth=0.8,
            alpha=0.5,
            zorder=2,
        )

        meta = movie_metadata[idx]
        title = meta.get("title") or meta.get("tmdb_title") or f"movie_{idx}"
        # which cluster is this rec in?
        cid = int(labels[idx])
        g = cluster_genre[cid]
        label_text = f"{title}\n(c{cid}: {g})"

        ax.text(
            x + 0.015,
            y + 0.015,
            label_text,
            fontsize=7,
            ha="left",
            va="bottom",
        )

    # ---- 5) genre legend for clusters ----
    genre_names = sorted(set(cluster_genre))
    legend_handles = []
    for g in genre_names:
        color = color_map[g]
        legend_handles.append(Patch(facecolor=color, edgecolor="black", label=g))

    legend1 = ax.legend(
        handles=legend_handles,
        title="Cluster majority genre",
        loc="upper left",
        fontsize=8,
    )
    ax.add_artist(legend1)

    # secondary legend for user/recs
    ax.legend(loc="lower right", fontsize=8)

    ax.set_title(f"Cluster-level taste map (user='{user_id}', msg={msg_idx})")
    ax.set_xlabel("PC1 (clusters)")
    ax.set_ylabel("PC2 (clusters)")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"[viz] Saved {out_path}")
