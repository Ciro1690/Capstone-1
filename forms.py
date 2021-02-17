from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField
from wtforms.validators import InputRequired, Optional

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class UserForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = StringField("Email")

class RecipeForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    image = StringField("Image", validators=[Optional()])
    calories = IntegerField("calories", validators=[Optional()])
    total_yield = FloatField("Total Yield", validators=[Optional()])
    time = FloatField("Time", validators=[Optional()])
    ingredients = StringField("Ingredients", validators=[Optional()])