from fastapi import FastAPI
from app.core.database import engine, Base
from app.modules.auth.router import router as auth_router
from app.modules.auth.models import Role
from app.core.database import SessionLocal


app = FastAPI()

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

def create_roles():
    db = SessionLocal()

    roles = ["OWNER", "ADMIN", "USER"]

    for role_name in roles:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(name=role_name))

    db.commit()
    db.close()

create_roles()

# Registrar rutas
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "API Mi Punto funcionando 🚀"}