from typing import Any, Dict, List, Optional


def choose_best_route(
    candidates: List[Dict[str, Any]],
    scores: Dict[str, float],
    theme: str,
) -> Optional[Dict[str, Any]]:
    """
    candidates: list of {"route_id", "theme", ...}
    scores: route_id -> score
    rule: theme match first; within same theme, highest score;
          if no score available, pick first theme-matching candidate.
    """
    themed = [c for c in candidates if c.get("theme") == theme]
    pool = themed if themed else candidates
    if not pool:
        return None

    scored = [(c, scores.get(c["route_id"])) for c in pool]
    scored_with = [x for x in scored if x[1] is not None]
    if scored_with:
        scored_with.sort(key=lambda x: x[1], reverse=True)
        return scored_with[0][0]

    # No scores available => deterministic fallback
    return pool[0]
