from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import database, models
from .routes import login_signup
from .routes.restaurant import get_restaurants, menu
from .routes.user import Address



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
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
app.include_router(get_restaurants.router)
app.include_router(menu.router)
app.include_router(Address.router)


@app.get("/")
async def read_root(db: Session = Depends(database.get_db)):
    
    return {"message": "Hello"}
