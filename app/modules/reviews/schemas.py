from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=2, max_length=2000)


class ReviewResponseCreate(BaseModel):
    body: str = Field(min_length=2, max_length=2000)


class ReviewResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    body: str
    created_at: datetime


class ReviewOut(BaseModel):
    """Reseña con info del usuario que la escribió y, si existe, la respuesta del admin."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    user_id: int
    user_full_name: str
    rating: int
    comment: str
    created_at: datetime
    response: Optional[ReviewResponseOut] = None


class MyReviewOut(BaseModel):
    """Reseña vista desde el perfil del usuario (incluye datos del negocio reseñado)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    rating: int
    comment: str
    created_at: datetime
    business_id: int
    business_name: str
    business_city: str
    business_category: str
    response: Optional[ReviewResponseOut] = None
