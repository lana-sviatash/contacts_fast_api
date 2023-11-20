from typing import List
import redis.asyncio as redis
import uvicorn
import time
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import EmailStr, BaseModel

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


from src.database.db import get_db
from src.routes import contacts, auth

class EmailSchema(BaseModel):
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME="lana-sv@meta.ua",
    MAIL_PASSWORD="qwerTy@123",
    MAIL_FROM="lana-sv@meta.ua",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Service",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/send-email")
async def send_in_background(background_tasks: BackgroundTasks, body: EmailSchema):
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[body.email],
        template_body={"fullname": "Dear friend"},
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message, template_name="example_email.html")

    return {"message": "email has been sent"}

@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers["performance"] = str(during)
    return response


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Contacts App"}
    )


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone() # Make request
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Bad connecting to the database")


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"msg": "Hello Friend"}

# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# if __name__ == "__main__":
#     uvicorn.run("app:app", reload=True)
