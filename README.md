# E-Commerce-Web-Application
A full-featured **Flask-based eCommerce web application** implementing modern software engineering practices, including **design patterns, modular architecture, and multi-level testing**.

📌 Project Overview

This project focuses on the development of a professional, scalable, and user-centric e-commerce web application designed for selling gaming and technology-related gadgets.
The primary goal is to provide a reliable online storefront where customers can seamlessly browse products, view detailed information, and make confident purchasing decisions through a smooth and secure digital experience.

The system is built with a modern frontend and a robust backend architecture, ensuring performance, security, and future scalability.

🎯 Objectives

* Create a visually appealing and intuitive user interface

* Enable fast and seamless product discovery

* Ensure secure data handling and user authentication

* Design a scalable system that grows with business needs

👥 Client & User Requirements

The application is designed to meet the following core requirements:

* Easy browsing of products with clear categorization

* Detailed product pages including specifications, price, and stock status

* Responsive design for both mobile and desktop users

* Secure and reliable shopping cart functionality

* Fast page loading and smooth navigation

* Scalable architecture for future business expansion

* Separate Admin and User Authentication System

✨ Key Findings

The following features are implemented to fulfill client and user needs:

* Modern, responsive, and mobile-friendly user interface

* Product listings organized by categories

* Detailed product pages to support informed purchasing decisions

* Session-based shopping cart with automatic quantity and price calculation

* Database-driven product management using SQLite / MySQL

* SEO-friendly structure with reusable templates

* kend architecture prepared for:

  * Admin panel integration

  * Payment gateway integration

🛠️ Technology Stack (Proposed)

* Frontend: HTML, CSS, JavaScript

* Backend: Server-side scripting (framework-ready)

* Database: SQLite / MySQL

* Architecture: Scalable and modular design

## 🚀 Features

- 🛍️ Product browsing and search  
- 🛒 Shopping cart & checkout system  
- ❤️ Wishlist functionality  
- 🔐 User authentication (login/register)  
- 🧑‍💼 Admin dashboard for product & order management  
- 🤖 Chatbot integration (basic support)  
- 📦 Product variants support  
- 📊 Fully integrated testing suite  

---

## 🏗️ Project Structure

```bash
ecommerce_fixed/
├── app.py                         # Main Flask application entry point and route definitions
├── config.py                      # App configuration (development, production, testing)
├── requirements.txt               # Runtime Python dependencies
├── init_db.py                     # Initializes database tables and seed-ready structure
├── fix_database.py                # Database repair/cleanup helper
├── create_variants_migration.py   # Variant schema migration helper
├── migrate_variant_support_SQLITE.py # SQLite-specific variant migration script
├── add_sample_variants.py         # Script to insert sample product variants
├── verify_buy_now.py              # Utility script for buy-now verification/debugging
│
├── instance/
│   └── ecommerce.db               # SQLite database file
│
├── models/                        # Data layer / ORM models
│   ├── db.py                      # SQLAlchemy database object
│   ├── product.py                 # Product model and product-related helpers
│   ├── product_variant.py         # Product variant model
│   ├── order.py                   # Order, order item, cart-related models
│   ├── user.py                    # User/admin model and authentication fields
│   └── wishlist.py                # Wishlist model
│
├── services/                      # Service/facade layer
│   ├── facade.py                  # Core business facades for products, cart, auth, orders
│   ├── chatbot_facade.py          # Chatbot orchestration/service logic
│   └── site_info.py               # Static store/service information used by chatbot/pages
│
├── strategies/                    # Strategy pattern implementations
│   └── auth_strategy.py           # Authentication strategy logic
│
├── factories/                     # Factory pattern implementations
│   └── user_factory.py            # Factory for creating user/admin entities
│
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Shared site layout
│   ├── index.html                 # Home page
│   ├── products.html              # Product listing page
│   ├── product.html               # Product details page
│   ├── cart.html                  # Shopping cart page
│   ├── checkout.html              # Checkout / billing page
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── orders.html                # User order history page
│   ├── order_confirmation.html    # Order confirmation page
│   ├── wishlist.html              # Wishlist page
│   ├── about.html                 # About page
│   ├── contact.html               # Contact page
│   ├── 404.html                   # Not found page
│   ├── 500.html                   # Server error page
│   └── admin/                     # Admin dashboard templates
│       ├── dashboard.html         # Admin dashboard home
│       ├── products.html          # Admin product management page
│       ├── add_product.html       # Add product form
│       ├── edit_product.html      # Edit product form
│       ├── orders.html            # Admin orders list
│       └── order_detail.html      # Admin order detail view
│
├── static/                        # Frontend assets
│   ├── css/
│   │   ├── style.css              # Main site styling
│   │   ├── responsive.css         # Responsive/mobile-specific styling
│   │   ├── admin.css              # Admin dashboard styling
│   │   ├── hero-slider.css        # Hero/banner section styling
│   │   ├── home-marketplace.css   # Home page marketplace layout styling
│   │   ├── categories.css         # Category block styling
│   │   ├── features-bar.css       # Feature strip styling
│   │   ├── stock-status.css       # Product stock display styling
│   │   ├── chatbot.css            # Chatbot UI styling
│   │   ├── lightbox.css           # Lightbox/gallery styling
│   │   └── button-hover-effects-FIXED.css # Button interaction styling
│   ├── js/
│   │   ├── chatbot.js             # Chatbot frontend behavior
│   │   └── home-hero.js           # Home page hero interactions
│   └── images/                    # Product images, hero images, icons
│
└── testing/                       # Full project testing suite and reports
    ├── conftest.py                # Shared pytest fixtures and seeded test data
    ├── pytest.ini                 # Pytest configuration and markers
    ├── requirements-test.txt      # Test dependencies
    ├── README.md                  # Testing-specific usage guide
    │
    ├── acceptance/                # Acceptance tests mapped to user stories
    ├── unit/                      # Unit tests for models, services, helpers, strategies
    ├── system/                    # End-to-end system tests using Flask test client
    ├── blackbox/                  # Browser-style black-box tests (Playwright)
    ├── component/                 # Component-level integration tests
    ├── reports/                   # Generated test reports and coverage
    └── ecommerce_fixed/           # Test-isolated project copy/support structure
```

# How to Run the Full Project
- 1. Clone or extract the project

  Move into the project root:

cd ecommerce_fixed
- 2. Create and activate a virtual environment
Windows
python -m venv venv
venv\Scripts\activate
Linux / macOS
python -m venv venv
source venv/bin/activate
- 3. Install dependencies
pip install -r requirements.txt
- 4. Initialize the database

If the database is not already prepared, run:

python init_db.py

If required, apply migration or helper scripts for variants or database fixes:

python create_variants_migration.py
python migrate_variant_support_SQLITE.py
python fix_database.py

Only run these if needed for a fresh setup or schema update.

- 5. Start the Flask application
python app.py

Then open the app in your browser, usually at:

http://127.0.0.1:5000

## 🧪 Testing

This project follows a multi-layered testing strategy to ensure robustness and quality.

🔹 1. Unit Testing
Tests individual components in isolation
Covers models, services, factories, strategies

📁 testing/unit/

🔹 2. Component Testing
Tests interaction between modules

📁 testing/component/

🔹 3. System Testing
Tests complete backend workflows

📁 testing/system/

🔹 4. Acceptance Testing
Based on user stories (US01–US13)
Validates real-world requirements

📁 testing/acceptance/

🔹 5. Black Box Testing (UI)
End-to-end UI testing using Playwright
Simulates real user interactions

📁 testing/blackbox/

📊 Test Reports

Generated reports include:

Coverage reports
HTML reports
JUnit XML reports
Acceptance matrix

# Testing Folder Structure
```bash
testing/
├── conftest.py
├── pytest.ini
├── requirements-test.txt
├── README.md
│
├── acceptance/
│   ├── test_us01_view_products.py
│   ├── test_us02_product_details.py
│   ├── test_us03_add_to_cart.py
│   ├── test_us04_manage_cart.py
│   ├── test_us05_responsive_access.py
│   ├── test_us06_about_contact.py
│   ├── test_us07_product_data_management.py
│   ├── test_us09_search.py
│   ├── test_us10_cart_summary.py
│   ├── test_us11_stock_status.py
│   ├── test_us12_reliability.py
│   └── test_us13_authentication.py
│
├── unit/
│   ├── test_models_product.py
│   ├── test_models_order.py
│   ├── test_models_user.py
│   ├── test_services_auth_facade.py
│   ├── test_services_product_facade.py
│   ├── test_services_cart_facade.py
│   ├── test_services_order_facade.py
│   ├── test_strategies_auth.py
│   ├── test_factories_user_factory.py
│   └── test_helpers_slug.py
│
├── system/
│   ├── test_customer_journey.py
│   ├── test_admin_product_management.py
│   ├── test_checkout_flow.py
│   └── test_search_and_stock_flow.py
│
├── blackbox/
│   ├── test_public_pages_playwright.py
│   ├── test_cart_playwright.py
│   ├── test_auth_playwright.py
│   └── test_responsive_playwright.py
│
├── component/
│   ├── test_product_component.py
│   ├── test_cart_component.py
│   ├── test_auth_component.py
│   └── test_admin_component.py
│
└── reports/
    ├── junit/
    ├── html/
    ├── coverage/
    └── acceptance_matrix/
```


📁 testing/reports/

▶️ Running Tests
# Install test dependencies
pip install -r testing/requirements-test.txt

# Run all tests
pytest

# Run specific category
pytest testing/unit/
pytest testing/system/
pytest testing/acceptance/

# Generate coverage report
pytest --cov=.
