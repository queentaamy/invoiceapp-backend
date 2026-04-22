# InvoiceFlow API
A backend system for managing customers and generating invoices for small businesses.
---
## The Problem
Many small businesses struggle to manage customer records and invoices efficiently. Most rely on spreadsheets or manual methods, which can become disorganized and difficult to maintain over time. There is a need for a simple and structured system that handles customer data and billing in a reliable way.
---
## What It Does
* Allows users to create and manage customers  
* Enables invoice creation with multiple items  
* Automatically calculates subtotal, tax, and total  
* Supports secure user authentication  
* Ensures each user only accesses their own data  
---
## Demo
Watch the project demo here:  
https://www.loom.com/share/f99ab78b3a224563aa0da02689737726
You can also explore the API interactively via:
http://127.0.0.1:8000/docs
---
## Tech Stack
Python  
Core programming language used for backend logic  
FastAPI  
Used to build the RESTful API and interactive documentation  
SQLAlchemy  
Handles database interactions and relationships  
SQLite  
Lightweight database for persistent storage  
Uvicorn  
ASGI server used to run the application  
---
## How to Run It Locally
1. Clone the repository
```bash
git clone https://github.com/queentaamy/invoiceapp-backend
cd invoice-flow

2. Create a virtual environment

python -m venv venv
source venv/bin/activate

On Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Run the server

uvicorn app.main:app --reload

5. Open in browser

http://127.0.0.1:8000/docs

⸻

API Endpoints

Authentication

Method	Endpoint	Description
POST	/signup	Create a new user
POST	/login	Authenticate user and return token

⸻

Customers

Method	Endpoint	Description
GET	/customers	Retrieve all customers for the logged in user
POST	/customers	Create a new customer

⸻

Invoices

Method	Endpoint	Description
GET	/invoices	Retrieve all invoices
GET	/invoices/{id}	Retrieve a single invoice
POST	/invoices	Create a new invoice

⸻

How to Test

1. Open the API docs in your browser:

http://127.0.0.1:8000/docs

2. Create a user using /signup
3. Log in using /login to get an access token
4. Use the token to create customers and invoices
5. Test endpoints directly using the interactive interface

⸻

Database Design

User
Stores authentication details

Customer
Linked to a specific user

Invoice
Stores billing data and links to a customer

InvoiceItem
Stores individual items within an invoice

These relationships ensure proper data organization and user level isolation.

⸻

Key Features

* Secure authentication using JWT
* User specific data isolation
* Automatic invoice calculations
* Interactive API documentation
* Structured backend design

⸻

Future Improvements

* PDF invoice generation
* Payment tracking
* Email notifications for invoices
* Deployment with a production database

⸻

Author

Asantewa Tutua Appiah
Computer Science student focused on backend and cloud engineering
