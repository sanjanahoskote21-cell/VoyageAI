# backend/scripts/dedupe_places.py
"""
Finds Place rows that are really the same place saved twice under different
casing (e.g. "Mysore Palace" / city "Mysore" vs "Mysore Palace" / city
"mysore" - this happens because sync_places_for_city() upserts by
external_place_id, so a manually-seeded row and a synced row never collide
even though they're the same place).

For each duplicate group, one row is kept (the "keeper") and the rest
("losers") are removed. Any trip that already added a loser is repointed
to the keeper first, via a straight SQL UPDATE - so no trip's saved places,
budget or route are affected by this cleanup.

Choosing the keeper, in order:
  1. A row some TripPlace already points to (never orphan a real trip).
  2. Otherwise, the row with the higher avg_rating.
  3. Otherwise, the row with the most recent last_synced_at.
  4. Otherwise, just the first one found - deterministic, not arbitrary.

DRY RUN BY DEFAULT - only prints what it would do. Add --apply to make it
write to the database:
    python scripts/dedupe_places.py            # preview
    python scripts/dedupe_places.py --apply     # actually merge
"""
import sys
import os
import argparse
from collections import defaultdict
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal
from app.models.place import Place
from app.models.trip import TripPlace

# Querying Place configures every mapper in the app's shared declarative
# registry, because TripPlace.trip -> Trip, and Trip has relationships that
# reference "User" and "ChatMessage" by string name (see app/models/trip.py).
# SQLAlchemy only resolves those names against classes that have actually
# been imported somewhere - these imports exist only to register them, even
# though this script never uses them directly. Without this, querying Place
# raises: sqlalchemy.exc.InvalidRequestError: ... failed to locate a name ('User').
from app.models.user import User  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.budget import BudgetEstimate  # noqa: F401


def _sort_key(place: Place, referenced_ids: set):
    # Higher is "better" (more deserving of being the keeper). Python's max()
    # picks the largest tuple, comparing element by element - so this alone
    # decides the order in find_duplicate_groups. Every element is always
    # the same, always-comparable type (bool / float / datetime / str), so
    # this never raises even when some rows are missing a rating or a sync
    # timestamp.
    return (
        place.id in referenced_ids,
        place.avg_rating or 0.0,
        place.last_synced_at or datetime.min,
        str(place.id),  # deterministic final tie-break, never arbitrary
    )


def find_duplicate_groups(db) -> list[tuple[Place, list[Place]]]:
    """Returns [(keeper, [losers]), ...] for every (name, city) that has more
    than one Place row, case-insensitive on both fields."""
    places = db.query(Place).all()
    referenced_ids = {tp.place_id for tp in db.query(TripPlace).all() if tp.place_id}

    groups = defaultdict(list)
    for p in places:
        key = (p.name.strip().lower(), p.city.strip().lower())
        groups[key].append(p)

    duplicate_groups = []
    for rows in groups.values():
        if len(rows) < 2:
            continue
        keeper = max(rows, key=lambda p: _sort_key(p, referenced_ids))
        losers = [p for p in rows if p.id != keeper.id]
        duplicate_groups.append((keeper, losers))

    return duplicate_groups


def merge_duplicates(db, apply: bool) -> int:
    duplicate_groups = find_duplicate_groups(db)

    if not duplicate_groups:
        print("No duplicate places found.")
        return 0

    for keeper, losers in duplicate_groups:
        print(f"\n'{keeper.name}' ({keeper.city}) - {len(losers)} duplicate(s):")
        print(f"  KEEP   {keeper.id}  city={keeper.city!r}  rating={keeper.avg_rating}")
        for loser in losers:
            print(f"  REMOVE {loser.id}  city={loser.city!r}  rating={loser.avg_rating}")

        if not apply:
            continue

        loser_ids = [loser.id for loser in losers]
        # Repoint any trip's saved place to the keeper BEFORE deleting the
        # loser rows, so no trip is left with a dangling place_id.
        db.query(TripPlace).filter(TripPlace.place_id.in_(loser_ids)).update(
            {TripPlace.place_id: keeper.id}, synchronize_session=False
        )
        for loser in losers:
            db.delete(loser)

    if apply:
        db.commit()
        print(f"\nDone. Merged {sum(len(losers) for _, losers in duplicate_groups)} duplicate row(s).")
    else:
        print(f"\nDry run only - {sum(len(losers) for _, losers in duplicate_groups)} row(s) would be removed. Re-run with --apply to make this change.")

    return len(duplicate_groups)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually write the merge (default: dry run / preview only)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        merge_duplicates(db, apply=args.apply)
    finally:
        db.close()