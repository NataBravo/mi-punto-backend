from fastapi import APIRouter

from app.shared.cities import CITIES

router = APIRouter()


@router.get("", response_model=list[str])
def list_cities() -> list[str]:
    return CITIES
