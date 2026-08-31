from typing import List, Optional
from fixtures.flask_ecommerce.app import db
from fixtures.flask_ecommerce.app.models.schema import Category, Product


class CatalogRepository:
    """Data access layer for categories and products."""

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        return Product.query.filter_by(id=product_id).first()

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        return Product.query.filter_by(sku=sku).first()

    def list_products(self, category_id: Optional[str] = None, limit: int = 50) -> List[Product]:
        query = Product.query.filter_by(is_active=True)
        if category_id:
            query = query.filter_by(category_id=category_id)
        return query.limit(limit).all()

    def create_product(self, product: Product) -> Product:
        db.session.add(product)
        db.session.commit()
        return product

    def list_categories(self) -> List[Category]:
        return Category.query.all()
