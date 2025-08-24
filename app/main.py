from fastapi import FastAPI
from .routes import products, users, orders


# Create the FastAPI application instance
app = FastAPI()

# Include the products router
app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
