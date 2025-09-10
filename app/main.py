from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .models import user, product,category,cart
from . import database
from .routes import cart_crud, login_signup, product,category,search,cart_crud, order as order_routes, notifications
# from .routes.restaurant import get_restaurants, menu
# from .routes.user import Address



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(user.Base.metadata.create_all,checkfirst=True)
    yield  # This allows the app to run
    # You can add cleanup tasks after `yield` if needed

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(login_signup.router)
app.include_router(product.router)
app.include_router(category.router)
app.include_router(search.router)
app.include_router(cart_crud.router)
app.include_router(order_routes.router)
app.include_router(notifications.router)


@app.get("/")
async def read_root(db: Session = Depends(database.get_db)):
    
    return {"message": "Hello"}
