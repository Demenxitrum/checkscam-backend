"""
move_all_raw_to_root.py
======================

Mục tiêu:
- Gom TẤT CẢ dữ liệu RAW về 1 chỗ duy nhất:
    storage/raw/   (ROOT)

Nguồn lấy:
1) etl/sources/data/
2) etl/storage/raw/

Nguyên tắc:
- KHÔNG ghi đè file đã tồn tại
- CHỈ copy các file dữ liệu (.json, .jsonl, .csv)
"""

from pathlib import Path
import shutil


# =========================
# SOURCE DIRS
# =========================
SRC_DIRS = [
    Path("etl/sources/data"),
    Path("etl/storage/raw"),
]

# =========================
# DESTINATION
# =========================
DEST_DIR = Path("storage/raw")

VALID_SUFFIX = {".json", ".jsonl", ".csv"}


def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0

    for src_dir in SRC_DIRS:
        if not src_dir.exists():
            print(f"[WARN] Source dir not found: {src_dir}")
            continue

        for file in src_dir.iterdir():
            if not file.is_file():
                continue

            if file.suffix not in VALID_SUFFIX:
                continue

            dest = DEST_DIR / file.name

            if dest.exists():
                print(f"[SKIP] Exists: {file.name}")
                skipped += 1
                continue

            shutil.copy2(file, dest)
            print(f"[COPY] {file} → {dest}")
            copied += 1

    print("\n=========================")
    print("MOVE RAW DATA DONE")
    print(f"Copied : {copied}")
    print(f"Skipped: {skipped}")
    print("=========================")


if __name__ == "__main__":
    main()
