"""
Site information knowledge base for the chatbot.
Centralises store policies, contact details, and FAQs so the
ChatbotFacade can answer service questions without hitting an API.
"""

SITE_INFO = {
    "delivery": {
        "keywords": ["delivery", "shipping", "ship", "courier", "how long", "days", "arrive", "dispatch", "send"],
        "title": "Delivery & Shipping",
        "answer": (
            "🚚 **Delivery Information**\n\n"
            "• **Dhaka city:** 1–2 business days — ৳60 flat rate\n"
            "• **Outside Dhaka:** 2–4 business days — ৳100–130 depending on location\n"
            "• **Express (same-day Dhaka):** Available on select products — ৳120\n"
            "• We use Sundarban, Pathao, and Steadfast courier services.\n"
            "• Orders placed before 2 PM are usually dispatched the same day.\n"
            "• You'll receive an SMS with a tracking number once your order ships."
        ),
    },
    "refund": {
        "keywords": ["refund", "return", "exchange", "money back", "replace", "wrong item", "damaged", "broken"],
        "title": "Refund & Return Policy",
        "answer": (
            "🔄 **Refund & Return Policy**\n\n"
            "• **Return window:** 7 days from delivery date.\n"
            "• Items must be unused, in original packaging, with all accessories included.\n"
            "• **Eligible for return:** Wrong item, factory defect, or damaged in transit.\n"
            "• **Not eligible:** Change of mind after opening, physical damage by user.\n"
            "• Approved refunds are processed within 3–5 business days.\n"
            "• Contact us at **01819-940370** or email to initiate a return."
        ),
    },
    "warranty": {
        "keywords": ["warranty", "guarantee", "official", "service", "repair", "broken after", "months"],
        "title": "Warranty Policy",
        "answer": (
            "🛡️ **Warranty Policy**\n\n"
            "• All products come with **official brand warranty** (typically 1–2 years).\n"
            "• We are an authorized reseller — warranty claims are processed directly with the brand.\n"
            "• **Gaming keyboards/mice:** 1 year\n"
            "• **Controllers & gamepads:** 1 year\n"
            "• **Monitors:** 1–3 years (brand-specific)\n"
            "• Bring your product + purchase invoice to our store for warranty service.\n"
            "• Hotline: **01819-940370** (10 AM – 8 PM)"
        ),
    },
    "payment": {
        "keywords": ["payment", "pay", "bkash", "nagad", "rocket", "bank", "cash", "card", "online payment", "cod"],
        "title": "Payment Methods",
        "answer": (
            "💳 **Payment Methods**\n\n"
            "• 💵 **Cash on Delivery (COD)** — available nationwide\n"
            "• 📱 **bKash / Nagad / Rocket** — mobile banking accepted\n"
            "• 🏦 **Bank Transfer** — Dutch-Bangla, BRAC, Islami Bank\n"
            "• 💳 **Debit/Credit Card** — Visa, Mastercard\n"
            "• All online payments are encrypted and secure.\n"
            "• For COD, payment is collected upon delivery."
        ),
    },
    "contact": {
        "keywords": ["contact", "phone", "call", "email", "hotline", "address", "location", "store", "reach", "support"],
        "title": "Contact & Store Info",
        "answer": (
            "📞 **Contact Us**\n\n"
            "• **Hotline:** 01819-940370 (10 AM – 8 PM, every day)\n"
            "• **Email:** support@ezgadgets.com.bd\n"
            "• **Dhaka Showroom:** Level 4, Multiplan Centre, New Elephant Road, Dhaka-1205\n"
            "• **Chattogram Branch:** GEC Circle, Chattogram\n"
            "• **Facebook:** facebook.com/ezgadgetsbd\n"
            "• Our team responds to messages within 1 hour during business hours."
        ),
    },
    "support_hours": {
        "keywords": ["hours", "open", "close", "available", "when", "time", "24/7", "business hours"],
        "title": "Support Hours",
        "answer": (
            "🕐 **Support Hours**\n\n"
            "• **Online support:** 10 AM – 8 PM, 7 days a week\n"
            "• **Store hours:** 10 AM – 8 PM (Friday: 2 PM – 8 PM)\n"
            "• **Emergency:** WhatsApp at 01819-940370 for urgent issues\n"
            "• Response time: Under 1 hour during business hours"
        ),
    },
    "about": {
        "keywords": ["about", "who", "company", "trusted", "genuine", "authentic", "authorized"],
        "title": "About Gamers GADGETS",
        "answer": (
            "🎮 **About Gamers GADGETS**\n\n"
            "• Bangladesh's premier gaming accessories store since 2019.\n"
            "• Authorized reseller for GameSir, AULA, Samsung, and many more brands.\n"
            "• **100% genuine products** — no fakes, ever.\n"
            "• Physical showrooms in Dhaka and Chattogram.\n"
            "• Trusted by 50,000+ gamers across Bangladesh.\n"
            "• We offer expert advice, after-sales support, and fast nationwide delivery."
        ),
    },
}

GREETING_RESPONSES = [
    "👋 Hi! I'm your Gamers GADGETS assistant. I can help you find products, check policies, or guide you around the store. What can I help you with?",
    "🎮 Hello! Welcome to Gamers GADGETS. Ask me about keyboards, monitors, gamepads, delivery info, or anything else!",
    "👾 Hey there! Need help finding the perfect gaming gear? Just ask — I'm here to help!",
]

FALLBACK_RESPONSE = (
    "🤔 I'm not sure about that one. Try asking me about:\n\n"
    "• **Products** — e.g., 'show me keyboards' or 'best monitor'\n"
    "• **Delivery** — shipping times and costs\n"
    "• **Refund & warranty** — our policies\n"
    "• **Payment** — accepted methods\n"
    "• **Contact** — reach our team\n\n"
    "Or use the quick buttons below! 👇"
)
