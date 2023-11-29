import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.schemas import ContactBase, ContactResponse
from src.repository.contacts import (
    create,
    update,
    remove,
    get_contacts,
    get_contact_by_id,
    get_contact_by_lastname_and_email,
    search_contacts_by_lastname,
    search_contacts_by_firstname,
    search_contact_by_email,
    get_birthdays
)



class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@test.com")

    async def test_create_contact(self):
        body_data = ContactBase(
            id = 1,
            firstname = "Someone",
            lastname = "Somewhere",
            email = "some@example.com",
            phone = "123456789",
            birth = "1990-01-01",
            additional_details = "Additional details",
            created_at = "2023-01-01T12:00:00",
            updated_at = "2023-01-01T12:00:00"
        )

        body = body_data.model_dump()

        result = await create(body, self.session, self.user)
        self.assertEqual(result.firstname, body_data.firstname)
        self.assertEqual(result.lastname, body_data.lastname)
        self.assertEqual(result.email, body_data.email)
        self.assertEqual(result.phone, body_data.phone)
        self.assertEqual(result.birth, body_data.birth)
        self.assertEqual(result.additional_details, body_data.additional_details)
        self.assertEqual(result.created_at, body_data.created_at)
        self.assertEqual(result.updated_at, body_data.updated_at)
        self.assertEqual(result.user_id, self.user.id)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact(self):
        contact_id = 1
        user_id = self.user.id
        email = "old_email@example.com"
        contact = Contact(id=contact_id, email=email, user_id=user_id)
                
        with patch("src.repository.contacts.get_contact_by_id") as mock_get_contact_by_id:
            mock_get_contact_by_id.return_value = contact

        new_email = "updated_email@example.com"
        body_data = ContactBase(
            id=contact_id,
            email=new_email,
            birth="2000-01-01",
            additional_details="Updated additional details",
        )

        updated_contact = await update(contact_id, body_data, user_id, self.session)
        self.assertEqual(updated_contact.email, new_email)
        self.assertTrue(self.session.commit.called)

    async def test_remove_contact(self):
        contact_id = 1
        user_id = self.user.id
        email = "test@example.com"
        contact = Contact(id=contact_id, email=email, user_id=user_id)

        with patch("src.repository.contacts.get_contact_by_id") as mock_get_contact_by_id:
            mock_get_contact_by_id.return_value = contact

            result = await remove(contact_id, user_id, self.session)

        # get_contact_by_id було викликано з правильними параметрами
        mock_get_contact_by_id.assert_called_once_with(contact_id, user_id, self.session)
        # сесія була викликана з commit
        self.assertTrue(self.session.commit.called)
        # remove було викликано з очікуваними параметрами
        self.session.delete.assert_called_once_with(contact)
        # результат є очікуваним значенням
        self.assertEqual(result, contact)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await get_contacts(self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contact_id = 1
        user_id = self.user.id
        expected_contact = Contact(id=contact_id, user_id=user_id)

        self.session.query(Contact).filter_by(id=contact_id, user_id=user_id).first.return_value = expected_contact
        result = await get_contact_by_id(contact_id, user_id, self.session)
        self.assertEqual(result, expected_contact)

    async def test_get_contact_by_lastname_and_email(self):
        contact_id = 1
        user_id = self.user.id
        lastname = 'Someone'
        email = "test@example.com"
        expected_contact = Contact(id=contact_id, user_id=user_id, lastname=lastname, email=email)

        self.session.query(Contact).filter_by(lastname=lastname, email=email, user_id=user_id).first.return_value = expected_contact
        result = await get_contact_by_id(contact_id, user_id, self.session)
        self.assertEqual(result, expected_contact)
    
    async def test_get_contact_by_lastname(self):
        contact_id = 1
        user_id = self.user.id
        lastname = 'Someone'
        expected_contact = Contact(id=contact_id, user_id=user_id, lastname=lastname)

        self.session.query(Contact).filter_by(lastname=lastname, user_id=user_id).first.return_value = expected_contact
        result = await get_contact_by_id(contact_id, user_id, self.session)
        self.assertEqual(result, expected_contact)

    async def test_get_contact_by_firstname(self):
        contact_id = 1
        user_id = self.user.id
        firstname = 'Someone'
        expected_contact = Contact(id=contact_id, user_id=user_id, firstname=firstname)

        self.session.query(Contact).filter_by(firstname=firstname, user_id=user_id).first.return_value = expected_contact
        result = await get_contact_by_id(contact_id, user_id, self.session)
        self.assertEqual(result, expected_contact)

    async def test_get_contact_by_email(self):
        contact_id = 1
        user_id = self.user.id
        email = "test@example.com"
        expected_contact = Contact(id=contact_id, user_id=user_id, email=email)

        self.session.query(Contact).filter_by(email=email, user_id=user_id).first.return_value = expected_contact
        result = await get_contact_by_id(contact_id, user_id, self.session)
        self.assertEqual(result, expected_contact)

    async def test_get_birthdays(self):
        contact_id = 1
        user_id = self.user.id
        birth = date(1990, 1, 1)
        start_date = date(1985, 1, 1)
        end_date = date(2000, 1, 1)
        expected_contact = Contact(id=contact_id, user_id=user_id, birth=birth)

        self.session.query(Contact).filter_by(birth >= start_date, birth <= end_date, user_id=user_id).first.return_value = expected_contact
        result = await get_contact_by_id(contact_id, user_id, self.session)
        self.assertEqual(result, expected_contact)


if __name__ == '__main__':
    unittest.main()