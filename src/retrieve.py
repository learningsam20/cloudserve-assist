"""Index and retrieve documentation passages. Always use doc_id (findings D2).

Supports dense (Chroma), hybrid (dense + lexical TF-IDF), and auto fallback:
dense first; if top score < HYBRID_DENSE_SCORE_FLOOR or empty → hybrid.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

import chromadb
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import get_settings
from src.models import Passage, Ticket
from src.observability import observe_retrieval

_embedder: Optional[SentenceTransformer] = None
_client = None
_lexical: Optional[dict[str, Any]] = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        settings = get_settings()
        name = settings.embedding_model
        # Prefer local HF cache (avoids hub/proxy failures mid-eval).
        try:
            _embedder = SentenceTransformer(name, local_files_only=True)
        except Exception:
            _embedder = SentenceTransformer(name)
        dim = int(_embedder.get_sentence_embedding_dimension() or 0)
        if dim < settings.embedding_min_dim:
            _embedder = None
            raise RuntimeError(
                f"Embedding model {name!r} loaded with invalid dim={dim} "
                f"(min {settings.embedding_min_dim}). Check HF cache, then re-run setup_all."
            )
        # Reject untrained mean-pool fallback (prints "No sentence-transformers model found").
        try:
            from sentence_transformers.models import Transformer as _STTransformer

            if not any(isinstance(m, _STTransformer) for m in _embedder):
                _embedder = None
                raise RuntimeError(
                    f"Embedding model {name!r} did not load a Transformer module "
                    "(offline mean-pool fallback). Ensure HF cache has the model, "
                    "then re-run setup_all / build_index."
                )
        except ImportError:
            pass
    return _embedder


def _get_collection():
    global _client
    settings = get_settings()
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    if _client is None:
        _client = chromadb.PersistentClient(path=str(settings.chroma_path))
    return _client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def _passage_key(p: Passage) -> str:
    return f"{p.doc_id}::{hash(p.text) & 0xFFFFFFFF}"


def _split_markdown(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple splitter; avoids inventing content. Sizes come from settings/env."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    parts = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    buf = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(buf) + len(part) + 2 <= chunk_size:
            buf = f"{buf}\n\n{part}".strip() if buf else part
            continue
        if buf:
            chunks.append(buf)
        if len(part) <= chunk_size:
            buf = part
        else:
            start = 0
            while start < len(part):
                end = min(start + chunk_size, len(part))
                chunks.append(part[start:end])
                if end >= len(part):
                    break
                start = max(end - overlap, start + 1)
            buf = ""
    if buf:
        chunks.append(buf)
    return chunks


def _save_lexical_index(
    documents: list[str],
    metadatas: list[dict],
    path: Path,
) -> None:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=50000,
    )
    matrix = vectorizer.fit_transform(documents)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "vectorizer": vectorizer,
            "matrix": matrix,
            "documents": documents,
            "metadatas": metadatas,
        },
        path,
    )
    global _lexical
    _lexical = None


def _load_lexical() -> Optional[dict[str, Any]]:
    global _lexical
    if _lexical is not None:
        return _lexical
    settings = get_settings()
    path = settings.lexical_index_path
    if not path.exists():
        return None
    _lexical = joblib.load(path)
    return _lexical


def build_index(documentation_path: Path, *, reset: bool = True) -> int:
    """Load real documentation.json and persist Chroma + lexical index."""
    docs = json.loads(Path(documentation_path).read_text(encoding="utf-8"))
    if not isinstance(docs, list):
        raise ValueError("documentation.json must be a JSON array")

    settings = get_settings()
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    if reset:
        try:
            client.delete_collection(settings.chroma_collection)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )

    embedder = _get_embedder()
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for doc in docs:
        doc_id = str(doc.get("doc_id") or "").strip()
        if not doc_id:
            raise ValueError("documentation entry missing doc_id")
        title = str(doc.get("title") or "")
        content = str(doc.get("content") or "")
        for i, chunk in enumerate(
            _split_markdown(content, settings.chunk_size, settings.chunk_overlap)
        ):
            ids.append(f"{doc_id}::{i}")
            documents.append(chunk)
            metadatas.append({"doc_id": doc_id, "title": title, "chunk_index": i})

    if not documents:
        return 0

    embeddings = embedder.encode(documents, show_progress_bar=False).tolist()
    batch = settings.index_batch_size
    for start in range(0, len(documents), batch):
        end = start + batch
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    _save_lexical_index(documents, metadatas, settings.lexical_index_path)

    global _client
    _client = client
    return len(documents)


def _dense_retrieve(query: str, k: int, score_floor: float) -> list[Passage]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    q_emb = _get_embedder().encode([query], show_progress_bar=False).tolist()
    n = min(k, max(1, collection.count()))
    result = collection.query(query_embeddings=q_emb, n_results=n)

    passages: list[Passage] = []
    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    for text, meta, dist in zip(docs, metas, distances):
        score = 1.0 - float(dist)
        if score < score_floor:
            continue
        passages.append(
            Passage(
                doc_id=str(meta.get("doc_id")),
                text=text,
                score=score,
                title=meta.get("title"),
            )
        )
    return passages


def _lexical_retrieve(query: str, k: int) -> list[Passage]:
    bundle = _load_lexical()
    if bundle is None:
        return []
    vectorizer: TfidfVectorizer = bundle["vectorizer"]
    matrix = bundle["matrix"]
    documents: list[str] = bundle["documents"]
    metadatas: list[dict] = bundle["metadatas"]
    q = vectorizer.transform([query])
    sims = cosine_similarity(q, matrix).ravel()
    if sims.size == 0:
        return []
    top_idx = np.argsort(-sims)[:k]
    out: list[Passage] = []
    for i in top_idx:
        score = float(sims[i])
        if score <= 0:
            continue
        meta = metadatas[int(i)]
        out.append(
            Passage(
                doc_id=str(meta.get("doc_id")),
                text=documents[int(i)],
                score=score,
                title=meta.get("title"),
            )
        )
    return out


def _rrf_order(
    dense: list[Passage],
    lexical: list[Passage],
    *,
    k: int,
    alpha: float,
) -> list[str]:
    """Return passage keys ordered by weighted reciprocal-rank fusion."""
    scores: dict[str, float] = {}

    for rank, p in enumerate(dense, start=1):
        key = _passage_key(p)
        scores[key] = scores.get(key, 0.0) + alpha * (1.0 / (60 + rank))

    for rank, p in enumerate(lexical, start=1):
        key = _passage_key(p)
        scores[key] = scores.get(key, 0.0) + (1.0 - alpha) * (1.0 / (60 + rank))

    return [key for key, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:k]]


def _hybrid_retrieve(query: str, k: int, score_floor: float) -> list[Passage]:
    """Fuse dense + lexical; keep routing scores as max(dense, lexical) cosine."""
    settings = get_settings()
    pool = max(k * 3, k)
    dense: list[Passage] = []
    try:
        dense = _dense_retrieve(query, k=pool, score_floor=0.0)
    except Exception:
        # Lexical-only rescue when embeddings unavailable
        dense = []
    lexical = _lexical_retrieve(query, k=pool)
    if not dense and not lexical:
        return []

    dense_map = {_passage_key(p): p for p in dense}
    lex_map = {_passage_key(p): p for p in lexical}
    ordered_keys = _rrf_order(
        dense, lexical, k=k, alpha=float(settings.hybrid_dense_alpha)
    )

    out: list[Passage] = []
    for key in ordered_keys:
        d = dense_map.get(key)
        lx = lex_map.get(key)
        base = d or lx
        if base is None:
            continue
        score = max(
            d.score if d is not None else 0.0,
            lx.score if lx is not None else 0.0,
        )
        out.append(
            Passage(
                doc_id=base.doc_id,
                text=base.text,
                score=float(score),
                title=base.title,
            )
        )
    # Prefer hits that clear a soft floor; otherwise keep top fused (rescue path)
    soft = score_floor * 0.5
    filtered = [p for p in out if p.score >= soft]
    return (filtered or out)[:k]


def retrieve(
    ticket: Ticket,
    *,
    top_k: Optional[int] = None,
    min_score: Optional[float] = None,
) -> list[Passage]:
    """Return ranked passages; mode dense|hybrid|auto from settings.

    ``auto`` runs dense first and only executes hybrid when dense is empty or
    top score falls below ``HYBRID_DENSE_SCORE_FLOOR``.
    """
    settings = get_settings()
    k = top_k if top_k is not None else settings.retrieval_top_k
    score_floor = settings.retrieval_min_score if min_score is None else min_score
    query = ticket.text_for_model()
    if not query:
        observe_retrieval(mode="none", top_score=0.0, n_passages=0)
        return []

    mode = settings.retrieval_mode
    used = mode
    passages: list[Passage] = []

    if mode == "hybrid":
        passages = _hybrid_retrieve(query, k, score_floor)
        used = "hybrid"
    elif mode == "dense":
        passages = _dense_retrieve(query, k, score_floor)
        used = "dense"
    else:  # auto — hybrid only when dense quality is below floor
        try:
            dense = _dense_retrieve(query, k, score_floor)
        except Exception:
            dense = []
        top = max((p.score for p in dense), default=0.0)
        if dense and top >= settings.hybrid_dense_score_floor:
            passages = dense
            used = "dense"
        else:
            passages = _hybrid_retrieve(query, k, score_floor)
            used = "auto_fallback_hybrid" if passages else "dense_empty"

    top_score = max((p.score for p in passages), default=0.0)
    observe_retrieval(mode=used, top_score=top_score, n_passages=len(passages))
    return passages


def index_stats() -> dict:
    """Return live Chroma collection stats (proves index is wired)."""
    settings = get_settings()
    collection = _get_collection()
    lexical_ok = settings.lexical_index_path.exists()
    return {
        "chroma_path": str(settings.chroma_path),
        "collection": settings.chroma_collection,
        "count": int(collection.count()),
        "lexical_index": str(settings.lexical_index_path),
        "lexical_ready": lexical_ok,
        "retrieval_mode": settings.retrieval_mode,
    }


def reset_retrieve_cache() -> None:
    global _embedder, _client, _lexical
    _embedder = None
    _client = None
    _lexical = None
