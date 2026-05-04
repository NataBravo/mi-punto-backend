from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.businesses.models import Business, BusinessVisit, Category
from app.modules.metrics.schemas import (
    BusinessMetricsOut,
    CategoryDistribution,
    CityDistribution,
    OwnerMetricsOut,
    RecentReviewOut,
)
from app.modules.reviews.models import Review, ReviewResponse


def _percentage(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)


def get_owner_metrics(db: Session) -> OwnerMetricsOut:
    total = db.scalar(select(func.count(Business.id))) or 0
    active = (
        db.scalar(select(func.count(Business.id)).where(Business.is_active.is_(True))) or 0
    )
    inactive = total - active
    total_reviews = db.scalar(select(func.count(Review.id))) or 0
    total_visits = db.scalar(select(func.count(BusinessVisit.id))) or 0

    cities_rows = db.execute(
        select(Business.city, func.count(Business.id))
        .group_by(Business.city)
        .order_by(func.count(Business.id).desc())
    ).all()

    categories_rows = db.execute(
        select(Category.name, func.count(Business.id))
        .join(Business, Business.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.count(Business.id).desc())
    ).all()

    cities = [
        CityDistribution(city=row[0], count=row[1], percentage=_percentage(row[1], total))
        for row in cities_rows
    ]
    categories = [
        CategoryDistribution(category=row[0], count=row[1], percentage=_percentage(row[1], total))
        for row in categories_rows
    ]

    return OwnerMetricsOut(
        total_businesses=total,
        active_businesses=active,
        inactive_businesses=inactive,
        total_reviews=total_reviews,
        total_visits=total_visits,
        cities=cities,
        categories=categories,
    )


def get_my_business_metrics(db: Session, current_user: User) -> BusinessMetricsOut:
    business = db.scalar(select(Business).where(Business.owner_id == current_user.id))
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not manage a business yet",
        )

    profile_views = (
        db.scalar(select(func.count(BusinessVisit.id)).where(BusinessVisit.business_id == business.id))
        or 0
    )
    total_reviews = (
        db.scalar(select(func.count(Review.id)).where(Review.business_id == business.id)) or 0
    )
    avg_rating = (
        db.scalar(
            select(func.coalesce(func.avg(Review.rating), 0.0)).where(
                Review.business_id == business.id
            )
        )
        or 0.0
    )
    responded = (
        db.scalar(
            select(func.count(ReviewResponse.id))
            .join(Review, Review.id == ReviewResponse.review_id)
            .where(Review.business_id == business.id)
        )
        or 0
    )
    response_rate = round((responded / total_reviews) * 100, 1) if total_reviews else 0.0
    pending_responses = total_reviews - responded

    recent_rows = db.execute(
        select(Review, User, ReviewResponse)
        .join(User, User.id == Review.user_id)
        .outerjoin(ReviewResponse, ReviewResponse.review_id == Review.id)
        .where(Review.business_id == business.id)
        .order_by(Review.created_at.desc())
        .limit(5)
    ).all()

    recent_reviews = [
        RecentReviewOut(
            id=review.id,
            user_full_name=user.full_name,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            has_response=response is not None,
        )
        for review, user, response in recent_rows
    ]

    return BusinessMetricsOut(
        business_id=business.id,
        profile_views=int(profile_views),
        total_reviews=int(total_reviews),
        average_rating=round(float(avg_rating), 2),
        response_rate=response_rate,
        pending_responses=int(pending_responses),
        recent_reviews=recent_reviews,
    )
