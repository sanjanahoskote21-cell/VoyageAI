# backend/scripts/seed_extra_cities.py
"""
Adds Hotel and Restaurant rate rows for cities that come up as custom places
but have no seeded data of their own - right now: Ballari and Hampi.

Without this, calculate_budget() in budget_service.py still works (it falls
back to the tier-wide average), but the number isn't backed by real data for
these two cities the way Coorg and Mysore are.

Safe to re-run: it only inserts a (city, budget_tier) pair that doesn't
already exist, so running this twice does not create duplicate rows.

Usage (from the backend/ folder, with your venv active):
    python scripts/seed_extra_cities.py
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal
from app.models.hotel import Hotel
from app.models.restaurant import Restaurant

# Rough estimates, in the same range as this project's other Karnataka
# towns (Coorg/Mysore mid-tier hotels run ~2200-2400, food ~650-700).
# Adjust these to match real prices if you have better numbers.
HOTEL_RATES = {
    "Ballari": {"budget": 900, "mid": 2100, "luxury": 4800},
    "Hampi":   {"budget": 1000, "mid": 2300, "luxury": 5200},  # tourist-town premium over Ballari
}
FOOD_RATES = {
    "Ballari": {"budget": 280, "mid": 650, "luxury": 1400},
    "Hampi":   {"budget": 320, "mid": 700, "luxury": 1500},
}


def seed_extra_cities(db) -> int:
    added = 0

    for city, tiers in HOTEL_RATES.items():
        for tier, price in tiers.items():
            exists = (
                db.query(Hotel)
                .filter(Hotel.city.ilike(city), Hotel.budget_tier == tier)
                .first()
            )
            if exists:
                continue
            db.add(Hotel(name=f"{city} {tier.title()} Stay", city=city, budget_tier=tier, price_per_night=price))
            added += 1

    for city, tiers in FOOD_RATES.items():
        for tier, price in tiers.items():
            exists = (
                db.query(Restaurant)
                .filter(Restaurant.city.ilike(city), Restaurant.budget_tier == tier)
                .first()
            )
            if exists:
                continue
            db.add(Restaurant(name=f"{city} {tier.title()} Dining", city=city, budget_tier=tier, avg_cost_per_person_per_day=price))
            added += 1

    db.commit()
    return added


if __name__ == "__main__":
    db = SessionLocal()
    try:
        count = seed_extra_cities(db)
        print(f"Added {count} new hotel/restaurant rows (existing ones were left untouched).")
    finally:
        db.close()