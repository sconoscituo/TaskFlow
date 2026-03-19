from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, PlanType
from app.config import config


async def create_checkout_session(user: User, plan: str, db: AsyncSession) -> dict:
    """Stripe 결제 세션 생성 (stub)"""
    if not config.STRIPE_SECRET_KEY:
        return {
            "message": "Stripe not configured",
            "plan": plan,
            "user_id": user.id,
            "checkout_url": None
        }

    try:
        import stripe
        stripe.api_key = config.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": config.PREMIUM_PRICE_ID, "quantity": 1}],
            mode="subscription",
            success_url="https://taskflow.app/success",
            cancel_url="https://taskflow.app/cancel",
            metadata={"user_id": str(user.id), "plan": plan},
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        return {"error": str(e)}


async def handle_webhook(payload: bytes, sig_header: str, db: AsyncSession) -> dict:
    """Stripe 웹훅 처리"""
    if not config.STRIPE_SECRET_KEY:
        return {"message": "Stripe not configured"}

    try:
        import stripe
        stripe.api_key = config.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(payload, sig_header, config.STRIPE_WEBHOOK_SECRET)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = int(session["metadata"]["user_id"])
            plan = session["metadata"]["plan"]

            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.plan = PlanType.premium
                payment = Payment(
                    user_id=user_id,
                    stripe_payment_intent_id=session.get("payment_intent"),
                    amount=session.get("amount_total", 0) / 100,
                    status=PaymentStatus.succeeded,
                    plan=plan,
                )
                db.add(payment)
                await db.commit()

        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
