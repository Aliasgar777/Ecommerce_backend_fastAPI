from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from . import schemas
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.product import utils as product_utils
from app.auth import models as auth_model
from . import models, utils
from app.core.logger import logger
from typing import List
from app.product import models as prod_model

router = APIRouter()

@router.post("/cart", response_model=schemas.CartResponse)
def add_to_cart(item : schemas.CartRequest, db : Session = Depends(get_db),
                current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    if utils.check_if_possible(item.product_id, db, item.quantity):
        product_in_cart = models.Cart(**item.model_dump(), user_id = current_user.get("id"))
        db.add(product_in_cart)
        db.commit()
        db.refresh(product_in_cart)
        return product_in_cart
    else :
        logger.error("Product not found")

@router.get("/cart", response_model=List[schemas.CartResponse])
def view_cart(db : Session = Depends(get_db),
              current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    items = db.query(models.Cart).filter(models.Cart.user_id == current_user.get("id")).all()
    return items

@router.delete("/cart/{cart_id}")
def remove_from_cart(cart_id : int ,db : Session = Depends(get_db),
              current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    item = db.query(models.Cart).filter(models.Cart.cart_id == cart_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="item in cart not found")
    
    product = db.query(prod_model.Product).filter(prod_model.Product.id == item.product_id).first()

    if product is None:
         raise HTTPException(status_code=404, detail="product in cart not found")

    product.stock = product.stock + item.quantity
    db.delete(item)
    db.commit()
    db.refresh(product)

    return {cart_id : "item deleted successfully"}

@router.put("/cart", response_model = schemas.CartResponse)
def update_cart(to_update : schemas.CartUpdate,db : Session = Depends(get_db),
              current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    item = db.query(models.Cart).filter(and_(models.Cart.cart_id == to_update.cart_id, models.Cart.user_id == current_user.get("id"))).first()

    if item is None:
        raise HTTPException(status_code=404, detail="item in cart not found")
    
    product = db.query(prod_model.Product).filter(prod_model.Product.id == item.product_id).first() 

    if product is None:
         raise HTTPException(status_code=404, detail="product in cart not found")
    
    if item.quantity > to_update.quantity :
        product.stock = product.stock + item.quantity - to_update.quantity
    elif product.stock >= to_update.quantity - item.quantity:
        product.stock = product.stock - (to_update.quantity - item.quantity)

    item.quantity = to_update.quantity

    db.commit()
    db.refresh(product)
    db.refresh(item)

    return item