"""Synthetic patient payload generator for demo + testing."""
import random
import uuid
from datetime import datetime, timezone
from typing import Any

FIRST_NAMES = ["Asha", "Rohan", "Maya", "Vikram", "Priya", "Arjun", "Neha", "Kabir", "Ishita", "Aditya"]
LAST_NAMES = ["Iyer", "Mehta", "Singh", "Kapoor", "Reddy", "Patel", "Sharma", "Khan", "Joshi", "Verma"]
NARRATIVES = {
    "green": [
        "Feeling pretty good today. Light stiffness in the morning, managed a 30-minute walk without pain. Mood stable.",
        "Sleeping well, energy is back to normal. Did yoga twice this week.",
        "Pain only when sitting too long. Movement feels natural again.",
    ],
    "yellow": [
        "Pain in lower back is bothering me when I bend. I worry that walking too much will make it worse. Sleep was patchy.",
        "Mornings are stiff. Sometimes I catastrophize about flare-ups. Trying to stay positive.",
        "Functional but distressed. I notice I'm guarding my back.",
    ],
    "red": [
        "Every movement terrifies me. I think the pain will destroy my body if I push. I can't focus, brain feels foggy. I'm exhausted and hopeless.",
        "Pain is constant. I've stopped going out. Nothing helps. Sleep is broken.",
        "Can't function. Catastrophizing daily. Severe fatigue, hopelessness.",
    ],
}

PROFILES = {
    "green": {
        "sNfL": (4.0, 9.5),
        "gamma": (0.9, 1.2),
        "IL6": (1.5, 4.5),
        "TNFa": (3.0, 7.0),
        "IL1b": (1.0, 2.8),
        "subP": (20, 45),
        "BDNF": (18, 26),
        "rom": (3, 12),
        "guard": (0.1, 0.25),
        "hrv": (38, 55),
        "sleep": (82, 92),
        "vel": (0.65, 0.85),
        "vas": (0.5, 3.0),
        "bpi": (0.5, 2.5),
        "dram": (8, 28),
    },
    "yellow": {
        "sNfL": (12, 22),
        "gamma": (1.35, 1.75),
        "IL6": (6, 11),
        "TNFa": (9, 14),
        "IL1b": (3.5, 6.0),
        "subP": (65, 110),
        "BDNF": (10, 16),
        "rom": (18, 32),
        "guard": (0.35, 0.55),
        "hrv": (22, 32),
        "sleep": (65, 78),
        "vel": (0.35, 0.5),
        "vas": (4.0, 6.5),
        "bpi": (4.0, 6.0),
        "dram": (45, 65),
    },
    "red": {
        "sNfL": (28, 42),
        "gamma": (1.9, 2.6),
        "IL6": (13, 22),
        "TNFa": (18, 28),
        "IL1b": (7, 11),
        "subP": (120, 170),
        "BDNF": (5, 10),
        "rom": (38, 55),
        "guard": (0.65, 0.85),
        "hrv": (10, 18),
        "sleep": (45, 62),
        "vel": (0.15, 0.3),
        "vas": (7.5, 9.5),
        "bpi": (7.0, 9.0),
        "dram": (72, 92),
    },
}


def _rng(lo: float, hi: float, ndigits: int = 2) -> float:
    return round(random.uniform(lo, hi), ndigits)


def generate_synthetic_case(severity: str | None = None) -> dict[str, Any]:
    severity = severity or random.choice(["green", "yellow", "red"])
    if severity not in PROFILES:
        severity = "yellow"
    p = PROFILES[severity]

    patient = {
        "id": str(uuid.uuid4()),
        "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "gender": random.choice(["female", "male"]),
        "birth_date": f"19{random.randint(60, 99)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "mrn": f"HCX-{random.randint(10000, 99999)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    biomarkers = {
        "sNfL_pg_per_ml": _rng(*p["sNfL"]),
        "gamma_ratio": _rng(*p["gamma"]),
        "IL6_pg_per_ml": _rng(*p["IL6"]),
        "TNFa_pg_per_ml": _rng(*p["TNFa"]),
        "IL1b_pg_per_ml": _rng(*p["IL1b"]),
        "substance_p_pg_per_ml": _rng(*p["subP"], ndigits=1),
        "BDNF_ng_per_ml": _rng(*p["BDNF"]),
    }
    kinematics = {
        "rom_deficit_pct": _rng(*p["rom"], ndigits=1),
        "guarding_index": _rng(*p["guard"]),
        "hrv_rmssd_ms": _rng(*p["hrv"], ndigits=1),
        "sleep_efficiency_pct": _rng(*p["sleep"], ndigits=1),
        "mean_velocity_mps": _rng(*p["vel"]),
        "joints": _generate_joint_telemetry(p),
    }
    psych = {
        "vas_pain": _rng(*p["vas"], ndigits=1),
        "bpi_interference": _rng(*p["bpi"], ndigits=1),
        "dram_distress": _rng(*p["dram"], ndigits=0),
        "text_note": random.choice(NARRATIVES[severity]),
    }
    return {
        "severity_hint": severity,
        "patient": patient,
        "biomarkers": biomarkers,
        "kinematics": kinematics,
        "psych": psych,
    }


def _generate_joint_telemetry(p: dict[str, Any]) -> list[dict[str, Any]]:
    """Simulate joint coordinates + velocity vectors for 3D viewer."""
    joint_names = [
        "head", "neck", "shoulder_l", "shoulder_r",
        "elbow_l", "elbow_r", "wrist_l", "wrist_r",
        "spine_t", "spine_l", "hip_l", "hip_r",
        "knee_l", "knee_r", "ankle_l", "ankle_r",
    ]
    base_positions = {
        "head": [0, 1.7, 0],
        "neck": [0, 1.5, 0],
        "shoulder_l": [-0.2, 1.4, 0],
        "shoulder_r": [0.2, 1.4, 0],
        "elbow_l": [-0.32, 1.1, 0],
        "elbow_r": [0.32, 1.1, 0],
        "wrist_l": [-0.38, 0.85, 0],
        "wrist_r": [0.38, 0.85, 0],
        "spine_t": [0, 1.2, 0],
        "spine_l": [0, 0.95, 0],
        "hip_l": [-0.13, 0.85, 0],
        "hip_r": [0.13, 0.85, 0],
        "knee_l": [-0.14, 0.45, 0],
        "knee_r": [0.14, 0.45, 0],
        "ankle_l": [-0.14, 0.05, 0],
        "ankle_r": [0.14, 0.05, 0],
    }
    vel_lo, vel_hi = p["vel"]
    guard_lo, guard_hi = p["guard"]
    out = []
    for name in joint_names:
        pos = base_positions[name]
        # add small jitter representing tracked telemetry
        jitter = random.uniform(-0.01, 0.01)
        speed = round(random.uniform(vel_lo, vel_hi), 3)
        guard = round(random.uniform(guard_lo, guard_hi), 3)
        out.append({
            "name": name,
            "position": [round(pos[0] + jitter, 3), round(pos[1] + jitter, 3), round(pos[2] + jitter, 3)],
            "velocity": [round(random.uniform(-speed, speed), 3) for _ in range(3)],
            "guarding": guard,
        })
    return out
