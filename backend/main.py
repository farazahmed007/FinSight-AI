from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from middleware.auth import AuthException
from routes.api import api_bp
from routes.budgets import budgets_bp
from routes.goals import goals_bp
from routes.financial_health import financial_health_bp
from routes.planning import planning_bp
from database import init_db, load_seed_data
import os

app = FastAPI(
    title="FinSight AI API",
    description="Backend API for FinSight AI Application",
    version="1.0.0"
)

# Enable CORS for local development prototype
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers to match exact Flask responses
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "status": exc.status_code, "message": exc.message},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = str(exc.detail)
    if exc.status_code == 404:
        message = "Resource not found"
    elif exc.status_code == 401:
        message = "Unauthorized"
    elif exc.status_code == 400:
        message = "Bad Request"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "status": exc.status_code, "message": message},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": True, "status": 400, "message": "Bad Request"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": True, "status": 500, "message": "Internal Server Error"},
    )

# Include router
app.include_router(api_bp, prefix="/api")
app.include_router(budgets_bp, prefix="/api/budgets")
app.include_router(goals_bp, prefix="/api/goals")
app.include_router(financial_health_bp, prefix="/api/financial-health")
app.include_router(planning_bp, prefix="/api/planning")

@app.on_event("startup")
async def startup_event():
    # Initialize database
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'data', 'finance.db')):
        init_db()
        load_seed_data()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
