"""Capstone 1 Project"""

from flask import Flask, request, redirect, jsonify, json, render_template, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Recipe
from forms import RegisterForm, LoginForm, UserForm
from sqlalchemy.exc import IntegrityError
import requests, pdb
import os
from dotenv import load_dotenv
from boto.s3.connection import S3Connection

load_dotenv()

EDAMAM_KEY = S3Connection(os.environ['API_KEY'], os.getenv('EDAMAM_KEY'))
EDAMAM_ID= S3Connection(os.environ['API_ID'], os.getenv('EDAMAM_ID'))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///recipebox-capstone')
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
    filtered = request.get_json()['filter']

    if filtered == []:
        res = requests.get(f"https://api.edamam.com/search?q={search}&app_id={EDAMAM_ID}&app_key={EDAMAM_KEY}&to=12")
        recipe_data = res.json()
        return jsonify(recipe_data)
    else:
        query = f"https://api.edamam.com/search?q={search}&app_id={EDAMAM_ID}&app_key={EDAMAM_KEY}&to=12"
        for spec in filtered:
            addition = f"&diet={spec}"
            query += addition
        res = requests.get(query)
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
    url = recipe_data['url']
    calories = recipe_data['calories']
    total_yield = recipe_data['yield']
    time = recipe_data['time']
    ingredients = recipe_data['ingredients']

    recipe = Recipe(title=title, image=image, url=url, calories=calories, total_yield=total_yield, time=time, ingredients=ingredients, username=username)
    db.session.add(recipe)
    db.session.commit()

    return  jsonify({ 'message': "Recipe saved!" })

@app.route("/recipes/<int:recipe_id>")
def show_recipe(recipe_id):
    """Detail page for a single recipe"""

    recipe = Recipe.query.get_or_404(recipe_id)
    
    ingredients = recipe.ingredients.split(',')
    ingredients = [item.replace('"', '') for item in ingredients]
    ingredients = [item.replace('{', '') for item in ingredients]
    ingredients = [item.replace('}', '') for item in ingredients]

    return render_template("recipe_detail.html", recipe=recipe, ingredients=ingredients)

@app.route("/recipes/<recipe_id>/delete", methods=['POST'])
def delete_recipe(recipe_id):
    """Delete a single recipe"""
    if 'username' not in session:
        flash("Please log in to view this page", "danger")
        return redirect('/login')
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    flash("Recipe deleted", "success")
    return redirect(f"/users/{session['username']}")

@app.route("/logout")
def logout():
    session.pop('username')
    flash('You are now logged out', "success")
    return redirect('/')