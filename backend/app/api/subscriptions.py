from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionStatusUpdate,
)
from app.services import subscriptions as svc

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: SubscriptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubscriptionRead:
    sub = svc.create_subscription(
        db,
        user_id=user.id,
        name=payload.name,
        cost=payload.cost,
        billing_cycle=payload.billing_cycle,
        renewal_date=payload.renewal_date,
    )
    return svc.annotate(sub)


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SubscriptionRead]:
    return [svc.annotate(sub) for sub in svc.list_subscriptions(db, user.id)]


@router.get("/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubscriptionRead:
    sub = svc.get_subscription(db, user.id, subscription_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return svc.annotate(sub)


@router.patch("/{subscription_id}/status", response_model=SubscriptionRead)
def patch_status(
    subscription_id: int,
    payload: SubscriptionStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubscriptionRead:
    sub = svc.get_subscription(db, user.id, subscription_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub = svc.set_status(db, sub, payload.status)
    return svc.annotate(sub)
