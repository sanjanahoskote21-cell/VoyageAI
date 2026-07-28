# tests/services/test_route_optimizer.py

import math
import pytest

from app.services.route_optimizer import (
    Point,
    haversine_distance,
    total_route_distance,
    nearest_neighbor_route,
    two_opt,
    optimize_route,
)


# ── haversine_distance ──────────────────────────────────────────────

def test_haversine_distance_same_point_is_zero():
    p = Point(id="a", latitude=12.9716, longitude=77.5946)
    assert haversine_distance(p, p) == 0.0


def test_haversine_distance_is_symmetric():
    a = Point(id="a", latitude=12.9716, longitude=77.5946)  # Bengaluru
    b = Point(id="b", latitude=12.2958, longitude=76.6394)  # Mysore
    assert haversine_distance(a, b) == pytest.approx(haversine_distance(b, a))


def test_haversine_distance_known_value_bengaluru_to_mysore():
    # Real-world distance is ~140km; Haversine (straight-line) should land
    # a bit under that, in the ~120-140km range.
    bengaluru = Point(id="a", latitude=12.9716, longitude=77.5946)
    mysore = Point(id="b", latitude=12.2958, longitude=76.6394)
    distance = haversine_distance(bengaluru, mysore)
    assert 100 < distance < 150


def test_haversine_distance_never_negative():
    a = Point(id="a", latitude=-33.8688, longitude=151.2093)  # Sydney
    b = Point(id="b", latitude=51.5072, longitude=-0.1276)    # London
    assert haversine_distance(a, b) > 0


# ── total_route_distance ────────────────────────────────────────────

def test_total_route_distance_empty_route_is_zero():
    assert total_route_distance([]) == 0.0


def test_total_route_distance_single_point_is_zero():
    p = Point(id="a", latitude=0.0, longitude=0.0)
    assert total_route_distance([p]) == 0.0


def test_total_route_distance_sums_consecutive_legs():
    a = Point(id="a", latitude=0.0, longitude=0.0)
    b = Point(id="b", latitude=0.0, longitude=1.0)
    c = Point(id="c", latitude=0.0, longitude=2.0)
    expected = haversine_distance(a, b) + haversine_distance(b, c)
    assert total_route_distance([a, b, c]) == pytest.approx(expected)


# ── nearest_neighbor_route ──────────────────────────────────────────

def test_nearest_neighbor_visits_every_place_exactly_once():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    places = [
        Point(id="a", latitude=0.0, longitude=1.0),
        Point(id="b", latitude=0.0, longitude=2.0),
        Point(id="c", latitude=0.0, longitude=3.0),
    ]
    route = nearest_neighbor_route(start, places)

    assert route[0] == start
    assert len(route) == len(places) + 1
    # every place appears exactly once, none dropped or duplicated
    assert sorted(p.id for p in route[1:]) == sorted(p.id for p in places)


def test_nearest_neighbor_picks_closest_first():
    # Places placed at increasing distance from start along a line — the
    # greedy nearest-neighbor choice is unambiguous here, so the order is
    # fully predictable: closest first, each step.
    start = Point(id="start", latitude=0.0, longitude=0.0)
    near = Point(id="near", latitude=0.0, longitude=1.0)
    mid = Point(id="mid", latitude=0.0, longitude=2.0)
    far = Point(id="far", latitude=0.0, longitude=5.0)

    route = nearest_neighbor_route(start, [far, near, mid])  # shuffled input
    assert [p.id for p in route] == ["start", "near", "mid", "far"]


def test_nearest_neighbor_with_no_places_returns_just_start():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    route = nearest_neighbor_route(start, [])
    assert route == [start]


# ── two_opt ──────────────────────────────────────────────────────────

def test_two_opt_never_makes_a_route_worse():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    places = [
        Point(id="a", latitude=0.3, longitude=0.9),
        Point(id="b", latitude=1.1, longitude=0.2),
        Point(id="c", latitude=0.6, longitude=1.4),
        Point(id="d", latitude=1.4, longitude=1.1),
    ]
    initial = nearest_neighbor_route(start, places)
    improved = two_opt(initial)

    assert total_route_distance(improved) <= total_route_distance(initial)


def test_two_opt_uncrosses_a_known_bad_route():
    # Four corners of a square. A route that zigzags across the diagonals
    # is provably worse than one that walks the perimeter. This route is
    # built by hand (not via nearest-neighbor) specifically to contain a
    # crossing, so this test checks 2-opt's actual job: untangling it.
    s = Point(id="s", latitude=0.0, longitude=0.0)   # bottom-left
    a = Point(id="a", latitude=0.0, longitude=1.0)   # bottom-right
    b = Point(id="b", latitude=1.0, longitude=1.0)   # top-right
    c = Point(id="c", latitude=1.0, longitude=0.0)   # top-left

    crossed_route = [s, b, a, c]  # s→b and a→c cross through the middle
    fixed_route = two_opt(crossed_route)

    crossed_distance = total_route_distance(crossed_route)
    fixed_distance = total_route_distance(fixed_route)

    assert fixed_distance < crossed_distance
    # every point still present exactly once — 2-opt reorders, never drops
    assert sorted(p.id for p in fixed_route) == sorted(p.id for p in crossed_route)


def test_two_opt_on_already_optimal_route_is_unchanged_in_distance():
    # A straight line is already optimal — 2-opt shouldn't be able to
    # improve on it, and shouldn't make it worse either.
    route = [
        Point(id="a", latitude=0.0, longitude=0.0),
        Point(id="b", latitude=0.0, longitude=1.0),
        Point(id="c", latitude=0.0, longitude=2.0),
        Point(id="d", latitude=0.0, longitude=3.0),
    ]
    result = two_opt(route)
    assert total_route_distance(result) == pytest.approx(total_route_distance(route))


def test_two_opt_handles_short_routes_without_error():
    # Routes with fewer than 3 points have no valid segment to reverse —
    # this should be a no-op, not a crash.
    start_only = [Point(id="a", latitude=0.0, longitude=0.0)]
    two_points = [
        Point(id="a", latitude=0.0, longitude=0.0),
        Point(id="b", latitude=1.0, longitude=1.0),
    ]
    assert two_opt(start_only) == start_only
    assert two_opt(two_points) == two_points


# ── optimize_route (full pipeline) ──────────────────────────────────

def test_optimize_route_returns_expected_keys():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    places = [Point(id="a", latitude=0.0, longitude=1.0)]
    result = optimize_route(start, places)

    assert set(result.keys()) == {
        "ordered_place_ids",
        "original_distance_km",
        "optimized_distance_km",
        "distance_saved_km",
    }


def test_optimize_route_includes_every_place_exactly_once():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    places = [
        Point(id="a", latitude=0.3, longitude=0.9),
        Point(id="b", latitude=1.1, longitude=0.2),
        Point(id="c", latitude=0.6, longitude=1.4),
    ]
    result = optimize_route(start, places)

    assert sorted(result["ordered_place_ids"]) == sorted(p.id for p in places)
    assert start.id not in result["ordered_place_ids"]  # start is excluded


def test_optimize_route_optimized_never_exceeds_original():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    places = [
        Point(id="a", latitude=0.3, longitude=0.9),
        Point(id="b", latitude=1.1, longitude=0.2),
        Point(id="c", latitude=0.6, longitude=1.4),
        Point(id="d", latitude=1.4, longitude=1.1),
    ]
    result = optimize_route(start, places)
    assert result["optimized_distance_km"] <= result["original_distance_km"]
    assert result["distance_saved_km"] == pytest.approx(
        result["original_distance_km"] - result["optimized_distance_km"]
    )


def test_optimize_route_with_no_places():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    result = optimize_route(start, [])

    assert result["ordered_place_ids"] == []
    assert result["original_distance_km"] == 0.0
    assert result["optimized_distance_km"] == 0.0
    assert result["distance_saved_km"] == 0.0


def test_optimize_route_with_single_place():
    start = Point(id="start", latitude=0.0, longitude=0.0)
    place = Point(id="a", latitude=1.0, longitude=1.0)
    result = optimize_route(start, [place])

    assert result["ordered_place_ids"] == ["a"]
    # only one possible route with a single place — nothing to optimize
    assert result["distance_saved_km"] == 0.0