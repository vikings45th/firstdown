from __future__ import annotations

from typing import List, Tuple


def decode_polyline(encoded: str) -> List[Tuple[float, float]]:
    """Decode a Google encoded polyline into a list of (lat, lng).

    This is the standard Encoded Polyline Algorithm Format used by Google Maps.
    """
    if not encoded:
        return []

    index = 0
    lat = 0
    lng = 0
    coordinates: List[Tuple[float, float]] = []

    length = len(encoded)

    while index < length:
        # Decode latitude
        shift = 0
        result = 0
        while True:
            if index >= length:
                return coordinates
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        # Decode longitude
        shift = 0
        result = 0
        while True:
            if index >= length:
                return coordinates
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append((lat / 1e5, lng / 1e5))
    return coordinates


def sample_points(points: List[Tuple[float, float]], ratios: List[float]) -> List[Tuple[float, float]]:
    """
    Pick a few representative points from a polyline by ratio [0..1].
    
    Improved algorithm to stably extract 25/50/75% points:
    - For single point: returns that point
    - For 2 points: returns both (0% and 100%)
    - For 3+ points: returns points at specified ratios (25%, 50%, 75%)
    """
    if not points:
        return []
    n = len(points)
    
    # Edge cases
    if n == 1:
        return [points[0]]
    if n == 2:
        # For 2 points, return both (start and end)
        return [points[0], points[1]]
    
    out: List[Tuple[float, float]] = []
    for r in ratios:
        r = max(0.0, min(1.0, float(r)))
        # Use floor to ensure stable indexing: 0.25 -> floor(0.25 * (n-1))
        # This ensures 25% is closer to start, 50% is middle, 75% is closer to end
        idx = int(r * (n - 1))
        # Clamp to valid range
        idx = max(0, min(n - 1, idx))
        out.append(points[idx])
    
    # de-dupe while preserving order
    uniq: List[Tuple[float, float]] = []
    seen = set()
    for p in out:
        if p in seen:
            continue
        seen.add(p)
        uniq.append(p)
    return uniq
