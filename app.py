"""Capstone 1 Project"""

from flask import Flask, request, redirect, jsonify, json, render_template, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Recipe
from forms import RegisterForm, LoginForm, UserForm, RecipeForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import requests, pdb
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "SECRET!")
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

EDAMAM_KEY = os.environ.get('API_KEY', os.getenv('EDAMAM_KEY'))
EDAMAM_ID= os.environ.get('API_ID', os.getenv('EDAMAM_ID'))

@app.route("/")
def home():
    """Direct to Home Page"""
    return render_template("home.html")

@app.route("/recipes", methods=['GET', 'POST'])
def show_recipes():
    """Search for recipe based on search results and filters and return JSON""" 
    try:
        search = request.get_json()['params']
        filtered = request.get_json()['filter']
        
        # Base URL for v2 API
        base_url = "https://api.edamam.com/api/recipes/v2"
        
        # Build query parameters
        params = {
            'type': 'public',
            'q': search,
            'app_id': EDAMAM_ID,
            'app_key': EDAMAM_KEY
        }
        
        # Add diet filters if any
        if filtered:
            params['diet'] = ','.join(filtered)
        
        # Make the API request
        res = requests.get(base_url, params=params)
        res.raise_for_status()  # Raise an error for bad status codes
        
        recipe_data = res.json()
        return jsonify(recipe_data)
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return jsonify({"error": "Failed to fetch recipes. Please try again later."}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

@app.route("/register", methods=['GET', 'POST'])
def register_user():
    """Register new user with data from form"""
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
    """Authenticate and login user or redirect if authentication fails"""
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
    """Show info on current user"""
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

@app.route("/recipes/new", methods=['GET', 'POST'])
def create_recipe():
    """Create new recipe"""
    if 'username' not in session:
        flash("Please log in to view this page", "danger")
        return redirect('/login')

    form = RecipeForm()
    username = session['username']

    if form.validate_on_submit():
        title = form.title.data
        image = form.image.data
        calories = form.calories.data
        total_yield = form.total_yield.data
        time = form.time.data
        ingredients = form.ingredients.data

        user = User.query.get_or_404(username)
        recipe = Recipe(title=title, image=image, url=None, calories=calories, total_yield=total_yield, time=time, ingredients=ingredients, username=username)
        db.session.add(recipe)
        db.session.commit()

        flash('Recipe added', "success")
        return redirect(f"/users/{username}")
    return render_template("new_recipe.html", form=form)


@app.route("/logout")
def logout():
    session.pop('username')
    flash('You are now logged out', "success")
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))