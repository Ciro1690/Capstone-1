"""Capstone 1 Project"""

from flask import Flask, request, redirect, jsonify, json, render_template, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Recipe, Grocery_list
from forms import RegisterForm, LoginForm, UserForm
from sqlalchemy.exc import IntegrityError
from secrets import EDAMAM_ID, EDAMAM_KEY
import requests, ast
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///capstone-1')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "SECRET!")
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route("/")
def home():
    """Direct to Home Page"""
    return render_template("home.html")

@app.route("/recipes", methods=['GET', 'POST'])
def show_recipes():
    search = request.get_json()['params']

    res = requests.get(f"https://api.edamam.com/search?q={search}&app_id={EDAMAM_ID}&app_key={EDAMAM_KEY}&to=12")
    recipe_data = res.json()
    return jsonify(recipe_data)

@app.route("/register", methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username already taken")
            return render_template("register.html", form=form)

        session['username'] = new_user.username
        flash("Created new account", "success")
        return redirect('/')

    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome {user.first_name}", "success")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)

@app.route("/users/<username>")
def user_info(username):
    if session['username'] != username:
        flash("Invalid credentials", "danger")
        return redirect('/')
    
    user = User.query.get_or_404(username)
    return render_template("user_info.html", user=user)

@app.route("/users/<username>/recipes/new", methods=['GET','POST'])
def save_recipe(username):
    """Save recipe to database"""
    if 'username' not in session:
        flash("Please login first", "danger")
        return redirect('/')

    recipe_data = request.get_json()['params']

    title = recipe_data['title']
    image = recipe_data['image']
    calories = recipe_data['calories']
    total_yield = recipe_data['yield']
    time = recipe_data['time']
    ingredients = recipe_data['ingredients']

    recipe = Recipe(title=title, image=image, calories=calories, total_yield=total_yield, time=time, ingredients=ingredients, username=username)
    db.session.add(recipe)
    db.session.commit()

    flash('Recipe added', 'success')
    return redirect(f'/users/{username}')

@app.route("/recipes/<int:recipe_id>")
def show_recipe(recipe_id):
    """Detail page for a single recipe"""

    recipe = Recipe.query.get_or_404(recipe_id)
    
    ingredients = recipe.ingredients.split(',')
    ingredients = [item.replace('"', '') for item in ingredients]
    ingredients = [item.replace('{', '') for item in ingredients]
    ingredients = [item.replace('}', '') for item in ingredients]

    return render_template("recipe_detail.html", recipe=recipe, ingredients=ingredients)


@app.route("/logout")
def logout():
    session.pop('username')
    flash('You are now logged out', "success")
    return redirect('/')