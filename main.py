from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from database import engine, AsyncSessionLocal
from fastapi.middleware.cors import CORSMiddleware
from routers import lansettings, users
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from sqlalchemy import select
import models

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: Create default LAN settings if none exist
    yield     
    # Shutdown
    await engine.dispose()

app = FastAPI(title="LAN Backend", description="Backend for LAN party management", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],        
)   

app.include_router(lansettings.router, prefix="/api/lan-settings", tags=["LAN Settings"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_override(request: Request, exception: StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

@app.exception_handler(RequestValidationError)
async def validation_exception_override(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

