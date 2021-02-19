from unittest import TestCase

from app import app
from models import db, User, Recipe

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone-test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

USER_DATA = {
    "username": "testuser",
    "password": "12345",
    "email": "test@email.com",
    "first_name": "test",
    "last_name": "user"
}

RECIPE_DATA = {
    "title": "Chicken", 
    "ingredients": "chicken, potatoes"
}

class RecipeViewsTestCase(TestCase):
    """Tests for views for Recipes."""

    def setUp(self):
        """Add sample recipe."""

        User.query.delete()

        user = User(**USER_DATA)
        db.session.add(user)
        db.session.commit()

        self.user = user

        Recipe.query.delete()

        recipe = Recipe(**RECIPE_DATA)
        db.session.add(recipe)
        db.session.commit()

        self.recipe_id = recipe.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()


    def test_show_post(self):
        with app.test_client() as client:
            resp = client.get(f"/recipes/{self.recipe_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Chicken', html)

    def test_add_post(self):
        with app.test_client() as client:
            d = {"title": "Beans", "ingredients": "Beans"}
            resp = client.post("/recipes/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

    def test_delete_recipe(self):
        with app.test_client() as client:
            resp = client.post("recipes/1/delete", follow_redirects=True)
            recipe = client.get("recipes/1")
            html = resp.get_data(as_text=True)

            self.assertEqual(recipe.status_code, 404)
            self.assertNotEqual("Chicken", html)