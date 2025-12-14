# 🎬 TasteEmbeddingGenerator
## Unified Movie & User Taste Embedding Pipeline for Conversational Recommendation Systems

TasteEmbeddingGenerator is an end-to-end embedding pipeline that constructs:
- Movie semantic embeddings from multi-source metadata
- User taste embeddings from ratings + dialogue behavior

This module powers the LLM-Driven Conversational Movie Recommendation & Taste Graph System by creating a unified embedding space for retrieval, similarity search, and recommendation.

---

## 📦 Directory Structure
```
TasteEmbeddingGenerator/
│
├── artifacts/                     # Saved movie/user embeddings (.parquet)
├── artifacts_huggingface/         # Embeddings using HF models (optional)
│
├── src/
│   ├── download_artifacts.sh      # Downloader for pretrained embeddings
│   └── ...                        
│
├── embeddings_backend.py          # Backend abstraction + ST/OpenAI backends
├── MovieEmbedding.py              # Movie embedding generator
├── UserEmbedding.py               # User embedding generator
├── Generator.py                   # High-level orchestration module
├── analysis.py                    # Quantitative evaluation (genre gap, hitrate)
├── comparison.py                  # Backend comparison utilities
├── test_generator.py              # Sanity test script
└── README.md
```

---

## ✨ Overview
TasteEmbeddingGenerator produces two core embedding spaces:

### 1. Movie Embeddings
Created from TMDB-enriched metadata from:
- MovieLens
- MovieTweetings
- INSPIRED Movie DB

#### Movie Text Construction
Each movie is converted into a unified natural-language description:

```
Title: The Matrix (1999).
Genres: Action, Sci-Fi.
Plot: A hacker discovers the nature of reality...
Cast: Keanu Reeves, Laurence Fishburne.
Keywords: cyberpunk, dystopia.
```

#### Duplicate Handling
- Primary key: tmdb_id
- Fallback: source:movie_id

→ Ensures identical movies across different datasets share a single embedding vector.

#### Embedding Backends
Pluggable encoder system supporting:
| Backend                      | Notes                                  |
| ---------------------------- | -------------------------------------- |
| `SentenceTransformerBackend` | Uses **BAAI/bge-base-en-v1.5** (local) |
| `OpenAIEmbeddingBackend`     | Uses **text-embedding-3-large**        |

As follow:
```python
BaseEmbeddingBackend.embed_texts(texts: List[str])
```

#### Output
Stored at:
```
TasteEmbeddingGenerator/artifacts/movie_embeddings.parquet
```
Contains:
- movie_id
- source
- metadata fields
- embedding_text
- embedding (vector)

### 2. User Taste Embeddings
User embeddings fuse implicit signals (ratings) and explicit signals (dialogue preferences)
#### A) Rating-based User Embedding
1. Load MovieLens ratings
2. Keep movies with rating ≥ 4.0
3. Group by userId
4. Keep users with at least 3 liked movies
5. Convert liked movie IDs → movie embeddings
6. Final user vector = mean(movie embedding vectors)

This produces a preference centroid vector representing the types of movies a user enjoys.

#### B) Text-based User Embedding
From dialogue datasets:
- CCPE
- ReDial
- INSPIRED dialogs

Process:
1. Identify user via speaker_id or dialog_id
2. Gather all utterances
3. Flatten into a user-level text profile
4. Encode profile using same embedding backend

#### C) α-Mix Fusion (Hybrid Final Embedding)
For each user:
```python
final = α * rating_vec + (1 - α) * text_vec
```
- Default α = 0.7 (rating-weighted)
- If one side missing → use the other

Output stored at:
```
TasteEmbeddingGenerator/artifacts/user_embeddings.parquet
```

---

## 🧪 Evaluation Metrics
### 1. Genre Separation Gap
- Computes distance between same-genre vs different-genre movie pairs
- Uses relative gap (embedding scales differ between models)
- OpenAI embeddings show significantly stronger separation

### 2. HitRate@10 (Recommendation Capability)
Random recommendation benchmark:
| Backend              | HitRate@10 |
| -------------------- | ---------- |
| **OpenAI embedding** | **0.164**  |
| **BGE-base**         | ~0.03      |

→ OpenAI ≈ 5× improvement over baseline.

---


Choose backend via config:
```python
cfg = TasteEmbeddingConfig(
    backend_type="sentence-transformers",  # or "openai"
    model_name="BAAI/bge-base-en-v1.5"
)
```

---

## 🚀 Usage
### Run Entire Pipeline
```bash
python -m TasteEmbeddingGenerator.Generator
```

### Generate Only User Embeddings
```python
from TasteEmbeddingGenerator.Generator import TasteEmbeddingGenerator
gen = TasteEmbeddingGenerator(cfg)
gen.build_user_embeddings(movie_emb_path)
```

---

## 🧰 Configuration Example
```python
cfg = TasteEmbeddingConfig(
    project_root=Path("."),
    backend_type="openai",                 # or "sentence-transformers"
    model_name="BAAI/bge-base-en-v1.5",
    openai_model="text-embedding-3-large",
    movie_sources=["movielens", "movietweetings", "inspired"],
    batch_size=64,
    rating_threshold=4.0,
    min_movies=3,
)
```

---

## 🔗 Artifacts (Movie/User Embeddings)
Due to size limits, generated embedding files are stored externally:

Google Drive folders:

- HuggingFace embeddings
https://drive.google.com/drive/folders/1mseNC_7f8Iy4pLJj977qSO9bo2YWlF7n

- OpenAI embeddings
https://drive.google.com/drive/folders/1emBZb4zts0d7ca0_4es1WDfba7HNp3E7

Auto-download:
```bash
bash ./TasteEmbeddingGenerator/src/download_artifacts.sh
```