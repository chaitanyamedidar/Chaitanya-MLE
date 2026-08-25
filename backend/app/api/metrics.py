from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.subscription import MetricsRead
from app.services import subscriptions as svc

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=MetricsRead)
def get_metrics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetricsRead:
    return svc.compute_metrics(svc.list_subscriptions(db, user.id))
