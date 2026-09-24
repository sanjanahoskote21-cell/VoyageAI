"""
travel_twin_service.py
Travel Twin - AI trip companion chat, using context-stuffing (Option A):
fetch trip data once per request, build one prompt, call Gemini.
"""

import time

from fastapi import HTTPException, status
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.trip import Trip
from app.models.chat_message import ChatMessage
from app.services.geo_utils import haversine_km
from app.services.trip_service import geocode_place_name

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-3.6-flash"  # versioned, stable - avoids the broken "-latest" alias
CHAT_HISTORY_LIMIT = 10  # only send the last N messages, keeps prompt size bounded
GEMINI_RETRIES = 2  # extra attempts when Gemini is overloaded (503) - these spikes are usually brief
GEMINI_RETRY_DELAY_SECONDS = 2

TRAVEL_TWIN_INSTRUCTIONS = """
You are Travel Twin, a friendly travel companion for the user's trip.

How to answer:
- Answer exactly what the user asked, first. Do NOT restate the trip summary
  (from, duration, budget, route) unless the user asks for a summary.
- Be conversational and concise: normally under 150 words. Go longer only
  when the user asks for a full itinerary or plan.
- When asked to plan or give an itinerary: one section per day (Day 1, Day 2, ...),
  following the visit order, and keep each day realistic. Give long drives
  their own day instead of packing many stops around them.
- Use the trip details below for places, distances and costs. Never invent
  prices, distances or places. If something isn't in the data, say so.
- The trip details list the distance between each pair of consecutive stops.
  These are straight-line distances, and real road distance is usually longer,
  so call them approximate (say so once, briefly). Stops that are not
  consecutive are not listed; you may add up consecutive legs, but don't guess.
- All amounts are in Indian rupees, written with the ₹ symbol.
- Formatting: light markdown only - short paragraphs, bullet lists, and
  bold for key names or numbers. No large headings, no horizontal rules,
  no emojis unless the user uses them first.
- End with at most one short follow-up suggestion, and only if it is useful.
""".strip()


def _try_geocode(name: str | None):
    """(lat, lon) for a place name, or None. Cached by the geocoder after the first lookup."""
    if not name:
        return None
    try:
        lat, lon, _ = geocode_place_name(name)
        return lat, lon
    except ValueError:
        return None


def build_route_legs_text(trip: Trip) -> str:
    """Straight-line distance between each pair of consecutive stops:
    start -> places in visit order -> end location (if the trip has one)."""
    stops = []  # (label, lat, lon)

    start = _try_geocode(trip.start_location)
    if start:
        stops.append((trip.start_location, start[0], start[1]))

    for tp in sorted(trip.trip_places, key=lambda p: p.visit_order or 0):
        lat, lon = tp.resolved_latitude, tp.resolved_longitude
        if lat is not None and lon is not None:
            stops.append((tp.display_name, lat, lon))

    end = _try_geocode(trip.end_location)
    if end:
        stops.append((trip.end_location, end[0], end[1]))

    if len(stops) < 2:
        return "Not available."

    lines = []
    for (a_name, a_lat, a_lon), (b_name, b_lat, b_lon) in zip(stops, stops[1:]):
        km = haversine_km(a_lat, a_lon, b_lat, b_lon)
        lines.append(f"- {a_name} → {b_name}: {km:.1f} km")
    return "\n".join(lines)


def build_trip_context(trip: Trip) -> str:
    """
    Serializes the trip's places, budget, and route into a compact text
    block the AI can read as background. This IS the "context stuffing" -
    no function calls, just plain text handed to the model.
    """
    places_lines = []
    for tp in sorted(trip.trip_places, key=lambda p: p.visit_order or 0):
        places_lines.append(f"- {tp.display_name} ({tp.display_city or 'custom location'})")
    places_text = "\n".join(places_lines) if places_lines else "No places added yet."

    budget = trip.budget_estimate
    if budget:
        budget_text = (
            f"Hotel: ₹{budget.hotel_cost}, Food: ₹{budget.food_cost}, "
            f"Fuel: ₹{budget.fuel_cost}, Misc: ₹{budget.misc_cost}, "
            f"Total: ₹{budget.total_cost}"
        )
    else:
        budget_text = "Budget not yet calculated."

    route_text = (
        f"Total distance: {trip.total_distance_km} km "
        f"(saved {trip.distance_saved_km} km via route optimization)"
        if trip.total_distance_km else "Route not yet optimized."
    )

    return f"""
Trip details:
- From: {trip.start_location} To: {trip.end_location or 'multiple destinations'}
- Duration: {trip.num_days} days, {trip.num_travelers} traveler(s)
- Budget tier: {trip.budget_tier}, Travel mode: {trip.travel_mode}

Places in this trip (in visit order):
{places_text}

Distance between consecutive stops (straight-line, in travel order):
{build_route_legs_text(trip)}

Budget breakdown:
{budget_text}

Route:
{route_text}
""".strip()


def get_recent_chat_history(db: Session, trip_id) -> list[types.Content]:
    """Fetches the last N messages for this trip, oldest first, in the SDK's expected format."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.trip_id == trip_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(CHAT_HISTORY_LIMIT)
        .all()
    )
    messages.reverse()  # oldest first for correct conversation order

    return [
        types.Content(
            role="user" if m.role == "user" else "model",
            parts=[types.Part(text=m.content)],
        )
        for m in messages
    ]


def _ask_gemini(chat, user_message: str) -> str:
    """Sends one message. Retries a few times if Gemini is overloaded, and turns
    Gemini's errors into clean HTTP errors (a plain crash reaches the browser as a
    confusing CORS error, because crash responses carry no CORS headers)."""
    for attempt in range(GEMINI_RETRIES + 1):
        try:
            return chat.send_message(user_message).text or ""
        except genai_errors.ServerError:  # 5xx, e.g. 503 "model is currently experiencing high demand"
            if attempt < GEMINI_RETRIES:
                time.sleep(GEMINI_RETRY_DELAY_SECONDS * (attempt + 1))
                continue
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Travel Twin is busy right now. Please try again in a minute.",
            )
        except genai_errors.ClientError as exc:  # 4xx
            if getattr(exc, "code", None) == 429:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Travel Twin has hit its usage limit. Please wait a minute and try again.",
                )
            raise


def send_message(db: Session, trip: Trip, user_message: str) -> str:
    """
    Main entry point: builds context, calls Gemini, saves both messages, returns reply.
    """
    system_prompt = TRAVEL_TWIN_INSTRUCTIONS + "\n\n" + build_trip_context(trip)

    history = get_recent_chat_history(db, trip.id)

    chat = client.chats.create(
        model=MODEL_NAME,
        history=history,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )

    ai_reply = _ask_gemini(chat, user_message) or "I couldn't come up with a reply. Could you rephrase that?"

    # Save both messages to DB
    db.add(ChatMessage(trip_id=trip.id, role="user", content=user_message))
    db.add(ChatMessage(trip_id=trip.id, role="assistant", content=ai_reply))
    db.commit()

    return ai_reply