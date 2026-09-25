# app/services/route_optimizer.py

import math
from typing import NamedTuple


class Point(NamedTuple):
    id: str          # TripPlace id, used to map back to the database row
    latitude: float
    longitude: float


def haversine_distance(a: Point, b: Point) -> float:
    """
    Calculates straight-line distance in kilometers between two
    lat/lng points using the Haversine formula.
    """
    R = 6371  # Earth's radius in km

    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(h))

    return R * c


def total_route_distance(route: list[Point]) -> float:
    return sum(
        haversine_distance(route[i], route[i + 1])
        for i in range(len(route) - 1)
    )


def nearest_neighbor_route(start: Point, places: list[Point]) -> list[Point]:
    """
    Builds an initial route by always jumping to the closest unvisited place.
    Does not know about any fixed end point - see optimize_route for that.
    """
    unvisited = places.copy()
    route = [start]
    current = start

    while unvisited:
        nearest = min(unvisited, key=lambda p: haversine_distance(current, p))
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return route


def two_opt(route: list[Point]) -> list[Point]:
    """
    Improves a route by repeatedly reversing segments that reduce total distance,
    until no further improvement is found.

    Note: this never moves route[0] or route[-1] - i and j are always chosen
    strictly between them. That's what lets optimize_route reuse this unchanged
    to also hold a fixed END point: append it to the route before calling
    two_opt, and it stays pinned in last place while everything between the
    two fixed ends gets reordered.
    """
    improved = True
    best_route = route

    while improved:
        improved = False
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                candidate = (
                    best_route[:i] + best_route[i:j + 1][::-1] + best_route[j + 1:]
                )
                if total_route_distance(candidate) < total_route_distance(best_route):
                    best_route = candidate
                    improved = True

    return best_route


def optimize_route(start: Point, places: list[Point], end: Point | None = None) -> dict:
    """
    Main entry point: returns the optimized order plus distance metrics.

    start is always fixed as the first stop. If end is given, it's fixed as
    the LAST stop and is NOT included in ordered_place_ids (it isn't a place
    to add to the trip, just where the route has to finish) - the places in
    between are ordered to make that start-to-end route as short as possible.
    If end is None, behavior is unchanged from before: the route just ends
    wherever nearest-neighbor + 2-opt leaves it.
    """
    route_with_places = [start] + places
    original_route = route_with_places + [end] if end is not None else route_with_places
    original_distance = total_route_distance(original_route)

    initial_places_order = nearest_neighbor_route(start, places)
    initial_route = initial_places_order + [end] if end is not None else initial_places_order

    optimized_route = two_opt(initial_route)
    optimized_distance = total_route_distance(optimized_route)

    ordered_places = optimized_route[1:]  # drop start
    if end is not None:
        ordered_places = ordered_places[:-1]  # drop end - it's a destination, not a place on the trip

    return {
        "ordered_place_ids": [p.id for p in ordered_places],
        "original_distance_km": round(original_distance, 2),
        "optimized_distance_km": round(optimized_distance, 2),
        "distance_saved_km": round(original_distance - optimized_distance, 2),
    }