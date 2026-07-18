# app/api/v1/travel_twin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.trip_service import get_trip
from app.services.travel_twin_service import send_message

router = APIRouter(prefix="/trips", tags=["Travel Twin"])


@router.post("/{trip_id}/chat", response_model=ChatResponse)
def chat_with_travel_twin(
    trip_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_trip(db, current_user, trip_id)
    reply = send_message(db, trip, chat_request.message)
    return ChatResponse(reply=reply)