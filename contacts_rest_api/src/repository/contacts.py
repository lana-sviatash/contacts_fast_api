from datetime import date

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactBase


async def create(body: ContactBase, db: Session):
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(id: int, body: ContactBase, db: Session):
    contact = await get_contact_by_id(id, db)
    if contact:
        contact.email = body.email
        contact.additional_data = body.additional_details
        contact.birth_date = body.birth
        db.commit()
    return contact


async def remove(id: int, db: Session):
    contact = await get_contact_by_id(id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts(db: Session):
    contacts = db.query(Contact).all()
    return contacts


async def get_contact_by_id(id: int, db: Session):
    contact = db.query(Contact).filter_by(id=id).first()
    return contact


async def get_contact_by_lastname_and_email(lastname: str, email: str, db: Session):
    contact = db.query(Contact).filter_by(lastname=lastname, email=email).first()
    return contact


async def search_contacts_by_lastname(lastname: str, db: Session):
    contacts = db.query(Contact).filter_by(lastname=lastname).all()
    return contacts


async def search_contacts_by_firstname(firstname: str, db: Session):
    contacts = db.query(Contact).filter_by(firstname=firstname).all()
    return contacts


async def search_contact_by_email(email: str, db: Session):
    contact = db.query(Contact).filter_by(email=email).all()
    return contact


async def get_birthdays(start_date: date, end_date: date, db: Session):
    birthdays = (
        db.query(Contact)
        .filter(Contact.birth >= start_date, Contact.birth_date <= end_date)
        .all()
    )
    return birthdays

