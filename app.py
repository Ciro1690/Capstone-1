"""Capstone 1 Project"""

from flask import Flask, request, redirect, jsonify, json, render_template, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Recipe
from forms import RegisterForm, LoginForm, UserForm, RecipeForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import requests, pdb
import os
import logging
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlencode
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Log environment variables (without sensitive values)
logger.info("Starting application initialization")
logger.info(f"Database URL configured: {'Yes' if os.environ.get('DATABASE_URL') else 'No'}")
logger.info(f"Secret Key configured: {'Yes' if os.environ.get('SECRET_KEY') else 'No'}")
logger.info(f"Edamam credentials configured: {'Yes' if os.environ.get('EDAMAM_KEY') and os.environ.get('EDAMAM_ID') else 'No'}")

# Configure database
try:
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Parse the URL
    parsed = urlparse(database_url)
    
    # Convert postgres:// to postgresql://
    if parsed.scheme == 'postgres':
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Parse existing query parameters
    query_params = parse_qs(parsed.query)
    
    # Add required Supabase parameters
    query_params.update({
        'sslmode': ['require'],
        'connect_timeout': ['30'],
        'application_name': ['recipebox'],
        'options': ['-c timezone=UTC'],
        'keepalives': ['1'],
        'keepalives_idle': ['30'],
        'keepalives_interval': ['10'],
        'keepalives_count': ['5']
    })
    
    # Reconstruct the URL with new parameters
    parsed = urlparse(database_url)
    new_query = urlencode(query_params, doseq=True)
    database_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    
    logger.info("Database URL configured successfully")
    logger.info(f"Database host: {parsed.hostname}")
except Exception as e:
    logger.error(f"Failed to configure database URL: {str(e)}")
    raise

try:
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    logger.info("Database connection initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "SECRET!")
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

EDAMAM_KEY = os.environ.get('API_KEY', os.getenv('EDAMAM_KEY'))
EDAMAM_ID= os.environ.get('API_ID', os.getenv('EDAMAM_ID'))

def test_db_connection():
    """Test database connection with retries"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.engine.connect()
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All database connection attempts failed")
                return False

@app.route("/health")
def health_check():
    """Health check endpoint"""
    try:
        db_status = test_db_connection()
        return jsonify({
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

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