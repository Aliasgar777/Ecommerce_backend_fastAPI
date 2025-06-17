from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.core.database import get_db
from app.product import models, schemas, utils
from sqlalchemy.orm import Session
from app.auth import models as auth_model
from app.core.logger import logger

router = APIRouter()

@router.post("/admin/products", response_model=schemas.ProductResponse)
def create_product(
    product_data: schemas.ProductCreate, db: Session = Depends(get_db),
    current_user: dict = Depends(utils.require_role(auth_model.UserRole.admin))):

    new_product = models.Product(**product_data.model_dump(), created_by=current_user.get("id"))
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/admin/products", response_model=List[schemas.ProductResponse])
def get_products(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(utils.require_role(auth_model.UserRole.admin)),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1)):

    offset = (page - 1) * page_size
    return utils.get_products_by_id(db, current_user, offset, page_size)
      

@router.get("/products/search", response_model=schemas.ProductSearchResponse)
def search_products(
    keyword: str = Query(..., min_length=1, max_length=100),
    db: Session = Depends(get_db),
    current_user : dict = Depends(utils.require_role(auth_model.UserRole.user))):

    keyword = keyword.strip()

    keyword_pattern = f"%{keyword}%"
    products = db.query(models.Product).filter(
    models.Product.name.ilike(keyword_pattern) |
    models.Product.description.ilike(keyword_pattern) |
    models.Product.category.ilike(keyword_pattern)
    ).all()

    if not products:
        logger.info(f"No products found for keyword - {keyword}")
        return {
            "products": [],
            "message": "No matching products found./"
        }

    return {
        "products": products,
        "message": None 
    }


@router.get("/admin/products/{id}", response_model=schemas.ProductResponse)
def get_product(
    id: int = Path(..., ge= 1),
    db: Session = Depends(get_db),
    current_user : dict = Depends(utils.require_role(auth_model.UserRole.admin))):

    return utils.get_product_by_id(db, id, current_user)


@router.put("/admin/products/{id}", response_model=schemas.ProductResponse)
def update_product( 
    updated_product: schemas.ProductUpdate, 
    db: Session = Depends(get_db),
    id: int = Path(..., ge=1),
    current_user : dict = Depends(utils.require_role(auth_model.UserRole.admin))):

    product = utils.update_product(db, id, updated_product, current_user)
    return product


@router.delete("/admin/products/{id}")
def delete_product(
    id: int = Path(..., ge = 1), 
    db: Session = Depends(get_db),
    current_user : dict = Depends(utils.require_role(auth_model.UserRole.admin))):

    utils.delete_product(db, id, current_user)
    return {"message": "Product deleted successfully"}


@router.get("/products/{id}", response_model=schemas.ProductResponse)
def get_product(
    id: int = Path(..., ge=1), 
    db: Session = Depends(get_db),
    current_user : dict = Depends(utils.require_role(auth_model.UserRole.user))):
    
    return utils.get_product_by_id_public(db, id)


@router.get("/products", response_model=List[schemas.ProductResponse])
def list_products(
    category: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    sort_by: Optional[str] = Query(default="id", min_length=2, max_length=5),
    page: Optional[int] = Query(default=1, ge=1),
    page_size: Optional[int] = Query(default=10, ge=1),
    db: Session = Depends(get_db),
    current_user : dict = Depends(utils.require_role(auth_model.UserRole.user))
):
    valid_sort_fields = ["price", "name", "id"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
        )

    try:
        query = db.query(models.Product)

        if category is not None:
            query = query.filter(models.Product.category == category)
        if min_price is not None:
            query = query.filter(models.Product.price >= min_price)
        if max_price is not None:
            query = query.filter(models.Product.price <= max_price)

        query = query.order_by(getattr(models.Product, sort_by))

        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()

        return products

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while fetching products."
        )
