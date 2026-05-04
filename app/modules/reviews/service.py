from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.businesses.models import Business, Category
from app.modules.reviews.models import Review, ReviewResponse
from app.modules.reviews.schemas import (
    MyReviewOut,
    ReviewCreate,
    ReviewOut,
    ReviewResponseCreate,
    ReviewResponseOut,
)


def _to_review_out(review: Review, user: User, response: ReviewResponse | None) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        business_id=review.business_id,
        user_id=review.user_id,
        user_full_name=user.full_name,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        response=ReviewResponseOut.model_validate(response) if response else None,
    )


def list_business_reviews(
    db: Session, business_id: int, *, page: int = 1, page_size: int = 20
) -> list[ReviewOut]:
    business = db.get(Business, business_id)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Business not found")

    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    rows = db.execute(
        select(Review, User, ReviewResponse)
        .join(User, User.id == Review.user_id)
        .outerjoin(ReviewResponse, ReviewResponse.review_id == Review.id)
        .where(Review.business_id == business_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return [_to_review_out(r, u, resp) for r, u, resp in rows]


def create_review(
    db: Session, business_id: int, current_user: User, payload: ReviewCreate
) -> ReviewOut:
    business = db.get(Business, business_id)
    if business is None or not business.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Business not found")
    if business.owner_id == current_user.id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "You cannot review your own business",
        )

    existing = db.scalar(
        select(Review).where(
            Review.business_id == business_id, Review.user_id == current_user.id
        )
    )
    if existing is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "You already reviewed this business",
        )

    review = Review(
        business_id=business_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _to_review_out(review, current_user, None)


def respond_to_review(
    db: Session, review_id: int, current_user: User, payload: ReviewResponseCreate
) -> ReviewOut:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    business = db.get(Business, review.business_id)
    if business is None or business.owner_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You can only respond to reviews on your own business",
        )

    existing = db.scalar(select(ReviewResponse).where(ReviewResponse.review_id == review_id))
    if existing is not None:
        existing.body = payload.body
        response = existing
    else:
        response = ReviewResponse(review_id=review_id, body=payload.body)
        db.add(response)

    db.commit()
    db.refresh(response)

    review_user = db.get(User, review.user_id)
    return _to_review_out(review, review_user, response)


def list_my_reviews(db: Session, current_user: User) -> list[MyReviewOut]:
    rows = db.execute(
        select(Review, Business, Category, ReviewResponse)
        .join(Business, Business.id == Review.business_id)
        .join(Category, Category.id == Business.category_id)
        .outerjoin(ReviewResponse, ReviewResponse.review_id == Review.id)
        .where(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
    ).all()

    out: list[MyReviewOut] = []
    for review, business, category, response in rows:
        out.append(
            MyReviewOut(
                id=review.id,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
                business_id=business.id,
                business_name=business.name,
                business_city=business.city,
                business_category=category.name,
                response=ReviewResponseOut.model_validate(response) if response else None,
            )
        )
    return out
