import hashlib


ANIMAL_SIGNS = [
    "Gaja",
    "Sinhaya",
    "Kurulla",
    "Makara",
    "Naga",
    "Hansa",
    "Mina",
    "Vrushabha",
]

ELEMENTS = ["Agni", "Jala", "Vayu", "Pruthvi"]

FORTUNE_WINDOWS = [
    "Early Morning Energy",
    "Midday Balance",
    "Sunset Reflection",
    "Night Insight",
]


def _pick(sequence: list[str], seed: str, offset: int) -> str:
    digest = hashlib.sha256(f"{seed}:{offset}".encode("utf-8")).hexdigest()
    idx = int(digest[:8], 16) % len(sequence)
    return sequence[idx]


def generate_birth_map(birthdate: str, birth_time: str, location: str) -> dict:
    seed = f"{birthdate}|{birth_time}|{location.strip().lower()}"
    sign = _pick(ANIMAL_SIGNS, seed, 1)
    element = _pick(ELEMENTS, seed, 2)
    window = _pick(FORTUNE_WINDOWS, seed, 3)

    return {
        "kendaraya_type": "demo-stub",
        "birth_map_name": f"{sign} {element} Map",
        "auspicious_window": window,
        "summary": (
            "This is a deterministic demonstration output for runtime testing. "
            "Use the same input values to reproduce the same birth map response."
        ),
        "input_echo": {
            "birthdate": birthdate,
            "birth_time": birth_time,
            "location": location,
        },
    }
