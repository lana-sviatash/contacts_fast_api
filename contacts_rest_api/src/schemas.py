from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


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


class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: str
    avatar: str

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
