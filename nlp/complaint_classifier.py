
import re

CATEGORY_KEYWORDS = {
    "Damaged Product": ["damaged", "broken", "cracked", "shattered", "scratched", "defective"],
    "Delivery Issue": ["delivery", "delayed", "late", "shipment", "shipping", "courier", "not delivered", "tracking"],
    "Stock Availability": ["out of stock", "unavailable", "not available", "restock", "stock availability"],
    "Pricing Issue": ["price", "pricing", "expensive", "overcharged", "cost", "discount", "billing"],
    "Product Quality": ["quality", "poor quality", "low quality", "material", "performance", "faulty"]
}


def classify_complaint(text):
    text = re.sub(r'\s+', ' ', text.lower())
    category_scores = {category: sum(1 for keyword in keywords if keyword in text) for category, keywords in CATEGORY_KEYWORDS.items()}
    best_category = max(category_scores, key=category_scores.get)
    return best_category if category_scores[best_category] > 0 else "Other"
