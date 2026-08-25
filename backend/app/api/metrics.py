from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.subscription import MetricsRead
from app.services import subscriptions as svc

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=MetricsRead)
def get_metrics(db: Session = Depends(get_db)) -> MetricsRead:
    return svc.compute_metrics(svc.list_subscriptions(db))
