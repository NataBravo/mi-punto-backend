from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_optional_current_user, require_role
from app.modules.auth.models import User, UserRole
from app.modules.businesses import service
from app.modules.businesses.schemas import (
    BusinessCreate,
    BusinessDetail,
    BusinessLocationUpdate,
    BusinessOwnerRow,
    BusinessUpdate,
    MyBusinessOut,
    PublicBusinessDetail,
    PublicBusinessSummary,
    ToggleResult,
)

router = APIRouter()


# ----- Público: catálogo y mapa -----

@router.get("", response_model=list[PublicBusinessSummary])
def list_public_businesses(
    city: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None, description="Search by name"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PublicBusinessSummary]:
    return service.list_public_businesses(
        db, city=city, category_id=category_id, q=q, page=page, page_size=page_size
    )


@router.get("/nearby", response_model=list[PublicBusinessSummary])
def list_nearby_businesses(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=5.0, gt=0, le=200),
    db: Session = Depends(get_db),
) -> list[PublicBusinessSummary]:
    return service.list_nearby_businesses(db, lat=lat, lng=lng, radius_km=radius_km)


# ----- Owner global -----

@router.get("/admin", response_model=list[BusinessOwnerRow])
def list_businesses_for_owner(
    q: Optional[str] = Query(default=None, description="Search by name"),
    status_filter: Optional[str] = Query(
        default=None, alias="status", pattern="^(active|inactive)$"
    ),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.owner)),
) -> list[BusinessOwnerRow]:
    return service.list_businesses_for_owner(db, q=q, status_filter=status_filter)


# ----- Admin de negocio (su propio negocio) -----

@router.get("/me", response_model=Optional[MyBusinessOut])
def get_my_business(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.business_admin)),
) -> MyBusinessOut | None:
    return service.get_my_business_view(db, current_user)


@router.post("/me", response_model=MyBusinessOut, status_code=status.HTTP_201_CREATED)
def create_my_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.business_admin)),
) -> MyBusinessOut:
    return service.create_my_business(db, current_user, payload)


@router.put("/me", response_model=MyBusinessOut)
def update_my_business(
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.business_admin)),
) -> MyBusinessOut:
    return service.update_my_business(db, current_user, payload)


@router.put("/me/location", response_model=MyBusinessOut)
def update_my_business_location(
    payload: BusinessLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.business_admin)),
) -> MyBusinessOut:
    return service.update_my_business_location(db, current_user, payload)


# ----- Detalle global por owner -----

@router.get("/{business_id}/admin", response_model=BusinessDetail)
def get_business_for_owner(
    business_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.owner)),
) -> BusinessDetail:
    return service.get_business_for_owner(db, business_id)


@router.patch("/{business_id}/toggle", response_model=ToggleResult)
def toggle_business(
    business_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.owner)),
) -> ToggleResult:
    business = service.toggle_business(db, business_id)
    return ToggleResult(id=business.id, is_active=business.is_active)


# ----- Detalle público (registra visita) -----

@router.get("/{business_id}", response_model=PublicBusinessDetail)
def get_public_business_detail(
    business_id: int,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_current_user),
) -> PublicBusinessDetail:
    viewer_id = viewer.id if viewer else None
    return service.get_public_business_detail(db, business_id, viewer_id=viewer_id)
