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

@router.post("/cart")
def add_to_cart(item : schemas.CartRequest, db : Session = Depends(get_db),
                current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    
    if utils.check_if_possible(item.product_id, db, item.quantity):
        prev_item = db.query(models.Cart).filter(models.Cart.product_id == item.product_id).first()

        if prev_item is None :
            product_in_cart = models.Cart(**item.model_dump(), user_id = current_user.get("id"))
            db.add(product_in_cart)
        else :
            prev_item.quantity = prev_item.quantity + item.quantity
        
        db.commit()
        return "Item added to Cart"
        
    else :
        return "Product not found"  

@router.get("/cart", response_model=List[schemas.CartResponse])
def view_cart(db : Session = Depends(get_db),
              current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    items = db.query(models.Cart).filter(models.Cart.user_id == current_user.get("id")).all()
    return items

@router.delete("/cart/{product_id}")
def remove_from_cart(product_id : int ,db : Session = Depends(get_db),
              current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    item = db.query(models.Cart).filter(and_(models.Cart.product_id == product_id , 
                                            models.Cart.user_id == current_user.get("id"))).first()

    if item is None:
        raise HTTPException(status_code=404, detail="item in cart not found")
    
    product = db.query(prod_model.Product).filter(prod_model.Product.id == item.product_id).first()

    if product is None:
         raise HTTPException(status_code=404, detail="product in cart not found")
        
    db.delete(item)
    db.commit()
    db.refresh(product)

    return {product_id : "item deleted successfully"}

@router.put("/cart/{product_id}")
def update_cart(product_id : int, to_update : schemas.CartUpdate ,db : Session = Depends(get_db),
              current_user: dict = Depends(product_utils.require_role(auth_model.UserRole.user))):
    
    item = db.query(models.Cart).filter(and_(models.Cart.product_id == product_id ,
                                            models.Cart.user_id == current_user.get("id"))).first()

    if item is None:
        raise HTTPException(status_code=404, detail="item in cart not found")
    
    product = db.query(prod_model.Product).filter(prod_model.Product.id == item.product_id).first() 

    if product is None:
         raise HTTPException(status_code=404, detail="product in cart not found")
    
    if to_update.quantity <= 0:
        db.delete(item)
    elif product.stock >= to_update.quantity:
        item.quantity = to_update.quantity
        db.commit()
        db.refresh(product)
        db.refresh(item)
        return "Products's quantity updated successfully"
    else :
        return "Not enough stock available"