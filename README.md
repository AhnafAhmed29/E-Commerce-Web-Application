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

✨ Key Features

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
ecommerce_with_testing/
└── ecommerce_fixed/
    ├── app.py
    ├── config.py
    ├── requirements.txt
    ├── init_db.py
    ├── fix_database.py
    ├── migrate_variant_support_SQLITE.py
    ├── create_variants_migration.py
    ├── verify_buy_now.py
    ├── add_sample_variants.py

    ├── instance/
    │   └── ecommerce.db

    ├── models/
    │   ├── db.py
    │   ├── user.py
    │   ├── product.py
    │   ├── product_variant.py
    │   ├── order.py
    │   └── wishlist.py

    ├── services/
    │   ├── facade.py
    │   ├── chatbot_facade.py
    │   └── site_info.py

    ├── strategies/
    │   └── auth_strategy.py

    ├── factories/
    │   └── user_factory.py

    ├── templates/
    │   ├── *.html
    │   └── admin/

    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── images/

    └── testing/
        ├── unit/
        ├── component/
        ├── system/
        ├── acceptance/
        ├── blackbox/
        └── reports/

