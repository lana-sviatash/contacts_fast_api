from datetime import date

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase


async def create(body: ContactBase, db: Session, user: User):
    """
    The create function creates a new contact in the database.
        
    
    :param body: ContactBase: Create a new contact object
    :param db: Session: Access the database
    :param user: User: Get the user_id of the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(id: int, body: ContactBase, user_id: int, db: Session):
    """
    The update function updates a contact in the database.
        
    
    :param id: int: Get the contact by id
    :param body: ContactBase: Pass the request body to the function
    :param user_id: int: Ensure that the user is only able to delete their own contacts
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(id, user_id, db)
    if contact and contact.user_id == user_id:
        contact.email = body.email
        contact.additional_data = body.additional_details
        contact.birth_date = body.birth
        db.commit()
    return contact


async def remove(id: int, user_id: int, db: Session):
    """
    The remove function removes a contact from the database.
        
    
    :param id: int: Specify the id of the contact to be removed
    :param user_id: int: Ensure that the user can only delete contacts they have created
    :param db: Session: Pass the database session to the function
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(id, user_id, db)
    if contact and contact.user_id == user_id:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts(db: Session, user: User):
    """
    The get_contacts function returns a list of contacts for the user.
        
    
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user_id from the user object
    :return: A list of contacts, so we can use the 'contacts' variable to access it
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=user.id).all()
    return contacts


async def get_contact_by_id(id: int, user_id: int, db: Session):
    """
    The get_contact_by_id function returns a contact by its id.
        Args:
            id (int): The ID of the contact to be retrieved.
            user_id (int): The ID of the user who owns this contact.
            db (Session, optional): A database session object for interacting with the database. Defaults to None.&lt;/code&gt;
    
    :param id: int: Filter the contact by id
    :param user_id: int: Filter the contacts by user_id
    :param db: Session: Pass the database session to the function
    :return: A contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=id, user_id=user_id).first()
    return contact


async def get_contact_by_lastname_and_email(lastname: str, email: str, user_id: int, db: Session):
    """
    The get_contact_by_lastname_and_email function returns a contact object from the database based on the lastname and email parameters.
        Args:
            lastname (str): The contact's last name.
            email (str): The contact's email address.
            user_id (int): The id of the user who owns this contact record in our database.
        Returns: 
            Contact object or None if no matching record is found.
    
    :param lastname: str: Filter the database by lastname
    :param email: str: Filter the database by email
    :param user_id: int: Filter the results by user_id
    :param db: Session: Connect to the database
    :return: The contact with the matching lastname and email
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(lastname=lastname, email=email, user_id=user_id).first()
    return contact


async def search_contacts_by_lastname(lastname: str, user: User, db: Session):
    """
    The search_contacts_by_lastname function searches for contacts by lastname.
        Args:
            lastname (str): The contact's last name to search for.
            user (User): The user who is searching for the contact.
            db (Session): A database session object that will be used to query the database with SQLAlchemy ORM methods.
    
    :param lastname: str: Filter the contacts by lastname
    :param user: User: Get the user id from the user object
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(lastname=lastname, user_id=user.id).all()
    return contacts


async def search_contacts_by_firstname(firstname: str, user: User, db: Session):
    """
    The search_contacts_by_firstname function searches for contacts by firstname.
        Args:
            firstname (str): The contact's first name.
            user (User): The user who owns the contact(s).
            db (Session): A database session object to query with.
        Returns:
            List[Contact]: A list of Contact objects that match the search criteria.
    
    :param firstname: str: Define the firstname of the contact that will be searched for
    :param user: User: Pass the user object to the function
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(firstname=firstname, user_id=user.id).all()
    return contacts


async def search_contact_by_email(email: str, user: User, db: Session):
    """
    The search_contact_by_email function searches for a contact by email.
        Args:
            email (str): The email of the contact to search for.
            user (User): The user who owns the contacts to search through.
            db (Session): A database session object used to query the database with SQLAlchemy ORM methods.
        Returns: 
            Contact: A single Contact object if found, otherwise None.
    
    :param email: str: Search for a contact by email
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass the database session to the function
    :return: The first contact that matches the email and user_id
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(email=email, user_id=user.id).first()
    return contact


async def get_birthdays(start_date: date, end_date: date, db: Session, user: User):
    """
    The get_birthdays function returns a list of contacts with birthdays between the start and end dates.
        Args:
            start_date (date): The first date to search for birthdays.
            end_date (date): The last date to search for birthdays.
            db (Session): A database session object used to query the database.
            user (User): A User object representing the current user making this request, used in filtering results by owner.
    
    :param start_date: date: Get the start date of the birthdays
    :param end_date: date: Specify the end date of the range
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user id from the database
    :return: A list of birthdays in the given date range
    :doc-author: Trelent
    """
    birthdays = (
        db.query(Contact)
        .filter(Contact.birth >= start_date, Contact.birth <= end_date, Contact.user_id == user.id)
        .all()
    )
    return birthdays

