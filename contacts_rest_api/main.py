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


from src.database.db import get_db
from src.routes import contacts, auth, users

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
    """
    The send_in_background function Sends an email in the background.
        ---
        tags: [email]
    
    
    :param background_tasks: BackgroundTasks: Add a task to the background
    :param body: EmailSchema: Get the email address from the request body
    :return: A dictionary with a message
    :doc-author: Trelent
    """
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
    """
    The custom_middleware function is a middleware function that adds the time it took to process the request
    to the response headers. This can be used for performance monitoring.
    
    :param request: Request: Access the request object
    :param call_next: Call the next middleware in the chain
    :return: A response object
    :doc-author: Trelent
    """
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers["performance"] = str(during)
    return response


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    """
    The root function is the entry point for the web application.
    It returns a TemplateResponse object, which renders an HTML template
    (index.html) with some context variables (title). The title variable is set to &quot;Contacts App&quot;.
    
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object
    :doc-author: Trelent
    """
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
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app, like database connections or caches.
    
    :return: A dictionary with the name of the class and an instance
    :doc-author: Trelent
    """
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;msg&quot; and value &quot;Hello Friend&quot;.
    
    
    :return: A dict object
    :doc-author: Trelent
    """
    return {"msg": "Hello Friend"}

# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# if __name__ == "__main__":
#     uvicorn.run("app:app", reload=True)
