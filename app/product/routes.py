from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.product import models, schemas, utils
from sqlalchemy.orm import Session
from app.auth.schemas import Token
from app.auth import models as auth_model
from app.core.logger import logger

router = APIRouter()

@router.post("/admin/products", response_model=schemas.ProductResponse)
def create_product( product_data: schemas.ProductCreate, db: Session = Depends(get_db),
    current_user: dict = Depends(utils.require_role(auth_model.UserRole.admin))):

    new_product = models.Product(**product_data.model_dump(), created_by=current_user.get("id"))
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/admin/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db), 
                current_user: dict = Depends(utils.require_role(auth_model.UserRole.admin))):
    if current_user is None:
        raise HTTPException(status_code=404, detail="Token Expired")
    return utils.get_products_by_id(db, current_user)


@router.get("/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db), 
                current_user: dict = Depends(utils.require_role(auth_model.UserRole.user))):
    if current_user is None:
        raise HTTPException(status_code=404, detail="Token Expired")
    return utils.get_all_products(db)
    

@router.get("/admin/products/{id}", response_model=schemas.ProductResponse)
def get_product(id: int, db: Session = Depends(get_db),
                current_user : dict = Depends(utils.require_role(auth_model.UserRole.admin))):
    return utils.get_product_by_id(db, id, current_user)


@router.put("/admin/products/{id}", response_model=schemas.ProductResponse)
def update_product(id: int, updated_product: schemas.ProductUpdate, db: Session = Depends(get_db),
                   current_user : dict = Depends(utils.require_role(auth_model.UserRole.admin))):
    product = utils.update_product(db, id, updated_product, current_user)
    return product


@router.delete("/admin/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db),
                   current_user : dict = Depends(utils.require_role(auth_model.UserRole.admin))):
    utils.delete_product(db, id, current_user)
    return {"message": "Product deleted successfully"}


@router.get("/products/{id}", response_model=schemas.ProductResponse)
def get_product(id: int, db: Session = Depends(get_db),
                current_user : dict = Depends(utils.require_role(auth_model.UserRole.user))):
    return utils.get_product_by_id_public(db, id)

