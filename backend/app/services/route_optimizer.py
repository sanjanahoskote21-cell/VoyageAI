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


def optimize_route(start: Point, places: list[Point]) -> dict:
    """
    Main entry point: returns the optimized order plus distance metrics.
    """
    original_route = [start] + places
    original_distance = total_route_distance(original_route)

    initial_route = nearest_neighbor_route(start, places)
    optimized_route = two_opt(initial_route)
    optimized_distance = total_route_distance(optimized_route)

    return {
        "ordered_place_ids": [p.id for p in optimized_route[1:]],  # exclude start
        "original_distance_km": round(original_distance, 2),
        "optimized_distance_km": round(optimized_distance, 2),
        "distance_saved_km": round(original_distance - optimized_distance, 2),
    }