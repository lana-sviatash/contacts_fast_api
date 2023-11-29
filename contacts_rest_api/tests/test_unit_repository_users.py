import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.schemas import UserBase, UserResponse
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)

class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@test.com")

    async def test_get_user_by_email(self):
        email = "test@example.com"
        expected_user = User(email=email)

        self.session.query(User).filter_by(email=email).first.return_value = expected_user
        result = await get_user_by_email(email, self.session)
        self.assertEqual(result, expected_user)
    
    async def test_create_user(self):
        body_data = UserBase(
            id = 1,
            username = "Someone",
            email = "some@example.com",
            password = '123456'
        )

        body = body_data.model_dump()

        result = await create_user(body, self.session)
        self.assertEqual(result.username, body_data.username)
        self.assertEqual(result.email, body_data.email)
        self.assertEqual(result.password, body_data.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User(id=1, username="Someone", email="test@example.com", password="testpassword")

        self.session.commit = MagicMock()
        new_refresh_token = "new_token"

        await update_token(user, new_refresh_token, self.session)
        self.assertEqual(user.refresh_token, new_refresh_token)
        self.session.commit.assert_called_once()
    
    async def test_confirmed_email(self):
        user_email = "test@example.com"
        user = User(id=1, username="Someone", email=user_email, password="testpassword")

        with unittest.mock.patch("src.repository.users.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = user

            await confirmed_email(user_email, self.session)
        
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()
    
    async def test_update_avatar(self):
        user_email = "test@example.com"
        user = User(id=1, username="Someone", email=user_email, password="testpassword")

        with unittest.mock.patch("src.repository.users.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = user

            new_avatar_url = "new_avatar_url"
            result = await update_avatar(user_email, new_avatar_url, self.session)
        
        self.assertEqual(result, user)
        self.assertEqual(user.avatar, new_avatar_url)
        self.session.commit.assert_called_once()
        

if __name__ == '__main__':
    unittest.main()
