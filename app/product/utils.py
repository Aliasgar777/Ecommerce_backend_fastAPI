from fastapi import Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.auth import utils as auth_utils
from . import models, schemas
from app.auth.models import UserRole 
from app.core.logger import logger

def require_role(required_role: UserRole):
    def role_checker(token_data: dict = Depends(auth_utils.get_current_user)):
        if token_data.get("role") != required_role:
            logger.warning(f"user with id {token_data.get("id")} does not have enough permission")
            raise HTTPException(
                status_code=403, 
                detail="Not enough permissions")
        return token_data
    return role_checker

def get_all_products(db: Session):
    try:
        products = db.query(models.Product).all()
        return products
    except Exception :
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch products"
        )
    
def get_products_by_id(db: Session, current_user: dict):
    
    id = current_user.get("id")
    products = db.query(models.Product).filter(models.Product.created_by == id).all()
    return products
    
def get_product_by_id(db: Session, id: int, current_user: dict):

    user_id = current_user.get("id")
    product = db.query(models.Product).filter(
        and_(models.Product.id == id,models.Product.created_by == user_id)).first()
    
    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Product not found")
    return product

def update_product(db : Session, id: int, updated_product: schemas.ProductUpdate, current_user : dict):

    user_id = current_user.get("id")
    product = db.query(models.Product).filter(and_(models.Product.id == id, models.Product.created_by ==user_id)).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {id} not found"
        )

    for field, value in updated_product.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product
    
def delete_product(db:Session, id:int, current_user:dict):

    user_id = current_user.get("id")
    product = db.query(models.Product).filter(and_(models.Product.id == id, models.Product.created_by ==user_id)).first()

    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Product not found")
    
    db.delete(product)
    db.commit()

def get_product_by_id_public(db: Session, id:int):

    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Product not found"
            )
    return product