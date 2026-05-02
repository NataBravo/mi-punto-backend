from sqlalchemy.orm import Session
from app.modules.auth import models, schemas
from app.modules.auth.security import PasswordService, TokenService
from app.modules.auth.models import Role


class AuthService:
    """Servicio para manejar la autenticación de usuarios, incluyendo registro y login."""

    def __init__(self, db: Session):
        """Inicializa el servicio con la sesión de base de datos."""
        self.db = db

    def register(self, user_data: schemas.UserCreate):
        """Registra un nuevo usuario en el sistema."""
        existing_user = self.db.query(models.User).filter(models.User.email == user_data.email).first()

        if existing_user:
            return {"error": "El usuario ya existe"}

        role = self.db.query(Role).filter(Role.name == "USER").first()

        if not role:
            return {"error": "Rol USER no existe"}

        hashed_password = PasswordService.hash_password(user_data.password)

        new_user = models.User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role_id=role.id
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return {"message": "Usuario registrado"}

    def login(self, user_data: schemas.UserLogin):
        """Inicia sesión de un usuario y genera un token de acceso."""
        user = self.db.query(models.User).filter(models.User.email == user_data.email).first()

        if not user:
            return {"error": "Usuario no encontrado"}

        if not PasswordService.verify_password(user_data.password, user.password_hash):
            return {"error": "Contraseña incorrecta"}

        token = TokenService.create_access_token({
            "sub": user.email,
            "role": user.role_id
        })

        return {"access_token": token, "token_type": "bearer"}