from typing import List
from datetime import date, timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repo_contacts
from src.database.models import User
from src.schemas import ContactBase, ContactResponse, UserBase, UserResponse
from src.services.auth import auth_service


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], name="All contacts")
async def get_contacts(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repo_contacts.get_contacts(db)
    return contacts


@router.get("/search_by_id/{id}", response_model=ContactResponse)
async def get_contact(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.get_contact_by_id(id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get(
    "/search_by_lastname/{lastname}",
    response_model=List[ContactResponse],
    name="Contacts by last name",
)
async def search_contacts_by_last_name(lastname: str, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.search_contacts_by_lastname(lastname, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get(
    "/search_by_firstname/{firstname}",
    response_model=List[ContactResponse],
    name="Contacts by first name",
)
async def search_contacts_by_first_name(firstname: str, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.search_contacts_by_firstname(firstname, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get(
    "/search_by_email/{email}",
    response_model=List[ContactResponse],
    name="Contacts by email",
)
async def search_contacts_by_email(email: str, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.search_contact_by_email(email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.get_contact_by_lastname_and_email(body.lastname ,body.email, db)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email exists!"
        )

    contact = await repo_contacts.create(body, db)
    return contact


@router.put("/{id}", response_model=ContactResponse)
async def update_contact(body: ContactBase, id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.update(id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return contact


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repo_contacts.remove(id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get(
    "/birthdays", response_model=List[ContactResponse], name="Upcoming Birthdays"
)
async def get_birthdays(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    today = date.today()
    end_date = today + timedelta(days=7)
    birthdays = await repo_contacts.get_birthdays(today, end_date, db)
    if birthdays is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return birthdays
