from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.modules.auth.models import User, UserRole
from app.modules.metrics import service
from app.modules.metrics.schemas import BusinessMetricsOut, OwnerMetricsOut

router = APIRouter()


@router.get("/owner", response_model=OwnerMetricsOut)
def owner_metrics(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.owner)),
) -> OwnerMetricsOut:
    return service.get_owner_metrics(db)


@router.get("/business/me", response_model=BusinessMetricsOut)
def my_business_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.business_admin)),
) -> BusinessMetricsOut:
    return service.get_my_business_metrics(db, current_user)
