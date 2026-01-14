from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Candidate:
    route_id: str
    polyline: str
    distance_km: float
    duration_min: float
    # MVP: keep minimal; extend later
    loop_closure_m: float
    bbox_area: float
    path_length_ratio: float
    turn_count: int
    # Exercise-related features
    has_stairs: bool = False
    elevation_gain_m: float = 0.0


def calc_features(
    *,
    candidate: Candidate,
    theme: str,
    round_trip_req: bool,
    distance_km_target: float,
    relaxation_step: int,
    candidate_rank_in_theme: int,
    poi_density: float = 0.0,
    park_poi_ratio: float = 0.0,
) -> Dict[str, Any]:
    # Derived
    turn_density = candidate.turn_count / max(candidate.distance_km, 1e-6)
    distance_error_ratio = abs(candidate.distance_km - distance_km_target) / max(distance_km_target, 1e-6)
    round_trip_fit = 1 if candidate.loop_closure_m <= 100.0 else 0
    
    # Exercise-related features
    has_stairs = 1 if candidate.has_stairs else 0
    elevation_gain_m = float(candidate.elevation_gain_m)
    # 標高差密度（標高差/距離）: 運動強度の指標
    elevation_density = elevation_gain_m / max(candidate.distance_km * 1000.0, 1.0)  # m/km

    # One-hot
    theme_exercise = 1 if theme == "exercise" else 0
    theme_think = 1 if theme == "think" else 0
    theme_refresh = 1 if theme == "refresh" else 0
    theme_nature = 1 if theme == "nature" else 0

    return {
        "distance_km": float(candidate.distance_km),
        "duration_min": float(candidate.duration_min),
        "loop_closure_m": float(candidate.loop_closure_m),
        "bbox_area": float(candidate.bbox_area),
        "path_length_ratio": float(candidate.path_length_ratio),
        "turn_count": int(candidate.turn_count),
        "turn_density": float(turn_density),

        "theme_exercise": theme_exercise,
        "theme_think": theme_think,
        "theme_refresh": theme_refresh,
        "theme_nature": theme_nature,

        "round_trip_req": 1 if round_trip_req else 0,
        "round_trip_fit": int(round_trip_fit),
        "distance_error_ratio": float(distance_error_ratio),

        "relaxation_step": int(relaxation_step),
        "candidate_rank_in_theme": int(candidate_rank_in_theme),

        # Exercise-related features
        "has_stairs": int(has_stairs),
        "elevation_gain_m": float(elevation_gain_m),
        "elevation_density": float(elevation_density),  # m/km

        # Optional (MVP: 0.0 if unavailable)
        "poi_density": float(poi_density),
        "park_poi_ratio": float(park_poi_ratio),
    }
