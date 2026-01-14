from typing import Any, Dict, List, Tuple
import logging
import httpx

from app.settings import settings

logger = logging.getLogger(__name__)


async def rank_routes(
    request_id: str,
    routes: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Call internal Ranker API. Partial success allowed.
    routes: [{"route_id": "...", "features": {...}}, ...]
    Returns (scores, failed_route_ids)
    """
    payload = {"request_id": request_id, "routes": routes}

    timeout = httpx.Timeout(settings.RANKER_TIMEOUT_SEC)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{settings.RANKER_URL}/rank", json=payload)
    except httpx.TimeoutException as e:
        logger.error(
            "[Ranker Timeout] request_id=%s timeout_sec=%.1f err=%r",
            request_id,
            settings.RANKER_TIMEOUT_SEC,
            e,
        )
        raise
    except httpx.RequestError as e:
        logger.error("[Ranker Request Error] request_id=%s err=%r", request_id, e)
        raise

    if r.status_code == 200:
        data = r.json()
        return data.get("scores", []), data.get("failed_route_ids", [])
    if r.status_code != 200:
        logger.warning(
            "[Ranker HTTP] request_id=%s status=%d body=%s",
            request_id,
            r.status_code,
            r.text[:500],
        )
    if r.status_code == 422:
        # Ranker could not score any route
        return [], [x.get("route_id") for x in routes if "route_id" in x]
    r.raise_for_status()
    return [], []
