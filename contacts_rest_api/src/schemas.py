from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    birth: date
    additional_details: str = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ContactResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    birth: date
    additional_details: str = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
