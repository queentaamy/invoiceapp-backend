"""
MAIN APPLICATION FILE

This file sets up the FastAPI application with all necessary configuration:
- Database connections
- CORS middleware for cross-origin requests
- API routes for authentication, customers, and invoices
"""

try:
    from dotenv import load_dotenv
except ImportError:
    # Allow app startup even if python-dotenv is not installed.
    def load_dotenv():
        return None

load_dotenv()  # Load environment variables from .env file when available

# Import FastAPI framework
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

# Import database setup
from app.database.connection import engine, Base, ensure_customer_ownership_columns
from app.utils.cache import response_cache

# Import models so database tables are created on startup
from app.models import models

# Import route handlers
from app.routes.customer import router as customer_router
from app.routes.invoice import router as invoice_router
from app.routes.auth import router as auth_router


# ✅ STEP 1: CREATE app INSTANCE
app = FastAPI(title="InvoiceFlow API", description="Invoice management system")


# ✅ STEP 2: ADD MIDDLEWARE (CORS - allows requests from different origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cache_key_for_request(request: Request) -> str:
    """
    Build a per-request cache key.

    Authorization is included so protected endpoints are cached per user token.
    """
    auth_header = request.headers.get("authorization", "")
    return f"{request.method}:{request.url.path}?{request.url.query}|auth={auth_header}"


@app.middleware("http")
async def cache_get_responses(request: Request, call_next):
    """
    Cache successful JSON GET responses and invalidate on write requests.
    """
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        response_cache.clear()
        response = await call_next(request)
        response.headers["X-Cache"] = "BYPASS"
        return response

    if request.method != "GET":
        response = await call_next(request)
        response.headers["X-Cache"] = "BYPASS"
        return response

    cache_key = _cache_key_for_request(request)
    cached_entry = response_cache.get(cache_key)
    if cached_entry is not None:
        cached_headers = dict(cached_entry.headers)
        cached_headers["X-Cache"] = "HIT"
        return Response(
            content=cached_entry.body,
            status_code=cached_entry.status_code,
            headers=cached_headers,
            media_type=cached_entry.media_type,
        )

    response = await call_next(request)
    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in {"content-length", "x-cache"}
    }

    content_type = response.headers.get("content-type", "")
    if response.status_code == 200 and "application/json" in content_type:
        response_cache.set(
            cache_key,
            body=body,
            status_code=response.status_code,
            media_type=response.media_type,
            headers=headers,
        )
        headers["X-Cache"] = "MISS"
    else:
        headers["X-Cache"] = "BYPASS"

    return Response(
        content=body,
        status_code=response.status_code,
        headers=headers,
        media_type=response.media_type,
    )


# ✅ STEP 3: CREATE DATABASE TABLES (if they don't exist)
Base.metadata.create_all(bind=engine)

# ✅ STEP 3.5: PATCH EXISTING SQLITE TABLES FOR NEW MULTI-USER OWNERSHIP COLUMNS
ensure_customer_ownership_columns()


# ✅ STEP 4: INCLUDE ROUTES (register all API endpoints)
app.include_router(customer_router, tags=["Customers"])
app.include_router(invoice_router, tags=["Invoices"])
app.include_router(auth_router, tags=["Authentication"])


# Root endpoint - health check
@app.get("/", tags=["Health"])
def root():
    """Check if the API is running"""
    return {"message": "InvoiceFlow API is running"}
