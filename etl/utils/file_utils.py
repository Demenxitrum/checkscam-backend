import json
import hashlib
from pathlib import Path


# =========================================================
# HASH
# =========================================================
def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash(item: dict) -> str:
    """
    Hash CHUẨN production:
    - Không phụ thuộc text
    - Dựa trên entity thật
    """
    key = "|".join([
        item.get("source", ""),
        item.get("group", "") or item.get("hashtag", ""),
        ",".join(item.get("phones", [])),
        ",".join(item.get("banks", [])),
        ",".join(item.get("urls", [])),
    ])
    return sha(key)


# =========================================================
# FILE IO
# =========================================================
def load_json(path: Path) -> list:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: list):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================================================
# MERGE + DEDUP
# =========================================================
def merge_dedup(old: list, new: list) -> list:
    """
    Chỉ giữ dữ liệu MỚI – KHÔNG TRÙNG
    """
    seen = {content_hash(item) for item in old}
    merged = old.copy()

    for item in new:
        h = content_hash(item)
        if h not in seen:
            item["content_hash"] = h
            merged.append(item)
            seen.add(h)

    return merged
