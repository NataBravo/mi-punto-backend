# Mi Punto – Backend

## 📌 Descripción del proyecto

Mi Punto es una plataforma orientada a la gestión y visualización de negocios locales. Este repositorio contiene la lógica del servidor, encargada de la gestión de datos, autenticación, reglas de negocio y exposición de servicios mediante API.

---

## 🚀 Tecnologías utilizadas

* FastAPI
* Pydantic (DTOs y validación de datos)
* SQLAlchemy (modelo de datos y ORM)
* Uvicorn (servidor ASGI)

---

## 🧠 Arquitectura

El backend está diseñado bajo una **arquitectura monolítica modular**, implementando principios de **Screaming Architecture**, donde los módulos representan funcionalidades del sistema como:

* Autenticación
* Negocios
* Reseñas

Esto permite una separación clara de responsabilidades y facilita la evolución del sistema.

---

## 📁 Estructura del proyecto

```
app/
│
├── modules/        # Módulos del sistema (auth, business, reviews)
├── core/           # Configuración global
├── main.py         # Punto de entrada de la aplicación
│
└── database/       # Configuración de base de datos

```
---


## ⚙️ Instalación y ejecución

1. Clonar el repositorio:

```
git clone <URL_DEL_REPOSITORIO>
```

2. Crear entorno virtual:

```
python -m venv venv
```

3. Activar entorno:

* Windows:

```
venv\Scripts\activate
```

* Linux/Mac:
source venv/bin/activate

4. Instalar dependencias:
pip install -r requirements.txt

5. Ejecutar servidor:
uvicorn app.main:app --reload

---

## 🧪 Estado del proyecto

En desarrollo bajo metodología Scrum, organizado por sprints y gestionado mediante Jira.

---

## 👥 Equipo de desarrollo

* Natalia Bravo
* Juan Camilo

---

## 📄 Notas

Este backend expone una API REST que será consumida por el frontend. El desarrollo se realiza de manera incremental, priorizando autenticación, gestión de negocios y funcionalidades de interacción.
