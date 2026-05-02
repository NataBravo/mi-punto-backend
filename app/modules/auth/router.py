from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).register(user)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return AuthService(db).login(user)