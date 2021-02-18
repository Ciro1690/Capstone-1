from unittest import TestCase

from app import app
from models import db, User, connect_db, Recipe
from sqlalchemy import exc

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone-test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

db.drop_all()
db.create_all()

USER_DATA = {
    "username": "testuser",
    "password": "12345",
    "email": "test@email.com",
    "first_name": "test",
    "last_name": "user"
}

class UserViewsTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add sample user."""

        User.query.delete()

        user = User(**USER_DATA)
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_show_homepage(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Recipe Box', html)

    def test_list_user(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = self.user.username

            url = f"/users/{self.user.username}"
            res = client.get(url)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('testuser', html)

    def test_logout_user(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = self.user.username

            url = "/logout"
            res = client.get((url), follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertNotIn('testuser', html)
            self.assertIn('You are now logged out', html)
