from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import router
from app.database import engine
from app.models import Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title="XML API Service", version="1.0", lifespan=lifespan)

app.include_router(router)
