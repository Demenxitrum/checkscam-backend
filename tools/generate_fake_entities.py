import json
import random
from pathlib import Path

# ==========================
# CONFIG
# ==========================
RAW_DIR = Path("storage/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

NUM_PHONE = 400
NUM_BANK = 150

PHONE_PREFIX = [
    "032", "033", "034", "035", "036", "037", "038", "039",
    "070", "076", "077", "078", "079",
    "081", "082", "083", "084", "085"
]

BANK_NAMES = [
    "Vietcombank",
    "BIDV",
    "VietinBank",
    "ACB",
    "MB Bank",
    "Techcombank",
    "Sacombank"
]

# ==========================
# GENERATORS
# ==========================
def gen_phone():
    prefix = random.choice(PHONE_PREFIX)
    return prefix + "".join(random.choices("0123456789", k=7))

def gen_bank():
    length = random.choice([9, 10, 12, 13])
    return "".join(random.choices("0123456789", k=length))

# ==========================
# MAIN
# ==========================
def main():
    # ---------- PHONE ----------
    phones = []
    used_phone = set()

    while len(phones) < NUM_PHONE:
        value = gen_phone()
        if value in used_phone:
            continue
        used_phone.add(value)

        phones.append({
            "source": "user_report",
            "type": "PHONE",
            "value": value,
            "context": "Số điện thoại nghi vấn lừa đảo ",
            "country": "VN"
        })

    # ---------- BANK ----------
    banks = []
    used_bank = set()

    while len(banks) < NUM_BANK:
        value = gen_bank()
        if value in used_bank:
            continue
        used_bank.add(value)

        banks.append({
            "source": "user_report",
            "type": "BANK",
            "value": value,
            "bank_name": random.choice(BANK_NAMES),
            "context": "Tài khoản ngân hàng nghi vấn lừa đảo ",
            "country": "VN"
        })

    # ---------- WRITE FILES ----------
    (RAW_DIR / "fake_phone.json").write_text(
        json.dumps(phones, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    (RAW_DIR / "fake_bank.json").write_text(
        json.dumps(banks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("✅ Fake data generated successfully")
    print(f"   - PHONE: {len(phones)} → storage/raw/fake_phone.json")
    print(f"   - BANK : {len(banks)} → storage/raw/fake_bank.json")


if __name__ == "__main__":
    main()
