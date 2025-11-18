from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, complaints, admin, notifications
from app.services.escalation_service import check_and_escalate_complaints, initialize_default_escalation_rules
from app.config import settings

# Initialize scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await initialize_default_escalation_rules()
    
    # Start escalation checker
    scheduler.add_job(
        check_and_escalate_complaints,
        'interval',
        minutes=settings.ESCALATION_CHECK_INTERVAL_MINUTES,
        id='escalation_checker'
    )
    scheduler.start()
    print(f"Escalation checker started (runs every {settings.ESCALATION_CHECK_INTERVAL_MINUTES} minutes)")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    await close_mongo_connection()

app = FastAPI(
    title="Cloud Complaint Management System",
    description="A comprehensive complaint management system with auto-escalation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(notifications.router)

@app.get("/")
async def root():
    return {
        "message": "Cloud Complaint Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
