from flask import Blueprint, jsonify, request
from fixtures.flask_ecommerce.app.repositories.catalog_repo import CatalogRepository

catalog_bp = Blueprint("catalog", __name__)
catalog_repo = CatalogRepository()


@catalog_bp.route("/products", methods=["GET"])
def list_products():
    category_id = request.args.get("category_id")
    products = catalog_repo.list_products(category_id=category_id)
    return jsonify({
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "price": p.price,
                "inventory": p.inventory_count,
                "sku": p.sku,
            }
            for p in products
        ]
    }), 200


@catalog_bp.route("/products/<product_id>", methods=["GET"])
def get_product(product_id: str):
    product = catalog_repo.get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "inventory": product.inventory_count,
    }), 200
