from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.cost import monthly_rate
from app.engines.dates import days_to_renewal, is_overdue, is_renewing_soon
from app.models.subscription import Subscription
from app.schemas.subscription import MetricsRead, SubscriptionRead


def annotate(sub: Subscription, today: date | None = None) -> SubscriptionRead:
    current = today if today is not None else date.today()
    days = days_to_renewal(sub.renewal_date, current)
    return SubscriptionRead(
        id=sub.id,
        name=sub.name,
        cost=sub.cost,
        billing_cycle=sub.billing_cycle,  # type: ignore[arg-type]
        renewal_date=sub.renewal_date,
        status=sub.status,  # type: ignore[arg-type]
        monthly_rate=monthly_rate(sub.cost, sub.billing_cycle),
        days_to_renewal=days,
        renewing_soon=is_renewing_soon(days),
        overdue=is_overdue(days),
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


def list_subscriptions(db: Session) -> list[Subscription]:
    return list(db.scalars(select(Subscription).order_by(Subscription.id)).all())


def get_subscription(db: Session, subscription_id: int) -> Subscription | None:
    return db.get(Subscription, subscription_id)


def create_subscription(
    db: Session,
    *,
    name: str,
    cost: float,
    billing_cycle: str,
    renewal_date: date,
) -> Subscription:
    monthly_rate(cost, billing_cycle)
    sub = Subscription(
        name=name,
        cost=cost,
        billing_cycle=billing_cycle,
        renewal_date=renewal_date,
        status="active",
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def set_status(db: Session, sub: Subscription, status: str) -> Subscription:
    sub.status = status
    sub.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def compute_metrics(subs: list[Subscription], today: date | None = None) -> MetricsRead:
    current = today if today is not None else date.today()
    active = [s for s in subs if s.status == "active"]
    paused = [s for s in subs if s.status == "paused"]
    burn = round(sum(monthly_rate(s.cost, s.billing_cycle) for s in active), 2)
    upcoming = sum(
        1 for s in subs if is_renewing_soon(days_to_renewal(s.renewal_date, current))
    )
    return MetricsRead(
        monthly_burn_rate=burn,
        upcoming_renewals_count=upcoming,
        active_count=len(active),
        paused_count=len(paused),
    )
