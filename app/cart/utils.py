from fastapi import Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from . import models
from app.product import models as prod_models


def check_if_possible(product_id : int, db : Session, item_quantity : int):
    product = db.query(prod_models.Product).filter(prod_models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product is not available")
    if product.stock < item_quantity:
        return False
    
    db.commit()
    db.refresh(product)
    return True


