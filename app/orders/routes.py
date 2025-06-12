from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.product import utils as prod_utils
from app.cart.models import Cart
from app.product.models import Product
from app.orders.models import Orders, OrderItem
from app.auth.models import UserRole
from . import schemas

router = APIRouter()


@router.post("/orders/checkout", response_model=schemas.OrderResponse)
def checkout(
    current_user: dict = Depends(prod_utils.require_role(UserRole.user)),
    db: Session = Depends(get_db)):

    current_user_id = current_user.get("id")

    cart_items = db.query(Cart).filter(Cart.user_id == current_user_id).all()
    if not cart_items:
        raise HTTPException(
            status_code=400, 
            detail="Cart is empty.")

    total = 0
    order = Orders(user_id=current_user_id, total_amount=0, status="paid")
    db.add(order)
    db.flush()  

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for {product.name}")

        product.stock -= item.quantity
        subtotal = product.price * item.quantity
        total += subtotal

        order_item = OrderItem(
            order_id=order.order_id,
            product_id=product.id,
            name=product.name,      
            price=product.price,    
            quantity=item.quantity,
            subtotal=subtotal
        )
        db.add(order_item)

    order.total_amount = total
    db.query(Cart).filter(Cart.user_id == current_user_id).delete()
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=List[schemas.OrderHistoryItem])
def order_history(
    current_user: dict = Depends(prod_utils.require_role(UserRole.user)),
    db: Session = Depends(get_db)):

    orders = db.query(Orders).filter(Orders.user_id == current_user.get("id")).all()
    return orders


@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def order_details(
    order_id: int, 
    current_user : dict = Depends(prod_utils.require_role(UserRole.user)),
    db: Session = Depends(get_db)):
    
    order = db.query(Orders).filter(
        Orders.order_id == order_id,
        Orders.user_id == current_user.get("id")
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order