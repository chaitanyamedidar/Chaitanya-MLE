from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.ml.insights import build_insights
from app.services import subscriptions as svc

router = APIRouter(tags=["insights"])


@router.get("/insights")
def get_insights(db: Session = Depends(get_db)) -> dict:
    return build_insights(svc.list_subscriptions(db))
