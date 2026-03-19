from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.services.payment import create_checkout_session, handle_webhook

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CheckoutRequest(BaseModel):
    plan: str = "premium"


@router.post("/checkout")
async def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = await create_checkout_session(current_user, data.plan, db)
    return session


@router.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    result = await handle_webhook(payload, sig_header, db)
    return result


@router.get("/status")
async def payment_status(current_user: User = Depends(get_current_user)):
    return {"plan": current_user.plan, "user_id": current_user.id}
