# Ecommerce-Project-1
Ecommerce 

I  will be developing an E-commerce Product API for managing products of a given grocery store called Fresh Fruit. Users can add, update, delete and also see the available products.

Requirements
CRUD operations for products and users.
Endpoint for searching products by name or category.
Use Django ORM for database interactions.
Deploy the API PythonAnywhere
 

1. Main Features
User Management: Register, log in, update, and delete users.
Product Management: CRUD operations on products (add, view, update, delete).
Product Search: Search products by name or category.
Simple Authentication: Protect sensitive endpoints (e.g., product creation or deletion).
Optional: If time allows, add filtering, pagination, or product images.
2. Find an API 
Since you are managing your own database of products, external APIs are NOT required for core features. If you want to enrich product data (e.g., nutrition info), you could consider free APIs like:
Open Food Facts API — public database of food products.
3. Django Apps & Endpoints (Modular Design)
Split core functionality into logical Django apps:
App Name
Responsibilities & Core Endpoints
users
User registration, login, profiles
products
CRUD for products, search endpoints

Recommended Endpoints:
/api/users/ — create, list, detail, update, delete users.
/api/products/ — create, list, detail, update, delete, search products.
/api/products/?search=banana — search by name/category.


Relationships & Constraints:
Each product is "owned" by a user (added_by).
Basic fields can have validation (e.g., no negative quantity or price).
Use created_at to allow sorting and filtering by recency.
5. Project Timeline (Weekly 
Week
Goal
Tasks
1
Project setup & core app scaffolding
Initialize project, set up virtualenv, create apps, add models/serializers
2
User API & Authentication
User endpoints, registration, login/logout, permissions
3
Product CRUD API
Endpoints for product list/detail/create/update/delete
4
Product search/filtering
Implement search by name/category, add API documentation
5
Testing & bug fixing
Write API tests, fix issues, polish error messages
6
Deployment
Prepare for deployment, configure PythonAnywhere, test live API



