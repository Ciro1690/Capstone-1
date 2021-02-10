"""Models for Capstone-1."""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    username = db.Column(db.String(20), 
                primary_key=True, unique=True)
 
    password = db.Column(db.Text,
                nullable=False)

    email = db.Column(db.String(50),
                nullable=False, unique=True)

    first_name = db.Column(db.String(30),
                nullable=False)
  
    last_name = db.Column(db.String(30),
                nullable=False)

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

    def get_full_name(self):
        """Get full name"""

        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Show info about user."""

        u = self
        return f"<User {u.username} - {u.first_name} {u.last_name}>"

class Recipe(db.Model):
    """Recipe Table"""

    __tablename__ = "recipes"

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    title = db.Column(db.String,
                    nullable=False)
    image = db.Column(db.String)
    calories = db.Column(db.Integer)
    total_yield = db.Column(db.Float)
    time = db.Column(db.Float)
    ingredients = db.Column(db.String)
    username = db.Column(db.String,
                        db.ForeignKey('users.username'))
    user = db.relationship('User', backref='recipes')

class Grocery_list(db.Model):
    """Grocery list table"""

    __tablename__ = "grocery_lists"
    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    ingredient = db.Column(db.String)
    purchased = db.Column(db.Boolean)
    username = db.Column(db.String,
                        db.ForeignKey('users.username'))
    user = db.relationship('User', backref='grocery_lists')