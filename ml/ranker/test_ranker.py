"""
Ranker 単体テスト: 入力固定で順序が崩れないことを確認
"""
import pytest
from app.main import rank, _calculate_score
from app.schemas import RankRequest, RankRoute


def test_score_calculation_deterministic():
    """スコア計算が決定的であることを確認"""
    features1 = {
        "distance_error_ratio": 0.1,
        "round_trip_req": 1,
        "round_trip_fit": 1,
        "loop_closure_m": 50.0,
        "park_poi_ratio": 0.3,
        "poi_density": 0.5,
    }
    
    score1, breakdown1 = _calculate_score(features1)
    score2, breakdown2 = _calculate_score(features1)
    
    assert score1 == score2, "同じ入力で同じスコアが返されるべき"
    assert breakdown1 == breakdown2, "同じ入力で同じ内訳が返されるべき"


def test_score_ordering_stable():
    """入力固定で順序が崩れないことを確認"""
    routes = [
        RankRoute(
            route_id="route_1",
            features={
                "distance_error_ratio": 0.05,  # 距離誤差が小さい
                "round_trip_req": 1,
                "round_trip_fit": 1,
                "loop_closure_m": 30.0,  # ループ閉鎖が良い
                "park_poi_ratio": 0.4,
                "poi_density": 0.6,
            }
        ),
        RankRoute(
            route_id="route_2",
            features={
                "distance_error_ratio": 0.2,  # 距離誤差が大きい
                "round_trip_req": 1,
                "round_trip_fit": 0,
                "loop_closure_m": 200.0,  # ループ閉鎖が悪い
                "park_poi_ratio": 0.1,
                "poi_density": 0.2,
            }
        ),
        RankRoute(
            route_id="route_3",
            features={
                "distance_error_ratio": 0.1,  # 中間
                "round_trip_req": 0,  # 往復不要
                "round_trip_fit": 0,
                "loop_closure_m": 1000.0,
                "park_poi_ratio": 0.2,
                "poi_density": 0.3,
            }
        ),
    ]
    
    req = RankRequest(request_id="test-001", routes=routes)
    response = rank(req)
    
    # スコア順にソートされていることを確認
    assert len(response.scores) == 3, "すべてのルートがスコアリングされる"
    assert response.scores[0].score >= response.scores[1].score, "降順でソートされている"
    assert response.scores[1].score >= response.scores[2].score, "降順でソートされている"
    
    # route_1が最高スコアであることを確認
    assert response.scores[0].route_id == "route_1", "距離誤差が小さく、loop closureが良いroute_1が最高スコア"
    
    # 複数回実行しても同じ順序であることを確認
    response2 = rank(req)
    assert [s.route_id for s in response2.scores] == [s.route_id for s in response.scores], "同じ入力で同じ順序"


def test_score_breakdown_present():
    """スコア内訳が含まれていることを確認"""
    routes = [
        RankRoute(
            route_id="route_1",
            features={
                "distance_error_ratio": 0.1,
                "round_trip_req": 1,
                "round_trip_fit": 1,
                "loop_closure_m": 50.0,
                "park_poi_ratio": 0.3,
                "poi_density": 0.5,
            }
        ),
    ]
    
    req = RankRequest(request_id="test-002", routes=routes)
    response = rank(req)
    
    assert len(response.scores) == 1
    assert response.scores[0].breakdown is not None, "スコア内訳が含まれている"
    assert "base" in response.scores[0].breakdown
    assert "distance_penalty" in response.scores[0].breakdown
    assert "loop_closure_bonus" in response.scores[0].breakdown
    assert "poi_bonus" in response.scores[0].breakdown
    assert "final_score" in response.scores[0].breakdown


def test_score_range():
    """スコアが0.0-1.0の範囲内であることを確認"""
    test_cases = [
        {"distance_error_ratio": 0.0, "round_trip_req": 0, "park_poi_ratio": 0.0, "poi_density": 0.0},
        {"distance_error_ratio": 1.0, "round_trip_req": 1, "loop_closure_m": 10.0, "park_poi_ratio": 1.0, "poi_density": 1.0},
        {"distance_error_ratio": 0.5, "round_trip_req": 1, "loop_closure_m": 300.0, "park_poi_ratio": 0.5, "poi_density": 0.5},
    ]
    
    for features in test_cases:
        score, _ = _calculate_score(features)
        assert 0.0 <= score <= 1.0, f"スコアは0.0-1.0の範囲内: {score}"


def test_distance_penalty():
    """距離乖離ペナルティが正しく機能することを確認"""
    features_low_error = {"distance_error_ratio": 0.05}
    features_high_error = {"distance_error_ratio": 0.5}
    
    score_low, _ = _calculate_score(features_low_error)
    score_high, _ = _calculate_score(features_high_error)
    
    assert score_low > score_high, "距離誤差が小さい方がスコアが高い"


def test_loop_closure_bonus():
    """Loop closure ボーナスが正しく機能することを確認"""
    features_good = {"round_trip_req": 1, "loop_closure_m": 50.0}
    features_bad = {"round_trip_req": 1, "loop_closure_m": 1000.0}
    
    score_good, _ = _calculate_score(features_good)
    score_bad, _ = _calculate_score(features_bad)
    
    assert score_good > score_bad, "loop_closure_mが小さい方がスコアが高い"


def test_poi_bonus():
    """POI ボーナスが正しく機能することを確認"""
    features_high_poi = {"park_poi_ratio": 0.8, "poi_density": 0.9}
    features_low_poi = {"park_poi_ratio": 0.1, "poi_density": 0.1}
    
    score_high, _ = _calculate_score(features_high_poi)
    score_low, _ = _calculate_score(features_low_poi)
    
    assert score_high > score_low, "POI数が多い方がスコアが高い"
