# Ecommerce_backend_fastAPI

- This is a production-grade backend API for an e-commerce application built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. It supports user authentication, product browsing, cart management, orders, and secure JWT-based access control.

---

## Features

- JWT Authentication (Access + Refresh Tokens)
- Role-based Access (User/Admin)
- Admin Product Management (Add, Edit, Delete, Search)
- User Cart Operations (Add, Update, Remove)
- Checkout with Stock Update and Order Creation
- Order History and Order Details
- Search and Filter Products
- Global Exception Handling with JSON Responses
- Alembic Migrations
- Environment Configuration via `.env`

---

## Technologies Used

- **FastAPI**
- **SQLAlchemy + Alembic**
- **PostgreSQL**
- **Pydantic v2**
- **Passlib (for password hashing)**
- **Python-Jose (for JWT)**
- **Uvicorn** (for development server)

---

## Setup Instructions

# 1. Clone the Repository
git clone https://github.com/your-username/e_commerce_backend.git
cd e_commerce_backend

# 2. Create and Activate a Virtual Environment
python3 -m venv .venv
source .venv/bin/activate 

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Create a .env File
copy fields from env_sample

# 5. Apply Database Migrations
alembic upgrade head

# 6. Run the FastAPI Server
uvicorn app.main:app --reload

---
