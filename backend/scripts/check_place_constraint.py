# backend/scripts/check_place_constraint.py
"""
Proves the unique (name, city) constraint on places works.

Tries to insert a case/whitespace variant of an existing place.
  - IntegrityError  -> constraint works (PASS)
  - No error        -> constraint missing; the test row is deleted again (FAIL)

Usage (from backend/, venv active, Supabase awake):
    python -m scripts.check_place_constraint
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.place import Place

# Register every model so mapper configuration doesn't fail (same reason
# as in dedupe_places.py).
from app.models.trip import TripPlace  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.budget import BudgetEstimate  # noqa: F401


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Place).first()
        if existing is None:
            print("No places in the database - seed one first, then rerun.")
            return

        test_row = Place(
            name=existing.name.upper() + "  ",
            city=existing.city.lower(),
            category="constraint-test",
            latitude=0.0,
            longitude=0.0,
        )
        db.add(test_row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print(f"PASS - duplicate of '{existing.name}' ({existing.city}) was rejected.")
            return

        # Insert succeeded, so the constraint is NOT active. Clean up.
        db.delete(test_row)
        db.commit()
        print("FAIL - duplicate was accepted. Did 'alembic upgrade head' run? Test row removed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()