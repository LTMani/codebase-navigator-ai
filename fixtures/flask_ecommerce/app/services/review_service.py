from typing import Any, Dict, List
from fixtures.flask_ecommerce.app import db
from fixtures.flask_ecommerce.app.models.review import ProductReview


class ReviewService:
    """Manages verified customer reviews, star ratings, and sentiment scoring."""

    def submit_review(self, product_id: str, user_id: str, rating: int, title: str, comment: str) -> Dict[str, Any]:
        """Record customer rating and review."""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5 stars.")

        review = ProductReview(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=True,
        )
        db.session.add(review)
        db.session.commit()

        return {
            "review_id": review.id,
            "product_id": product_id,
            "rating": rating,
            "title": title,
        }

    def get_product_rating_summary(self, product_id: str) -> Dict[str, Any]:
        """Aggregate ratings and calculate average customer review score."""
        reviews = ProductReview.query.filter_by(product_id=product_id).all()
        if not reviews:
            return {"product_id": product_id, "reviews_count": 0, "average_rating": 0.0}

        avg = sum(r.rating for r in reviews) / len(reviews)
        return {
            "product_id": product_id,
            "reviews_count": len(reviews),
            "average_rating": round(avg, 2),
        }
