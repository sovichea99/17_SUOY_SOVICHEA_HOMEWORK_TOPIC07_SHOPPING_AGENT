
import re
from mockdata import PRODUCTS

def search_products(query: str) -> dict:
    """
    Search products by name or category (case-insensitive).
    Natural-language action words are ignored, and stock-related queries
    return only products that currently have stock.
    """
    query = query.lower().strip()
    stock_filter = any(
        phrase in query
        for phrase in ("in stock", "available", "have stock")
    )
    search_terms = [
        term for term in re.findall(r"[a-z0-9]+", query)
        if term not in {
            "a", "all", "and", "are", "check", "for", "have", "how",
            "in", "many", "me", "of", "please", "product", "products",
            "remove", "search", "show", "stock", "that", "the", "what",
            "with",
        }
    ]
    show_all = query in {"", "all", "available products", "products"}

    results = []

    for product in PRODUCTS:
        product_text = (
            f"{product['name']} {product['category']}"
        ).lower()
        if (
            (show_all or not search_terms
             or any(term in product_text for term in search_terms))
            and (not stock_filter or product["stock"] > 0)
        ):
            results.append(
                {
                    "id": product["id"],
                    "name": product["name"],
                    "category": product["category"],
                    "price": product["price"],
                    "stock": product["stock"],
                }
            )

    return {
        "success": True,
        "products": results,
    }


def check_stock(product_id: int) -> dict:
    """
    Check how many units of a product are available.
    """
    for product in PRODUCTS:
        if product["id"] == product_id:
            return {
                "success": True,
                "product_id": product_id,
                "product_name": product["name"],
                "stock": product["stock"],
            }

    return {
        "success": False,
        "error": "PRODUCT_NOT_FOUND",
        "message": "Product was not found.",
    }


def buy_product(product_id: int, quantity: int) -> dict:
    """
    Buy a product if enough stock is available.
    """
    for product in PRODUCTS:
        if product["id"] == product_id:
            if product["stock"] < quantity:
                return {
                    "success": False,
                    "error": "INSUFFICIENT_STOCK",
                    "message": (
                        f"Only {product['stock']} unit(s) "
                        f"are available."
                    ),
                }

            product["stock"] -= quantity

            return {
                "success": True,
                "message": "Purchase successful!",
                "product_id": product_id,
                "product_name": product["name"],
                "quantity": quantity,
                "remaining_stock": product["stock"],
            }

    return {
        "success": False,
        "error": "PRODUCT_NOT_FOUND",
        "message": "Product was not found.",
    }


def delete_product(product_id: int) -> dict:
    """
    Delete a product from the store. Admin-only
    """
    for product in PRODUCTS:
        if product["id"] == product_id:
            PRODUCTS.remove(product)
            return {
                "success": True,
                "message": f"{product['name']} was deleted.",
            }

    return {
        "success": False,
        "error": "PRODUCT_NOT_FOUND",
        "message": "Product was not found.",
    }
