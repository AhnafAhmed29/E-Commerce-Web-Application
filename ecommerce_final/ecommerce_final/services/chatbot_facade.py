"""
Chatbot Facade — orchestrates rule-based chatbot responses.

Architecture:
  ChatbotFacade (Facade)
      ├── ProductSearchStrategy   – searches the product/category DB
      ├── ServiceInfoStrategy     – answers policy/store questions
      └── NavigationStrategy      – returns quick-nav links

All strategies are pure read-only; they never modify cart, orders, or auth.
"""
from __future__ import annotations
import re
from typing import Optional

from services.site_info import SITE_INFO, GREETING_RESPONSES, FALLBACK_RESPONSE


# ──────────────────────────────────────────────────────────────────────────────
# Strategy base
# ──────────────────────────────────────────────────────────────────────────────
class BaseChatStrategy:
    def can_handle(self, message: str) -> bool:
        raise NotImplementedError

    def handle(self, message: str) -> dict:
        raise NotImplementedError


# ──────────────────────────────────────────────────────────────────────────────
# Strategy 1: Service / Policy information
# ──────────────────────────────────────────────────────────────────────────────
class ServiceInfoStrategy(BaseChatStrategy):
    def can_handle(self, message: str) -> bool:
        msg = message.lower()
        for topic_data in SITE_INFO.values():
            if any(kw in msg for kw in topic_data["keywords"]):
                return True
        return False

    def handle(self, message: str) -> dict:
        msg = message.lower()
        best_topic = None
        best_count = 0
        for topic_data in SITE_INFO.values():
            hits = sum(1 for kw in topic_data["keywords"] if kw in msg)
            if hits > best_count:
                best_count = hits
                best_topic = topic_data
        if best_topic:
            return {
                "type": "info",
                "text": best_topic["answer"],
                "links": [],
                "products": [],
            }
        return _fallback()


# ──────────────────────────────────────────────────────────────────────────────
# Strategy 2: Product / Category search
# ──────────────────────────────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "keyboard":  ["keyboard", "keyboards", "mechanical", "typing", "keys", "keeb"],
    "mouse":     ["mouse", "mice", "gaming mouse", "wireless mouse"],
    "monitor":   ["monitor", "monitors", "display", "screen", "4k", "144hz", "165hz", "180hz"],
    "headset":   ["headset", "headphone", "earphone", "audio", "hearing"],
    "gamepad":   ["gamepad", "controller", "joystick", "pad"],
    "mousepad":  ["mousepad", "mouse pad", "desk mat", "mat"],
    "microphone":["microphone", "mic", "streaming mic"],
}

PRICE_PATTERN = re.compile(
    r"under\s*(\d[\d,]*)|below\s*(\d[\d,]*)|less\s*than\s*(\d[\d,]*)|budget\s*(\d[\d,]*)",
    re.IGNORECASE,
)


class ProductSearchStrategy(BaseChatStrategy):
    TRIGGER_WORDS = [
        "show", "find", "search", "looking for", "want", "need", "buy",
        "best", "cheap", "price", "product", "get me", "any", "have",
        "suggest", "recommend", "take me", "go to", "see",
    ]

    def can_handle(self, message: str) -> bool:
        msg = message.lower()
        has_trigger = any(tw in msg for tw in self.TRIGGER_WORDS)
        has_category = any(kw in msg for kws in CATEGORY_KEYWORDS.values() for kw in kws)
        return has_trigger or has_category

    def handle(self, message: str) -> dict:
        from models.product import Product, Category

        msg = message.lower()

        # --- Determine which category slug to search ---
        matched_slug: Optional[str] = None
        for slug, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in msg for kw in keywords):
                matched_slug = slug
                break

        # --- Optional price ceiling ---
        price_ceiling: Optional[float] = None
        m = PRICE_PATTERN.search(msg)
        if m:
            raw = next(g for g in m.groups() if g is not None)
            price_ceiling = float(raw.replace(",", ""))

        # --- Build query ---
        if matched_slug:
            cat = Category.query.filter(
                Category.slug.ilike(f"%{matched_slug}%")
            ).first()
            if cat:
                q = Product.query.filter_by(category_id=cat.id, is_active=True)
            else:
                q = Product.query.filter(
                    Product.name.ilike(f"%{matched_slug}%"),
                    Product.is_active == True,
                )
        else:
            # Generic product search from the raw message
            words = [w for w in msg.split() if len(w) > 3
                     and w not in self.TRIGGER_WORDS]
            if words:
                term = f"%{words[0]}%"
                q = Product.query.filter(
                    Product.name.ilike(term),
                    Product.is_active == True,
                )
            else:
                return _fallback()

        if price_ceiling:
            q = q.filter(Product.price <= price_ceiling)

        products = q.order_by(Product.price.asc()).limit(4).all()

        # --- Build category nav link ---
        links = []
        if matched_slug:
            links.append({
                "label": f"Browse all {matched_slug.replace('-', ' ').title()}",
                "url":   f"/category/{matched_slug}",
            })

        if not products:
            return {
                "type": "products",
                "text": (
                    f"😕 I couldn't find any products matching your query"
                    f"{' under ৳' + str(int(price_ceiling)) if price_ceiling else ''}. "
                    "Try browsing a category below!"
                ),
                "links": links,
                "products": [],
            }

        product_list = []
        for p in products:
            product_list.append({
                "name":  p.name,
                "price": f"৳{p.price:,.2f}",
                "url":   f"/product/{p.slug}",
                "image": p.main_image or "",
                "in_stock": p.is_in_stock,
            })

        text = (
            f"🎮 Found **{len(products)} product(s)**"
            f"{' under ৳' + str(int(price_ceiling)) if price_ceiling else ''}"
            f"{' in ' + matched_slug.replace('-',' ').title() if matched_slug else ''}:"
        )

        return {
            "type":     "products",
            "text":     text,
            "links":    links,
            "products": product_list,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Strategy 3: Navigation hints
# ──────────────────────────────────────────────────────────────────────────────
class NavigationStrategy(BaseChatStrategy):
    NAV_MAP = {
        "cart":     ("/cart",        "🛒 Go to your cart"),
        "orders":   ("/orders",      "📦 View my orders"),
        "wishlist": ("/wishlist",    "❤️ My wishlist"),
        "login":    ("/login",       "🔑 Login page"),
        "register": ("/register",    "📝 Create an account"),
        "home":     ("/",            "🏠 Homepage"),
        "all products": ("/products","🛍️ All products"),
    }

    def can_handle(self, message: str) -> bool:
        msg = message.lower()
        return any(kw in msg for kw in self.NAV_MAP)

    def handle(self, message: str) -> dict:
        msg = message.lower()
        links = []
        for kw, (url, label) in self.NAV_MAP.items():
            if kw in msg:
                links.append({"label": label, "url": url})
        return {
            "type":     "navigation",
            "text":     "Sure! Here are some quick links:",
            "links":    links[:3],
            "products": [],
        }


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _fallback() -> dict:
    return {
        "type":     "fallback",
        "text":     FALLBACK_RESPONSE,
        "links":    [],
        "products": [],
    }


def _is_greeting(message: str) -> bool:
    greet_words = ["hi", "hello", "hey", "good morning", "good evening",
                   "howdy", "what's up", "whats up", "hiya", "sup", "yo"]
    msg = message.lower().strip()
    return any(msg.startswith(g) or msg == g for g in greet_words)


# ──────────────────────────────────────────────────────────────────────────────
# Facade (public API)
# ──────────────────────────────────────────────────────────────────────────────
class ChatbotFacade:
    """
    Facade that orchestrates the three strategies.
    Order of priority: greeting → service info → navigation → product search.
    Falls back to a helpful prompt when nothing matches.
    """

    _strategies: list[BaseChatStrategy] = [
        ServiceInfoStrategy(),
        NavigationStrategy(),
        ProductSearchStrategy(),
    ]

    @classmethod
    def process(cls, message: str) -> dict:
        """
        Entry point.  Returns a dict:
          {
            "type":     str,           # "greeting"|"info"|"products"|"navigation"|"fallback"
            "text":     str,           # main response text (supports **bold** markdown)
            "links":    list[dict],    # [{"label": str, "url": str}, ...]
            "products": list[dict],    # [{"name", "price", "url", "image", "in_stock"}, ...]
          }
        """
        if not message or not message.strip():
            return _fallback()

        if _is_greeting(message):
            import random
            return {
                "type":     "greeting",
                "text":     random.choice(GREETING_RESPONSES),
                "links":    [],
                "products": [],
            }

        for strategy in cls._strategies:
            if strategy.can_handle(message):
                return strategy.handle(message)

        return _fallback()
