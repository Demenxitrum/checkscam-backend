# etl/similarity/embedder.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
import re
import hashlib

try:
    import numpy as np
except Exception as e:
    raise RuntimeError("embedder.py requires numpy. Please install: pip install numpy") from e


TextLike = Union[str, None]


# ==========================================================
# CONFIG
# ==========================================================

_DEFAULT_DIM = 384  # phổ biến cho MiniLM; fallback hash vector cũng dùng dim này


def _safe_str(x: Any) -> str:
    return "" if x is None else str(x)


def _normalize_spaces(s: str) -> str:
    s = s.replace("\u200b", " ")  # zero-width space
    return re.sub(r"\s+", " ", s).strip()


def _truncate(s: str, max_len: int) -> str:
    if max_len <= 0:
        return s
    return s if len(s) <= max_len else s[:max_len]


def _l2_normalize(v: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(v))
    if norm <= 1e-12:
        return v
    return v / norm


def _tokenize(text: str) -> List[str]:
    """
    Tokenizer đơn giản, ổn cho tiếng Việt/Anh:
    - giữ chữ + số
    - tách theo non-word
    """
    text = text.lower()
    # giữ chữ số + chữ cái + underscore; các ký tự khác -> space
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    text = _normalize_spaces(text)
    if not text:
        return []
    return text.split(" ")


def _hash_to_index_and_sign(token: str, dim: int) -> Tuple[int, float]:
    """
    Map token -> (index, sign) deterministic
    """
    h = hashlib.sha256(token.encode("utf-8")).digest()
    # lấy 4 byte đầu -> index
    idx = int.from_bytes(h[:4], "little", signed=False) % dim
    # lấy 1 bit -> sign
    sign = 1.0 if (h[4] & 1) == 0 else -1.0
    return idx, sign


def _hash_embed_text(text: str, dim: int) -> np.ndarray:
    """
    Hash-based embedding (fallback):
    - Bag-of-tokens + 2-gram tokens (nhẹ nhưng hữu ích)
    - deterministic, không cần model
    """
    v = np.zeros((dim,), dtype=np.float32)
    tokens = _tokenize(text)
    if not tokens:
        return v

    # unigram
    for t in tokens:
        idx, sign = _hash_to_index_and_sign(t, dim)
        v[idx] += sign

    # bigram
    if len(tokens) >= 2:
        for i in range(len(tokens) - 1):
            bg = tokens[i] + "_" + tokens[i + 1]
            idx, sign = _hash_to_index_and_sign(bg, dim)
            v[idx] += 0.7 * sign

    return v


# ==========================================================
# EMBEDDER
# ==========================================================

@dataclass
class EmbedderConfig:
    """
    Cấu hình embedder.
    """
    prefer_sentence_transformers: bool = True
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dim: int = _DEFAULT_DIM

    # giới hạn text đưa vào model (tránh quá dài)
    max_text_len: int = 1200

    # luôn L2 normalize output để similarity cosine dễ chuẩn
    l2_normalize: bool = True


class Embedder:
    """
    Embedder chịu trách nhiệm:
    - build text đầu vào (từ NormalizedRecord hoặc text thường)
    - tạo vector embedding (model-based nếu có / fallback hash)
    - trả về vector dạng List[float] để dễ JSON hóa
    """

    def __init__(self, config: Optional[EmbedderConfig] = None):
        self.config = config or EmbedderConfig()
        self._backend = "hash"  # default fallback
        self._model = None

        if self.config.prefer_sentence_transformers:
            self._try_init_sentence_transformers()

    # -----------------------------
    # Backend init
    # -----------------------------
    def _try_init_sentence_transformers(self) -> None:
        """
        Thử load sentence-transformers nếu có.
        Nếu không có, tự fallback hash (không crash).
        """
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._model = SentenceTransformer(self.config.model_name)
            self._backend = "sentence_transformers"
        except Exception:
            self._model = None
            self._backend = "hash"

    # -----------------------------
    # Public info
    # -----------------------------
    @property
    def backend(self) -> str:
        """
        backend đang dùng: 'sentence_transformers' hoặc 'hash'
        """
        return self._backend

    @property
    def dim(self) -> int:
        return int(self.config.dim)

    # -----------------------------
    # Build input text
    # -----------------------------
    def build_text_for_record(self, record: Any) -> str:
        """
        Build text ổn định để embedding từ NormalizedRecord.

        Mục tiêu:
        - giúp similarity hiểu "ngữ cảnh" chứ không chỉ value
        - nhưng vẫn giữ format ổn định / dễ debug

        record kỳ vọng có các field:
          entity_type, entity_value, country, source, context, url, rules_triggered
        """
        etype = _safe_str(getattr(record, "entity_type", "")).strip()
        # entity_type có thể là Enum -> lấy .value nếu có
        if hasattr(getattr(record, "entity_type", None), "value"):
            etype = _safe_str(getattr(record.entity_type, "value", etype))

        value = _safe_str(getattr(record, "entity_value", "")).strip()
        country = _safe_str(getattr(record, "country", "")).strip()
        source = _safe_str(getattr(record, "source", "")).strip()
        url = _safe_str(getattr(record, "url", "")).strip()
        ctx = _safe_str(getattr(record, "context", "")).strip()

        rules = getattr(record, "rules_triggered", None)
        if rules is None:
            rules_str = ""
        else:
            # rules có thể là list[str] hoặc string
            if isinstance(rules, (list, tuple)):
                rules_str = " ".join([_safe_str(x) for x in rules])
            else:
                rules_str = _safe_str(rules)

        parts = [
            f"type:{etype}",
            f"value:{value}",
            f"country:{country}",
            f"source:{source}",
        ]
        if url:
            parts.append(f"url:{url}")
        if rules_str:
            parts.append(f"rules:{rules_str}")
        if ctx:
            parts.append(f"context:{ctx}")

        text = " | ".join(parts)
        text = _normalize_spaces(text)
        text = _truncate(text, self.config.max_text_len)
        return text

    # -----------------------------
    # Embed text(s)
    # -----------------------------
    def embed_text(self, text: TextLike) -> List[float]:
        """
        Embed 1 text -> vector list[float]
        """
        text = _truncate(_normalize_spaces(_safe_str(text)), self.config.max_text_len)
        if not text:
            v = np.zeros((self.dim,), dtype=np.float32)
            return v.tolist()

        v = self._embed_text_to_np(text)
        if self.config.l2_normalize:
            v = _l2_normalize(v)
        return v.astype(np.float32).tolist()

    def embed_texts(self, texts: Sequence[TextLike]) -> List[List[float]]:
        """
        Embed nhiều text một lần.
        """
        cleaned: List[str] = []
        for t in texts:
            s = _truncate(_normalize_spaces(_safe_str(t)), self.config.max_text_len)
            cleaned.append(s)

        vectors_np = self._embed_texts_to_np(cleaned)
        if self.config.l2_normalize:
            vectors_np = np.stack([_l2_normalize(v) for v in vectors_np], axis=0)
        return vectors_np.astype(np.float32).tolist()

    def embed_record(self, record: Any) -> List[float]:
        """
        Embed trực tiếp từ NormalizedRecord.
        """
        text = self.build_text_for_record(record)
        return self.embed_text(text)

    def embed_records(self, records: Sequence[Any]) -> List[List[float]]:
        """
        Embed list NormalizedRecord.
        """
        texts = [self.build_text_for_record(r) for r in records]
        return self.embed_texts(texts)

    # -----------------------------
    # Internal embedding
    # -----------------------------
    def _embed_text_to_np(self, text: str) -> np.ndarray:
        if self._backend == "sentence_transformers" and self._model is not None:
            # sentence-transformers trả về np.ndarray
            v = self._model.encode([text], normalize_embeddings=False, show_progress_bar=False)
            v = np.asarray(v[0], dtype=np.float32)
            # nếu model dim khác config.dim, thì update dim theo model
            if v.shape[0] != self.dim:
                # không crash; ưu tiên dim thực tế
                self.config.dim = int(v.shape[0])
            return v
        # fallback hash
        return _hash_embed_text(text, self.dim)

    def _embed_texts_to_np(self, texts: List[str]) -> np.ndarray:
        if self._backend == "sentence_transformers" and self._model is not None:
            v = self._model.encode(texts, normalize_embeddings=False, show_progress_bar=False)
            v = np.asarray(v, dtype=np.float32)
            if v.shape[1] != self.dim:
                self.config.dim = int(v.shape[1])
            return v

        # fallback hash
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            out[i] = _hash_embed_text(t, self.dim)
        return out


# ==========================================================
# QUICK DEMO (optional)
# ==========================================================
if __name__ == "__main__":
    # Demo nhanh: embed 2 text và tính cosine similarity
    e = Embedder()
    print("[Embedder] backend =", e.backend, "| dim =", e.dim)

    a = "type:URL | value:https://abc.vn/login | context: mạo danh ngân hàng yêu cầu đăng nhập"
    b = "type:URL | value:https://xyz.vn/secure | context: cảnh báo trang giả mạo ngân hàng"

    va = np.array(e.embed_text(a), dtype=np.float32)
    vb = np.array(e.embed_text(b), dtype=np.float32)

    sim = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-12))
    print("cosine_similarity =", sim)
