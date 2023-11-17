from datetime import date

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase


async def create(body: ContactBase, db: Session, user: User):
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(id: int, body: ContactBase, user_id: int, db: Session):
    contact = await get_contact_by_id(id, db)
    if contact and contact.user_id == user_id:
        contact.email = body.email
        contact.additional_data = body.additional_details
        contact.birth_date = body.birth
        db.commit()
    return contact


async def remove(id: int, user_id: int, db: Session):
    contact = await get_contact_by_id(id, db)
    if contact and contact.user_id == user_id:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts(db: Session, user: User):
    contacts = db.query(Contact).filter_by(user_id=user.id).all()
    return contacts


async def get_contact_by_id(id: int, user_id: int, db: Session):
    contact = db.query(Contact).filter_by(id=id, user_id=user_id).first()
    return contact


async def get_contact_by_lastname_and_email(lastname: str, email: str, user_id: int, db: Session):
    contact = db.query(Contact).filter_by(lastname=lastname, email=email, user_id=user_id).first()
    return contact


async def search_contacts_by_lastname(lastname: str, user: User, db: Session):
    contacts = db.query(Contact).filter_by(lastname=lastname, user_id=user.id).all()
    return contacts


async def search_contacts_by_firstname(firstname: str, user: User, db: Session):
    contacts = db.query(Contact).filter_by(firstname=firstname, user_id=user.id).all()
    return contacts


async def search_contact_by_email(email: str, user: User, db: Session):
    contact = db.query(Contact).filter_by(email=email, user_id=user.id).first()
    return contact


async def get_birthdays(start_date: date, end_date: date, db: Session, user: User):
    birthdays = (
        db.query(Contact)
        .filter(Contact.birth >= start_date, Contact.birth_date <= end_date, Contact.user_id == user.id)
        .all()
    )
    return birthdays

