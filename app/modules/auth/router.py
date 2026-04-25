from fastapi import APIRouter

router = APIRouter()

@router.get("/auth")
def test_auth():
    return {"message": "Auth funcionando"}