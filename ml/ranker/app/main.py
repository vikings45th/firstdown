from __future__ import annotations
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from app.schemas import RankRequest, RankResponse, ScoreItem
from app.settings import settings

app = FastAPI(title="firstdown Ranker API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


def _calculate_score(features: Dict[str, Any]) -> tuple[float, Dict[str, float]]:
    """
    ルールベーススコアリング: 距離乖離 / loop closure / poi 数を考慮
    
    Returns:
        (score, breakdown): スコアと内訳
    """
    # 1. 距離乖離ペナルティ（距離誤差が小さいほど良い）
    distance_error_ratio = float(features.get("distance_error_ratio", 0.0))
    distance_penalty = -distance_error_ratio * 0.5  # 誤差が大きいほど減点
    
    # 2. Loop closure ボーナス（往復ルート適合度）
    round_trip_req = features.get("round_trip_req", 0)
    round_trip_fit = features.get("round_trip_fit", 0)
    loop_closure_bonus = 0.0
    if round_trip_req:
        # 往復ルートが要求されている場合、loop_closure_mが小さいほど良い
        loop_closure_m = float(features.get("loop_closure_m", 1000.0))
        if loop_closure_m <= 100.0:
            loop_closure_bonus = 0.2  # 100m以内ならボーナス
        elif loop_closure_m <= 500.0:
            loop_closure_bonus = 0.1  # 500m以内なら小さいボーナス
        # round_trip_fitも考慮（後方互換性）
        if round_trip_fit:
            loop_closure_bonus = max(loop_closure_bonus, 0.2)
    
    # 3. POI 数ボーナス（park_poi_ratioとpoi_densityを考慮）
    park_poi_ratio = float(features.get("park_poi_ratio", 0.0))
    poi_density = float(features.get("poi_density", 0.0))
    poi_bonus = park_poi_ratio * 0.15 + min(poi_density, 1.0) * 0.1  # 上限あり
    
    # ベーススコア
    base = 0.5
    
    # 合計
    score = base + distance_penalty + loop_closure_bonus + poi_bonus
    score = max(0.0, min(1.0, score))  # 0.0-1.0にクリップ
    
    # 内訳（debug用）
    breakdown = {
        "base": base,
        "distance_penalty": distance_penalty,
        "loop_closure_bonus": loop_closure_bonus,
        "poi_bonus": poi_bonus,
        "final_score": score,
    }
    
    return score, breakdown


@app.post("/rank", response_model=RankResponse)
def rank(req: RankRequest) -> RankResponse:
    """
    MVP: rule-based stub scoring. Replace with Vertex AI later.
    
    スコアリングロジック:
    - 距離乖離: 目標距離との誤差が小さいほど良い（ペナルティ方式）
    - Loop closure: 往復ルート要求時、loop_closure_mが小さいほど良い
    - POI数: park_poi_ratioとpoi_densityが高いほど良い
    """
    scores = []
    failed = []

    for r in req.routes:
        try:
            score, breakdown = _calculate_score(r.features)
            scores.append(ScoreItem(route_id=r.route_id, score=score, breakdown=breakdown))
        except Exception as e:
            failed.append(r.route_id)

    if len(scores) == 0:
        raise HTTPException(status_code=422, detail="No successful inference")

    # スコア順にソート（高い順）
    scores.sort(key=lambda x: x.score, reverse=True)

    return RankResponse(scores=scores, failed_route_ids=failed)
