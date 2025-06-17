from fastapi import APIRouter, Depends, HTTPException, Path
from . import schemas
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.product.utils import require_role
from app.auth.models import UserRole
from . import models
from app.core.logger import logger
from typing import List
from app.product import models as prod_model

router = APIRouter()

@router.post("/cart")
def add_to_cart(
    cart_item : schemas.CartRequest, db : Session = Depends(get_db),
    current_user: dict = Depends(require_role(UserRole.user))
    ):
    logger.info(f"adding products to cart with id {cart_item.product_id} to user {current_user.get("id")}")

    product = db.query(prod_model.Product).filter(prod_model.Product.id == cart_item.product_id).first()
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product is not available")
    
    if product.stock < cart_item.quantity:
        raise HTTPException(
            status_code=400,
            detail= f"Insufficient stock, prod_id - {cart_item.product_id}")
    
    exist_in_cart = db.query(models.Cart).filter(
        models.Cart.product_id == cart_item.product_id,
        models.Cart.user_id == current_user.get("id")
        ).first()

    if exist_in_cart is None :
        product_in_cart = models.Cart(
            **cart_item.model_dump(),
            user_id = current_user.get("id")
            )
        db.add(product_in_cart)
    else :
        exist_in_cart.quantity += cart_item.quantity
    
    db.commit()
    logger.info(f"Item with prod_id - {cart_item.product_id} ,added to Cart")
    return f"Item with prod_id - {cart_item.product_id} ,added to Cart"
         
@router.get("/cart", response_model=List[schemas.CartResponse])
def view_cart(
    db : Session = Depends(get_db),
    current_user: dict = Depends(require_role(UserRole.user))):

    logger.info(f"veiwing carts items for user with email - {current_user.get("sub")}")
    items = db.query(models.Cart).filter(models.Cart.user_id == current_user.get("id")).all()
    return items

@router.delete("/cart/{product_id}")
def remove_from_cart(
    product_id : int = Path(..., ge=1),
    db : Session = Depends(get_db),
    current_user: dict = Depends(require_role(UserRole.user))
    ):
    logger.info(f"Removing product with id - {product_id} from cart")

    cart_item = db.query(models.Cart).filter(
        models.Cart.product_id == product_id , 
        models.Cart.user_id == current_user.get("id")).first()

    if cart_item is None:
        logger.warning(f"cart item with product id - {product_id} not found in cart")
        raise HTTPException(
            status_code=404, 
            detail="item in cart not found")
        
    db.delete(cart_item)
    db.commit()

    logger.info(f"cart item with product id - {product_id} deleted successfully")
    return f"cart item with product id - {product_id} deleted successfully"

@router.put("/cart/{product_id}")
def update_cart( 
    prod_to_update : schemas.CartUpdate ,
    product_id : int = Path(..., ge=1),
    db : Session = Depends(get_db),
    current_user: dict = Depends(require_role(UserRole.user))
    ):
    logger.info(f"updating the product with id-{product_id} quantity in cart")
    
    cart_item = db.query(models.Cart).filter(
        models.Cart.product_id == product_id ,
        models.Cart.user_id == current_user.get("id")).first()

    if cart_item is None:
        logger.warning(f"product id-{product_id} : not found in cart")
        raise HTTPException(status_code=404, detail="item in cart not found")
    
    product = db.query(prod_model.Product).filter(prod_model.Product.id == cart_item.product_id).first() 

    if product is None:
        logger.warning(f"product id-{product_id} : does not exist in db")
        raise HTTPException(status_code=404, detail=f"product id-{product_id} : does not exist in db")
    
    if prod_to_update.quantity <= 0:
        db.delete(cart_item)
    elif product.stock >= prod_to_update.quantity:
        cart_item.quantity = prod_to_update.quantity
        db.commit()
        db.refresh(product)
        db.refresh(cart_item)
        return f"Product id-{product_id} : quantity updated successfully"
    else :
        return f"Not enough stock available of product id-{product_id}"