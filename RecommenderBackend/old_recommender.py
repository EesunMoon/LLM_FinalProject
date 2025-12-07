# from __future__ import annotations

# from taste_parser import extract_structured_taste
# from embedding_loader import load_movie_embeddings, load_user_embeddings
# from vector_index import MovieIndex
# from llm import call_llm
# from config import MOVIE_EMBED_PATH, USER_EMBED_PATH, TOP_K, FINAL_K

# import numpy as np

# import sys
# from pathlib import Path


# import numpy as np

# from user_store import load_user_state, save_user_state


# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# sys.path.append(str(PROJECT_ROOT))

# from typing import Dict, Optional
# import numpy as np

# # Runtime user state (for “real” users during this session)
# # USER_STATE: Dict[str, dict] = {}
# # Map: user_id -> np.ndarray (taste vector)
# USER_STATE: dict[str, np.ndarray] = load_user_state()

# # How much to keep from previous taste vs. new message
# USER_FUSE_ALPHA = 0.8  # 0.8 old taste, 0.2 new message



# # ------------ LOAD ALL VECTORS -------------
# movie_embeddings, movie_metadata = load_movie_embeddings(MOVIE_EMBED_PATH)
# user_vectors = load_user_embeddings(USER_EMBED_PATH)
# # In-memory preference history for explanation (not persisted yet)
# preference_history: dict[str, list[str]] = {}


# movie_index = MovieIndex(movie_embeddings)

# # # ------------ COLD START TASTE EMBEDDING -------------
# # def embed_user_taste(text: str) -> np.ndarray:
# #     """
# #     TEMPORARY: replace with your SentenceTransformer backend
# #     """
# #     raise NotImplementedError("Plug in your taste embedding model here.")

# from TasteEmbeddingGenerator.embeddings_backend import SentenceTransformerBackend
# from TasteEmbeddingGenerator.Generator import TasteEmbeddingConfig

# # ---- Initialize backend ONCE ----
# # _cfg = TasteEmbeddingConfig(
# #     backend_type="sentence-transformers",
# #     model_name="BAAI/bge-base-en-v1.5"
# # )

# # _backend = SentenceTransformerBackend(_cfg)

# from pathlib import Path
# from TasteEmbeddingGenerator.embeddings_backend import SentenceTransformerBackend
# from TasteEmbeddingGenerator.Generator import TasteEmbeddingConfig

# # ---- Proper project root for your generator ----
# GENERATOR_ROOT = Path(__file__).resolve().parents[1] / "TasteEmbeddingGenerator"

# _cfg = TasteEmbeddingConfig(
#     project_root=str(GENERATOR_ROOT),
#     backend_type="sentence-transformers",
#     model_name="BAAI/bge-base-en-v1.5"
# )

# # _backend = SentenceTransformerBackend(_cfg)
# _backend = SentenceTransformerBackend(
#     model_name=_cfg.model_name,
#     device="mps"  # since you're on Mac
# )



# def embed_user_taste(text: str) -> np.ndarray:
#     # vec = _backend.embed_texts([text])[0]
#     # return np.array(vec, dtype="float32")
#     vec = _backend.embed_texts([text])[0]
#     vec = np.array(vec, dtype="float32")
#     vec /= np.linalg.norm(vec)
#     # return vec
#     return np.array(vec, dtype=np.float32)


# # CREATE A USER TASTE VECTOR
# def update_user_taste(user_id: Optional[str],
#                       taste_profile: str,
#                       new_vec: np.ndarray,
#                       alpha: float = 0.7) -> tuple[Optional[str], np.ndarray]:
#     """
#     Update or create a user taste vector.

#     - If user_id is None: we don't persist anything (pure cold start).
#     - If user_id is new: we store this vector as their initial taste.
#     - If user_id exists: we blend old + new (simple EMA).

#     Returns: (user_id, fused_vec)
#     """
#     if user_id is None:
#         # Pure cold start: just return the new vector, no persistence
#         return None, new_vec

#     if user_id not in USER_STATE:
#         # First time we see this id
#         USER_STATE[user_id] = {
#             "taste_vec": new_vec,
#             "history_text": taste_profile,
#         }
#         return user_id, new_vec

#     # Refine existing user taste by blending previous + new
#     prev_vec = USER_STATE[user_id]["taste_vec"]
#     fused = alpha * prev_vec + (1.0 - alpha) * new_vec

#     # Re-normalize
#     fused /= np.linalg.norm(fused)

#     USER_STATE[user_id]["taste_vec"] = fused
#     USER_STATE[user_id]["history_text"] += "\n" + taste_profile

#     return user_id, fused


# # ----------- Get clean taste profile for this user (persistent convo memory stability) -----
# from openai import OpenAI
# import os

# _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def extract_taste_with_llm(user_input: str) -> str:
#     """
#     Uses an LLM to convert raw user input into a clean taste profile string.
#     This minimizes prompt noise and standardizes embedding input.
#     """

#     system_prompt = """
# You are a preference extraction assistant for a movie recommender system.
# Your job is to rewrite the user's input as a clean, concise taste profile.
# Do NOT recommend movies.
# Only return the normalized preference description.
# """

#     response = _client.chat.completions.create(
#         model="gpt-4o-mini",  # cheapest + strong enough
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_input},
#         ],
#         temperature=0.2,
#     )

#     return response.choices[0].message.content.strip()




# # ------------ CORE RECOMMENDER -----------------

# # def recommend(user_input: str, user_id: Optional[str] = None):


# #     # ✅ CASE 1: KNOWN USER → USE STORED USER EMBEDDING
# #     if user_id is not None and user_id in user_vectors:
# #         user_vec = user_vectors[user_id]

# #     # ✅ CASE 2: NEW USER → EXTRACT TASTE + EMBED
# #     else:
# #         # taste_profile = extract_structured_taste(user_input)
# #         # user_vec = embed_user_taste(taste_profile)
# #         taste_profile = extract_taste_with_llm(user_input)
# #         # taste_profile = user_input
# #         new_vec = embed_user_taste(taste_profile)

# #         # Persist or not depending on user_id
# #         user_id, user_vec = update_user_taste(user_id, taste_profile, new_vec)


# #     # -------- MOVIE RETRIEVAL ----------
# #     idxs, scores = movie_index.search(user_vec, k=TOP_K)
# #     candidates = [movie_metadata[i] for i in idxs]

# #     # -------- OPTIONAL RERANK ----------
# #     rerank_prompt = f"""
# # User query:
# # {user_input}

# # Candidate movies:
# # {candidates}

# # Select the best {FINAL_K} movies and explain why.
# # """

# #     return call_llm(rerank_prompt, temperature=0.4)

# # def recommend(user_input: str, user_id: Optional[str] = None) -> str:
# #     """
# #     Main recommendation entry point.

# #     - Builds a taste vector from the *current* text input
# #     - If user_id is provided and seen before, fuses new taste with stored taste
# #     - Persists user taste vectors to runtime_users.parquet via user_store
# #     - Retrieves Top-K movies via the embedding index
# #     - Uses a single LLM call to format/rerank/explain candidates
# #     """

# #     # ----------------- 1) TASTE EMBEDDING FROM CURRENT INPUT -----------------
# #     # OPTION A (no extra GPT): directly embed raw preference text
# #     taste_profile = user_input

# #     # OPTION B (more structured, but costs a second GPT call):
# #     # taste_profile = extract_taste_with_llm(user_input)

# #     new_vec = embed_user_taste(taste_profile)  # -> np.ndarray or list[float]
# #     new_vec = np.array(new_vec, dtype=np.float32)

# #     # ----------------- 2) FUSE WITH PREVIOUS TASTE (IF ANY) ------------------
# #     # Treat empty string as "no identity" (ephemeral user)
# #     has_identity = user_id is not None and user_id != ""

# #     if has_identity and user_id in user_vectors:
# #         prev_vec = user_vectors[user_id]
# #         # Exponential moving average in taste space
# #         user_vec = USER_FUSE_ALPHA * prev_vec + (1.0 - USER_FUSE_ALPHA) * new_vec
# #     else:
# #         # New user or no identity: just use current message taste
# #         user_vec = new_vec

# #     # ----------------- 3) PERSIST UPDATED USER STATE -------------------------
# #     if has_identity:
# #         user_vectors[user_id] = user_vec
# #         save_user_state(user_vectors)

# #     # ----------------- 4) MOVIE RETRIEVAL ------------------------------------
# #     # NOTE: If movie_index expects shape (1, d), wrap accordingly:
# #     #   idxs, scores = movie_index.search(user_vec[None, :], k=TOP_K)
# #     # If your current code already handles that internally, keep as-is.
# #     idxs, scores = movie_index.search(user_vec, k=TOP_K)

# #     candidates = [movie_metadata[i] for i in idxs]

# #     # ----------------- 5) OPTIONAL LLM RERANK + EXPLANATION ------------------
# #     rerank_prompt = f"""
# # You are a movie recommender system.

# # User's latest preference/input:
# # {user_input}

# # (You may infer that their long-term taste vector has already been updated,
# # so this list should match their overall taste, not just this one sentence.)

# # Candidate movies (as Python-like list of dicts):
# # {candidates}

# # From these candidates, select the best {FINAL_K} movies for the user
# # and explain briefly why each fits their taste.
# # Return a clear, human-readable list.
# # """

# #     return call_llm(rerank_prompt, temperature=0.4)


# from typing import Optional
# import numpy as np

# from user_store import load_user_state, save_user_state

# # Persistent runtime users: user_id -> np.ndarray taste vector
# user_vectors: dict[str, np.ndarray] = load_user_state()
# USER_FUSE_ALPHA = 0.8  # 0.8 old taste, 0.2 new

# # In-process text memory for explanations
# preference_history: dict[str, list[str]] = {}


# def recommend(user_input: str, user_id: Optional[str] = None) -> str:
#     """
#     Main recommendation entry point.

#     - Build a taste vector from this input
#     - Fuse with previous taste if user_id is known
#     - Save updated taste vector to runtime_users.parquet
#     - Keep a small text history per user for the LLM
#     - Retrieve movies and ask GPT to explain/rerank using both history + latest input
#     """

#     # ----------------- 1) TASTE EMBEDDING FROM CURRENT INPUT -----------------
#     # Simple version: use raw input as taste profile
#     taste_profile = user_input
#     new_vec = embed_user_taste(taste_profile)
#     new_vec = np.array(new_vec, dtype=np.float32)

#     # ----------------- 2) FUSE WITH PREVIOUS TASTE (IF ANY) ------------------
#     has_identity = user_id is not None and user_id != ""

#     if has_identity and user_id in user_vectors:
#         prev_vec = user_vectors[user_id]
#         user_vec = USER_FUSE_ALPHA * prev_vec + (1.0 - USER_FUSE_ALPHA) * new_vec
#     else:
#         user_vec = new_vec

#     # ----------------- 3) UPDATE & PERSIST USER STATE ------------------------
#     if has_identity:
#         # Vector memory
#         user_vectors[user_id] = user_vec
#         save_user_state(user_vectors)

#         # Textual preference history (for LLM explanations)
#         prefs = preference_history.get(user_id, [])
#         prefs.append(user_input)
#         # Optional: keep only last N preference lines
#         if len(prefs) > 10:
#             prefs = prefs[-10:]
#         preference_history[user_id] = prefs
#         history_text = "\n".join(f"- {p}" for p in prefs)
#     else:
#         history_text = "- (no stable user id; only using this message)"

#     # ----------------- 4) MOVIE RETRIEVAL ------------------------------------
#     # If movie_index expects (1, d) shape, wrap as user_vec[None, :]
#     idxs, scores = movie_index.search(user_vec, k=TOP_K)
#     candidates = [movie_metadata[i] for i in idxs]

#     # ----------------- 5) LLM RERANK + EXPLANATION ---------------------------
#     rerank_prompt = f"""
# You are a movie recommender system.

# User's long-term preferences so far:
# {history_text}

# User's latest message:
# {user_input}

# Candidate movies (as a Python-like list of dicts):
# {candidates}

# From these candidates, choose the best {FINAL_K} movies
# that match BOTH the user's long-term tastes and their latest message.
# Explain briefly why each one fits.
# Return a clear, human-readable list.
# """
    
#     if has_identity and user_id in user_vectors:
#         prev_vec = user_vectors[user_id]
#         print(f"[debug] prev_norm={np.linalg.norm(prev_vec):.3f} "
#             f"new_norm={np.linalg.norm(new_vec):.3f}")
#         user_vec = USER_FUSE_ALPHA * prev_vec + (1.0 - USER_FUSE_ALPHA) * new_vec
#         print(f"[debug] fused_norm={np.linalg.norm(user_vec):.3f}")


#     return call_llm(rerank_prompt, temperature=0.4)

