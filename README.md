# Capstone-1

# RecipeBox

## Overview

- Allows a user to search for recipes and organize them in a virtual cookbook  
- Targeted toward any demographic, but particularly people interested in cooking and keeping track of recipes
- Once logged in, users can create their own recipes or save recipes from their search
- A basic search will produce recipe images and titles with a link to the full recipe on an external website
- Once saved, a recipe will display all recipe information available from the following: title, image, url, calories, total yield, ingredients, and cook time
- Site is hosted at the following URL: https://ciro-blogly.onrender.com

## Schema 

- Table for users containing username, password, first name, last name and email  
- Table for recipes containing recipe title, image, URL, yield, calories, ingredients, time, and username
- Tables are joined on username

## Potential API issues

- Error handling if API is down or doesn't return a 200 response code
- Some recipes don't contain correct images or are missing data

## Functionality/User Flow

- User starts by seeing a homepage with a text box where he/she can enter the name of a dish or an ingredient to search for recipes
- User can filter the search by clicking checkboxes for high protein, low-fat or low-carb
- An alert will let the user know if the recipe search did not yield any results
- Once the search button is clicked, cards with 12 recipes will immediately be loaded and the screen will slide down to view the cards
- In the navbar, users will have the options to register for a new account or to log in
- Once logged in, a user is then redirected to his/her personal recipe page with options to view individual saved recipes or create a personal recipe
- Individual recipe pages contain all of the recipe data that is available from the schema. A default image is provided if the recipe doesn't provide one
- Additionally, recipes can be deleted from a user's personal recipe page
- Once logged in, a new button appears next to each recipe when searched allowing for the user to save the recipe

## Data
- Edamam API contains information on recipes based on ingredient and nutrients
- All of the information outlined in the schema for recipes is available on Edamam
- Link to API - https://developer.edamam.com/edamam-docs-recipe-api

## Technology Stack
- Site was created using Python & Flask for the back end and Javascript for the front end
- Additional dependencies include Bootstrap, SQLAlchemy, WTForms & Axios