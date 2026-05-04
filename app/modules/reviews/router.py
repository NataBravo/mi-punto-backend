from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.modules.auth.models import User, UserRole
from app.modules.reviews import service
from app.modules.reviews.schemas import (
    ReviewCreate,
    ReviewOut,
    ReviewResponseCreate,
)

# Reseñas anidadas bajo /businesses/{business_id}/reviews
business_reviews_router = APIRouter()


@business_reviews_router.get("", response_model=list[ReviewOut])
def list_reviews_by_business(
    business_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ReviewOut]:
    return service.list_business_reviews(db, business_id, page=page, page_size=page_size)


@business_reviews_router.post(
    "", response_model=ReviewOut, status_code=status.HTTP_201_CREATED
)
def create_review(
    business_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.end_user)),
) -> ReviewOut:
    return service.create_review(db, business_id, current_user, payload)


# Acciones sobre reseñas individuales (responder).
reviews_router = APIRouter()


@reviews_router.post("/{review_id}/response", response_model=ReviewOut)
def respond_to_review(
    review_id: int,
    payload: ReviewResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.business_admin)),
) -> ReviewOut:
    return service.respond_to_review(db, review_id, current_user, payload)
