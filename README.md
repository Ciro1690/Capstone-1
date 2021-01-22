# Capstone-1

## Personal Cookbook App

-Allows a user to search for recipes and organize them in a virtual cookbook  
-Targeted toward any demographic, but particularly people interested in cooking and keeping track of recipes

## Schema 

-Table for users containing username, password, first name, last name and email  
-Table for recipes containing recipe title, image, instructions, dish type, cuisine type, ingredients, cook time, serving quantity, dietary information, notes

## Potential API issues

-Error handling if API is down or doesn't return a 200 response code

## Functionality/User Flow

-User would start by seeing a homepage with login/register options
-User would then be redirected to his/her personal recipe page with options to view all recipes, add a personal recipe or search for a new recipe
-There would be options to view recipes based on different criteria, such as cuisine type or cook time
-Additionally, I am considering implementing nutrional facts about recipes and a shopping list functionality

## Data
- Spoonacular API contains information on recipes based on ingredient, nutrients and price
- All of the information outlined in the schema for recipes is available on Spoonacular
