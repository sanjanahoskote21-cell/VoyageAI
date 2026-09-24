# app/services/budget_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.hotel import Hotel
from app.models.restaurant import Restaurant

HOTEL_FALLBACK_RATES = {"budget": 800, "mid": 2000, "luxury": 5000}
FOOD_FALLBACK_RATES = {"budget": 300, "mid": 700, "luxury": 1500}

MILEAGE_KM_PER_LITER = {"car": 15, "bike": 40}
FUEL_PRICE_PER_LITER = 105
PUBLIC_TRANSPORT_RATE_PER_KM = 2
MISC_BUFFER_PERCENT = 0.10


def _avg_rate(db: Session, model, price_column, budget_tier: str, city: str | None = None) -> float | None:
    """Average price for a tier, optionally for one city (case-insensitive).
    Returns None when there are no matching rows."""
    query = db.query(func.avg(price_column)).filter(model.budget_tier == budget_tier)
    if city is not None:
        query = query.filter(func.lower(model.city) == city.lower())
    value = query.scalar()
    return float(value) if value is not None else None


def _average_rate(db: Session, model, price_column, cities: list[str], budget_tier: str, constant_rates: dict) -> float:
    """Prices EACH city separately, then averages across cities.
    A city with no data is estimated with the tier-wide average (or the constant
    if the table has nothing for that tier) instead of being silently ignored."""
    constant = constant_rates.get(budget_tier, constant_rates["mid"])
    if not cities:
        return constant

    default = _avg_rate(db, model, price_column, budget_tier)
    if default is None:
        default = constant

    unique_cities = {c.lower(): c for c in cities}.values()  # "mysore" and "Mysore" count once
    rates = []
    for city in unique_cities:
        rate = _avg_rate(db, model, price_column, budget_tier, city)
        rates.append(rate if rate is not None else default)

    return sum(rates) / len(rates)


def get_average_hotel_rate(db: Session, cities: list[str], budget_tier: str) -> float:
    return _average_rate(db, Hotel, Hotel.price_per_night, cities, budget_tier, HOTEL_FALLBACK_RATES)


def get_average_food_rate(db: Session, cities: list[str], budget_tier: str) -> float:
    return _average_rate(
        db, Restaurant, Restaurant.avg_cost_per_person_per_day, cities, budget_tier, FOOD_FALLBACK_RATES
    )


def calculate_budget(
    db: Session,
    cities: list[str],
    budget_tier: str,
    num_days: int,
    num_travelers: int,
    total_distance_km: float,
    travel_mode: str,
) -> dict:
    if budget_tier not in FOOD_FALLBACK_RATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid budget_tier: {budget_tier}",
        )

    hotel_rate = get_average_hotel_rate(db, cities, budget_tier)
    hotel_cost = hotel_rate * num_days

    food_rate = get_average_food_rate(db, cities, budget_tier)
    food_cost = food_rate * num_days * num_travelers

    if travel_mode in MILEAGE_KM_PER_LITER:
        liters_needed = total_distance_km / MILEAGE_KM_PER_LITER[travel_mode]
        fuel_cost = liters_needed * FUEL_PRICE_PER_LITER
    elif travel_mode == "public_transport":
        fuel_cost = total_distance_km * PUBLIC_TRANSPORT_RATE_PER_KM * num_travelers
    else:
        fuel_cost = 0

    subtotal = hotel_cost + food_cost + fuel_cost
    misc_cost = subtotal * MISC_BUFFER_PERCENT
    total_cost = subtotal + misc_cost

    return {
        "hotel_cost": round(hotel_cost, 2),
        "food_cost": round(food_cost, 2),
        "fuel_cost": round(fuel_cost, 2),
        "misc_cost": round(misc_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_day": round(total_cost / num_days, 2) if num_days else 0,
        "cost_per_person": round(total_cost / num_travelers, 2) if num_travelers else 0,
    }