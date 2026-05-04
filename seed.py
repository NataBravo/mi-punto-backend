"""Seed inicial: owner, admins de negocio, usuarios finales, categorías y negocios demo.

Idempotente: si los emails ya existen, no duplica.
Uso: `python seed.py` con el venv activado y la migración aplicada.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.auth.models import User, UserRole
from app.modules.businesses.models import Business, Category
from app.modules.reviews.models import Review

CATEGORIES = [
    ("Cafetería", "cafeteria"),
    ("Restaurante", "restaurante"),
    ("Librería", "libreria"),
    ("Gimnasio", "gimnasio"),
    ("Tienda", "tienda"),
    ("Supermercado", "supermercado"),
    ("Farmacia", "farmacia"),
    ("Panadería", "panaderia"),
]

USERS = [
    ("owner@demo.com", "owner1234", "Camila Restrepo", UserRole.owner),
    ("admin1@demo.com", "admin1234", "Carlos Mejía", UserRole.business_admin),
    ("admin2@demo.com", "admin1234", "Daniela Pérez", UserRole.business_admin),
    ("admin3@demo.com", "admin1234", "Felipe López", UserRole.business_admin),
    ("admin4@demo.com", "admin1234", "Laura Gómez", UserRole.business_admin),
    ("admin5@demo.com", "admin1234", "Andrés Ruiz", UserRole.business_admin),
    ("user1@demo.com", "user1234", "María González", UserRole.end_user),
    ("user2@demo.com", "user1234", "Juan Torres", UserRole.end_user),
]

BUSINESSES = [
    {
        "admin_email": "admin1@demo.com",
        "name": "Café Aroma",
        "description": "Cafetería con repostería artesanal y café de origen.",
        "category_slug": "cafeteria",
        "city": "Bogotá",
        "address": "Calle 72 #10-34",
        "phone": "+57 320 123 4567",
        "email": "contacto@cafearoma.com",
        "hours": "Lun-Sáb 7:00-20:00",
        "lat": 4.6533,
        "lng": -74.0836,
        "is_active": True,
    },
    {
        "admin_email": "admin2@demo.com",
        "name": "Restaurante El Sabor",
        "description": "Cocina colombiana contemporánea en un ambiente cálido.",
        "category_slug": "restaurante",
        "city": "Bogotá",
        "address": "Carrera 15 #85-23",
        "phone": "+57 311 234 5678",
        "email": "reservas@elsabor.co",
        "hours": "Mar-Dom 12:00-22:00",
        "lat": 4.6697,
        "lng": -74.0596,
        "is_active": True,
    },
    {
        "admin_email": "admin3@demo.com",
        "name": "Librería Papiros",
        "description": "Más de 20.000 títulos en literatura, filosofía y arte.",
        "category_slug": "libreria",
        "city": "Medellín",
        "address": "Calle 10 #43E-66",
        "phone": "+57 304 345 6789",
        "email": "hola@papiros.co",
        "hours": "Lun-Sáb 9:00-19:00",
        "lat": 6.2087,
        "lng": -75.5712,
        "is_active": True,
    },
    {
        "admin_email": "admin4@demo.com",
        "name": "Gimnasio FitZone",
        "description": "Entrenamiento funcional, clases grupales y nutrición.",
        "category_slug": "gimnasio",
        "city": "Cali",
        "address": "Av. Roosevelt #34-12",
        "phone": "+57 318 456 7890",
        "email": "info@fitzone.co",
        "hours": "Lun-Sáb 5:00-23:00",
        "lat": 3.4372,
        "lng": -76.5225,
        "is_active": True,
    },
    {
        "admin_email": "admin5@demo.com",
        "name": "Panadería La Esquina",
        "description": "Pan recién horneado, pasteles y desayunos.",
        "category_slug": "panaderia",
        "city": "Bogotá",
        "address": "Calle 53 #13-25",
        "phone": "+57 322 567 8901",
        "email": "ventas@laesquina.co",
        "hours": "Lun-Dom 6:00-21:00",
        "lat": 4.6481,
        "lng": -74.0668,
        "is_active": False,  # demo de negocio desactivado
    },
]

REVIEWS = [
    ("user1@demo.com", "Café Aroma", 5, "Excelente café y postres deliciosos. ¡100% recomendado!"),
    ("user2@demo.com", "Café Aroma", 4, "Buen lugar para trabajar, wifi rápido."),
    ("user1@demo.com", "Restaurante El Sabor", 5, "Las arepas rellenas son espectaculares."),
    ("user2@demo.com", "Librería Papiros", 5, "Variedad increíble y atención muy amable."),
    ("user1@demo.com", "Gimnasio FitZone", 4, "Entrenadores capacitados, equipos modernos."),
    ("user2@demo.com", "Gimnasio FitZone", 3, "Bueno pero a veces se llena demasiado."),
]


def upsert_user(db: Session, email: str, password: str, full_name: str, role: UserRole) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
        )
        db.add(user)
        db.flush()
    return user


def upsert_category(db: Session, name: str, slug: str) -> Category:
    cat = db.scalar(select(Category).where(Category.slug == slug))
    if cat is None:
        cat = Category(name=name, slug=slug)
        db.add(cat)
        db.flush()
    return cat


def upsert_business(db: Session, data: dict, admins: dict[str, User], cats: dict[str, Category]) -> Business:
    business = db.scalar(select(Business).where(Business.name == data["name"]))
    if business is not None:
        return business

    admin = admins[data["admin_email"]]
    cat = cats[data["category_slug"]]
    location_wkt = f"SRID=4326;POINT({data['lng']} {data['lat']})"

    business = Business(
        owner_id=admin.id,
        name=data["name"],
        description=data["description"],
        category_id=cat.id,
        city=data["city"],
        address=data["address"],
        phone=data["phone"],
        email=data["email"],
        hours=data["hours"],
        location=location_wkt,
        is_active=data["is_active"],
    )
    db.add(business)
    db.flush()
    return business


def upsert_review(
    db: Session,
    user_email: str,
    business_name: str,
    rating: int,
    comment: str,
    users: dict[str, User],
    businesses: dict[str, Business],
) -> None:
    user = users[user_email]
    business = businesses[business_name]
    existing = db.scalar(
        select(Review).where(
            Review.business_id == business.id,
            Review.user_id == user.id,
        )
    )
    if existing is not None:
        return
    db.add(Review(business_id=business.id, user_id=user.id, rating=rating, comment=comment))


def seed() -> None:
    db = SessionLocal()
    try:
        cats = {slug: upsert_category(db, name, slug) for name, slug in CATEGORIES}
        users = {
            email: upsert_user(db, email, pwd, name, role)
            for email, pwd, name, role in USERS
        }
        admins = {email: u for email, u in users.items() if u.role == UserRole.business_admin}

        businesses = {}
        for data in BUSINESSES:
            b = upsert_business(db, data, admins, cats)
            businesses[b.name] = b

        for user_email, biz_name, rating, comment in REVIEWS:
            upsert_review(db, user_email, biz_name, rating, comment, users, businesses)

        db.commit()
        print("Seed listo:")
        print(f"  - {len(cats)} categorías")
        print(f"  - {len(users)} usuarios")
        print(f"  - {len(businesses)} negocios")
        print(f"  - {len(REVIEWS)} reseñas")
        print()
        print("Credenciales demo:")
        print("  Owner       → owner@demo.com / owner1234")
        print("  Admin neg.  → admin1@demo.com / admin1234")
        print("  Usuario     → user1@demo.com / user1234")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
