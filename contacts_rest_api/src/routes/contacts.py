from typing import List
from datetime import date, timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repo_contacts
from src.database.models import User
from src.schemas import ContactBase, ContactResponse, UserBase, UserResponse
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.
        The function takes in an optional skip and limit parameter to paginate the results.
        
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Access the database
    :param current_user: User: Get the user_id of the current logged in user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repo_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/search_by_id/{id}", response_model=ContactResponse)
async def get_contact(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by id.
        Args:
            id (int): The ID of the contact to return.
            db (Session, optional): SQLAlchemy Session instance. Defaults to Depends(get_db).
            current_user (User, optional): User object from auth middleware. Defaults to Depends(auth_service.get_current_user).
    
    :param id: int: Specify the id of the contact we want to update
    :param db: Session: Get access to the database
    :param current_user: User: Get the user from the database
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The search_contacts_by_last_name function searches for a contact by last name.
        Args:
            lastname (str): The last name of the contact to search for.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object with user information and permissions. Defaults to Depends(auth_service.get_current_user).
        Returns:
            Contact: A single Contact object matching the provided criteria or None if no match is found.
    
    :param lastname: str: Pass the lastname of the contact to be searched
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user_id of the current logged in user
    :return: A list of contacts with the same last name
    :doc-author: Trelent
    """
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
    """
    The search_contacts_by_first_name function searches for a contact by first name.
        Args:
            firstname (str): The first name of the contact to search for.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object with user information and permissions. Defaults to Depends(auth_service.get_current_user).
        Returns:
            Contact: A single Contact object matching the provided criteria or None if no match is found.
    
    :param firstname: str: Pass the firstname of the contact to be searched for
    :param db: Session: Inject the database session into the function
    :param current_user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
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
    """
    The search_contacts_by_email function searches for a contact by email.
        Args:
            email (str): The email of the contact to search for.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object containing user information from the JWT token payload. Defaults to Depends(auth_service.get_current_user).
        Raises:
            HTTPException: 404 Not Found if no contacts are found with that email address or 500 Internal Server Error if there is an error in the database
    
    :param email: str: Pass the email of the contact to be searched
    :param db: Session: Get the database connection
    :param current_user: User: Get the current user information from the database
    :return: A contact
    :doc-author: Trelent
    """
    contact = await repo_contacts.search_contact_by_email(email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactBase object as input and returns the newly created contact.
        If an email already exists, it will return an HTTP 409 error.
    
    :param body: ContactBase: Pass the contact data to the function
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: The contact object, which is a dict
    :doc-author: Trelent
    """
    contact = await repo_contacts.get_contact_by_lastname_and_email(body.lastname ,body.email, db)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email exists!"
        )

    contact = await repo_contacts.create(body, db)
    return contact


@router.put("/{id}", response_model=ContactResponse)
async def update_contact(body: ContactBase, id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as parameters, which are used to update the contact.
        If no contact is found with that id, then an HTTPException is raised.
    
    :param body: ContactBase: Get the data from the request body
    :param id: int: Identify the contact to be deleted
    :param db: Session: Access the database
    :param current_user: User: Get the current user from the auth_service
    :return: An instance of contactbase, which is a pydantic model
    :doc-author: Trelent
    """
    contact = await repo_contacts.update(id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return contact


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
        Args:
            id (int): The ID of the contact to remove.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for authentication and authorization purposes. Defaults to Depends(auth_service.get_current_user).
    
    :param id: int: Identify the contact to be removed
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user that is currently logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repo_contacts.remove(id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get(
    "/birthdays", response_model=List[ContactResponse], name="Upcoming Birthdays"
)
async def get_birthdays(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_birthdays function returns a list of contacts with birthdays in the next 7 days.
        The function takes no parameters and returns a list of contact objects.
    
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A list of contacts that have birthdays in the next 7 days
    :doc-author: Trelent
    """
    today = date.today()
    end_date = today + timedelta(days=7)
    birthdays = await repo_contacts.get_birthdays(today, end_date, db)
    if birthdays is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return birthdays
