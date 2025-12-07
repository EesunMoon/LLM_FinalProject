# # # user_store.py
# # from __future__ import annotations

# # from pathlib import Path
# # from typing import Dict

# # import numpy as np
# # import pandas as pd

# # # We’ll keep runtime user taste vectors here
# # RUNTIME_USERS_PATH = Path(__file__).parent / "runtime_users.parquet"


# # def load_user_state() -> Dict[str, np.ndarray]:
# #     """
# #     Load persistent user taste vectors from runtime_users.parquet.

# #     Returns:
# #         dict user_id -> np.ndarray (taste vector)
# #     """
# #     if not RUNTIME_USERS_PATH.exists():
# #         return {}

# #     try:
# #         df = pd.read_parquet(RUNTIME_USERS_PATH)
# #     except Exception as e:
# #         # Fail-safe: if the file is corrupted, log and start fresh
# #         print(f"[user_store] Warning: could not read {RUNTIME_USERS_PATH}: {e}")
# #         return {}

# #     state: Dict[str, np.ndarray] = {}
# #     if "user_id" not in df.columns or "embedding" not in df.columns:
# #         print(f"[user_store] Warning: {RUNTIME_USERS_PATH} missing required columns.")
# #         return {}

# #     for row in df.itertuples(index=False):
# #         # row.embedding is a list[float]; convert to np.ndarray
# #         state[str(row.user_id)] = np.array(row.embedding, dtype=np.float32)

# #     print(f"[user_store] Loaded {len(state)} runtime users from {RUNTIME_USERS_PATH}")
# #     return state


# # def save_user_state(state: Dict[str, np.ndarray]) -> None:
# #     """
# #     Persist user taste vectors to runtime_users.parquet.

# #     Args:
# #         state: dict user_id -> np.ndarray
# #     """
# #     if not state:
# #         # If no users, optionally delete the file
# #         if RUNTIME_USERS_PATH.exists():
# #             RUNTIME_USERS_PATH.unlink()
# #             print(f"[user_store] No users, removed {RUNTIME_USERS_PATH}")
# #         return

# #     data = {
# #         "user_id": [],
# #         "embedding": [],
# #     }

# #     for user_id, vec in state.items():
# #         data["user_id"].append(str(user_id))
# #         # Ensure plain Python list for parquet
# #         data["embedding"].append(vec.tolist())

# #     df = pd.DataFrame(data)
# #     df.to_parquet(RUNTIME_USERS_PATH, index=False)
# #     print(f"[user_store] Saved {len(state)} runtime users to {RUNTIME_USERS_PATH}")
# from pathlib import Path
# from typing import Dict

# import numpy as np
# import pandas as pd

# RUNTIME_USERS_PATH = Path(__file__).parent / "runtime_users.parquet"


# def load_user_state() -> Dict[str, np.ndarray]:
#     if not RUNTIME_USERS_PATH.exists():
#         return {}

#     try:
#         df = pd.read_parquet(RUNTIME_USERS_PATH)
#     except Exception as e:
#         print(f"[user_store] Warning: could not read {RUNTIME_USERS_PATH}: {e}")
#         return {}

#     state: Dict[str, np.ndarray] = {}
#     for row in df.itertuples(index=False):
#         state[str(row.user_id)] = np.array(row.embedding, dtype=np.float32)

#     print(f"[user_store] Loaded {len(state)} runtime users from {RUNTIME_USERS_PATH}")
#     return state


# def save_user_state(state: Dict[str, np.ndarray]) -> None:
#     if not state:
#         if RUNTIME_USERS_PATH.exists():
#             RUNTIME_USERS_PATH.unlink()
#             print(f"[user_store] No users, removed {RUNTIME_USERS_PATH}")
#         return

#     data = {"user_id": [], "embedding": []}
#     for user_id, vec in state.items():
#         data["user_id"].append(str(user_id))
#         data["embedding"].append(vec.tolist())

#     df = pd.DataFrame(data)
#     df.to_parquet(RUNTIME_USERS_PATH, index=False)
#     print(f"[user_store] Saved {len(state)} runtime users to {RUNTIME_USERS_PATH}")

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

RUNTIME_USERS_PATH = Path(__file__).parent / "runtime_users.parquet"


def load_user_state() -> Dict[str, np.ndarray]:
    if not RUNTIME_USERS_PATH.exists():
        return {}

    try:
        df = pd.read_parquet(RUNTIME_USERS_PATH)
    except Exception as e:
        print(f"[user_store] Warning: could not read {RUNTIME_USERS_PATH}: {e}")
        return {}

    state: Dict[str, np.ndarray] = {}
    for row in df.itertuples(index=False):
        state[str(row.user_id)] = np.array(row.embedding, dtype=np.float32)

    print(f"[user_store] Loaded {len(state)} runtime users from {RUNTIME_USERS_PATH}")
    return state


def save_user_state(state: Dict[str, np.ndarray]) -> None:
    if not state:
        if RUNTIME_USERS_PATH.exists():
            RUNTIME_USERS_PATH.unlink()
            print(f"[user_store] No users, removed {RUNTIME_USERS_PATH}")
        return

    data = {"user_id": [], "embedding": []}
    for user_id, vec in state.items():
        data["user_id"].append(str(user_id))
        data["embedding"].append(vec.tolist())

    df = pd.DataFrame(data)
    df.to_parquet(RUNTIME_USERS_PATH, index=False)
    print(f"[user_store] Saved {len(state)} runtime users to {RUNTIME_USERS_PATH}")


# ---------------------------------------------------------
# 🔍 Debug helper: inspect current runtime users
# ---------------------------------------------------------

def debug_inspect_users(max_users: int = 20) -> None:
    """
    Print a summary of runtime users stored in runtime_users.parquet.

    Shows:
    - total count
    - up to `max_users` user_ids
    - embedding dimension and L2 norm for sanity checking
    """
    state = load_user_state()
    if not state:
        print("[debug] No runtime users found.")
        return

    print(f"[debug] Total runtime users: {len(state)}")
    print(f"[debug] Showing up to {max_users} users:\n")

    for i, (user_id, vec) in enumerate(state.items()):
        if i >= max_users:
            break
        dim = vec.shape[0]
        norm = float(np.linalg.norm(vec))
        print(f"  - user_id='{user_id}': dim={dim}, norm={norm:.3f}")


if __name__ == "__main__":
    # Run: python user_store.py
    debug_inspect_users()
