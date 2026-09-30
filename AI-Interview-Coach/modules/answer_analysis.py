from functools import lru_cache
from typing import Dict

from sentence_transformers import SentenceTransformer, util


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def score_answer_relevance(question: str, user_answer: str, ideal_answer: str) -> Dict[str, float]:
    if not user_answer or not user_answer.strip():
        return {"relevance_score": 0.0, "similarity": 0.0}

    model = _load_model()
    emb = model.encode([user_answer, ideal_answer], convert_to_tensor=True)
    similarity = float(util.cos_sim(emb[0], emb[1]).item())
    score = max(0.0, min(100.0, (similarity + 1) / 2 * 100))
    return {"relevance_score": round(score, 2), "similarity": round(similarity, 4)}
