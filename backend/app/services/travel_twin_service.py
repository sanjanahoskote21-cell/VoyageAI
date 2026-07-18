"""
travel_twin_service.py
Travel Twin - AI trip companion chat, using context-stuffing (Option A):
fetch trip data once per request, build one prompt, call Gemini.
"""

import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import get_settings
from app.models.trip import Trip
from app.models.chat_message import ChatMessage

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.0-flash"  # fast + free-tier friendly; swap easily if needed
CHAT_HISTORY_LIMIT = 10  # only send the last N messages, keeps prompt size bounded


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

Budget breakdown:
{budget_text}

Route:
{route_text}
""".strip()


def get_recent_chat_history(db: Session, trip_id) -> list[dict]:
    """Fetches the last N messages for this trip, oldest first, in Gemini's expected format."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.trip_id == trip_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(CHAT_HISTORY_LIMIT)
        .all()
    )
    messages.reverse()  # oldest first for correct conversation order

    return [
        {"role": "user" if m.role == "user" else "model", "parts": [m.content]}
        for m in messages
    ]


def send_message(db: Session, trip: Trip, user_message: str) -> str:
    """
    Main entry point: builds context, calls Gemini, saves both messages, returns reply.
    """
    system_prompt = (
        "You are Travel Twin, a friendly AI travel companion helping the user "
        "plan and think through their trip. Use the trip details below to give "
        "specific, grounded answers - don't make up places or numbers that "
        "aren't in the context.\n\n" + build_trip_context(trip)
    )

    model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)

    history = get_recent_chat_history(db, trip.id)
    chat = model.start_chat(history=history)

    response = chat.send_message(user_message)
    ai_reply = response.text

    # Save both messages to DB
    db.add(ChatMessage(trip_id=trip.id, role="user", content=user_message))
    db.add(ChatMessage(trip_id=trip.id, role="assistant", content=ai_reply))
    db.commit()

    return ai_reply