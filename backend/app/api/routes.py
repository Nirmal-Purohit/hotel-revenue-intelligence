from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from datetime import datetime

from app.schemas.revenue import ForecastRequest, PriceRecommendationRequest
from app.services import revenue_intelligence as intelligence

router = APIRouter()

# Email request model
class EmailNotificationRequest(BaseModel):
    message: str
    user_email: Optional[str] = "Guest User"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/forecast")
def forecast(request: ForecastRequest):
    return intelligence.forecast(request)


@router.post("/recommend-price")
def recommend_price(request: PriceRecommendationRequest):
    return intelligence.recommend_price(request)


@router.get("/dashboard")
def dashboard(
    hotel_id: str = "HRI-BLR-001", 
    room_type: Optional[str] = None, 
    horizon_days: int = Query(default=30, ge=7, le=90)
):
    """Get complete dashboard data"""
    try:
        # Convert "All room types" to None for the backend
        processed_room_type = None
        if room_type and room_type != "All room types" and room_type != "All":
            processed_room_type = room_type
        
        # Call the dashboard service
        return intelligence.dashboard(
            hotel_id=hotel_id, 
            room_type=processed_room_type, 
            horizon_days=horizon_days
        )
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/booking-pace")
def booking_pace(
    days: int = Query(default=30, ge=1, le=90), 
    hotel_id: str = "HRI-BLR-001", 
    room_type: Optional[str] = None
):
    return intelligence.booking_pace(days, hotel_id=hotel_id, room_type=room_type)


@router.get("/market-demand")
def market_demand(days: int = Query(default=30, ge=1, le=90), hotel_id: str = "HRI-BLR-001"):
    return intelligence.market_demand(days, hotel_id=hotel_id)


@router.get("/competitor-analysis")
def competitor_analysis(room_type: str = "Deluxe", hotel_id: str = "HRI-BLR-001"):
    return intelligence.competitor_analysis(room_type, hotel_id=hotel_id)


# EMAIL NOTIFICATION ENDPOINT
@router.post("/send-notification")
def send_notification(email_data: EmailNotificationRequest):
    """Send email notification when someone opens the app"""
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        email = Mail(
            from_email='nirmal.purohit1427@gmail.com',
            to_emails='nirmal.purohit1427@gmail.com',
            subject='🔔 Hotel Revenue Intelligence - New Activity',
            html_content=f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; border-radius: 5px;">
                <h2 style="color: #333;">🔔 New Activity Detected</h2>
                <p><strong>⏰ Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>👤 User:</strong> {email_data.user_email}</p>
                <p><strong>📝 Action:</strong> {email_data.message}</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">Hotel Revenue Intelligence</p>
            </div>
            """
        )
        
        response = sg.send(email)
        return {
            "success": True,
            "message": "Email sent successfully",
            "status_code": response.status_code
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }