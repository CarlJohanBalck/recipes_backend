from datetime import datetime, date, timedelta
from tkinter import INSERT
from flask import Flask, request
from flask_cors import CORS
import socket
import random
import gkeepapi
import json
import mysql.connector as mariadb;
from decimal import *
import re


from config import (
	IP_ADDRESS,
	RECIPES_PORT,
	KEEP_EMAIL,
	KEEP_PASSWORD,
	DB_USER,
	DB_PASSWORD,
	DB_HOST,
	DB_PORT,
	DB_DATABASE,
	DB_QUERY_GET_ALL,
	DB_QUERY_GET_ALL_INGREDIENTS,
	DB_QUERY_GET_ALL_UNITS,
	DB_QUERY_GET_DISH_LIST,
	DB_QUERY_INGREDIENTS_1,
	DB_QUERY_INGREDIENTS_2,
	DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_1,
	DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_2,
	DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_3,
	DB_QUERY_ADD_RECIPE,
	DB_QUERY_ADD_INGREDIENT,
	DB_QUERY_ADD_RECIPE_INSTRUCTIONS_NULL,
	DB_QUERY_ADD_RECIPE_URL_NULL
)
hostname = socket.gethostname()
isOnWalk = False

hasBeenGiven = False

ip_address = IP_ADDRESS
app = Flask(__name__)
CORS(app)

print('\n Hostname of your Pi: ' + hostname)
print(' IP address of Pi: ' + ip_address)

@app.route('/Siri/MatlistaTest', methods=['POST'])
def MatlistaTest():
		data = request.json
		numberOfDishes = data.get("numberOfDishes")
		keep = gkeepapi.Keep()
		keep.login(KEEP_EMAIL, KEEP_PASSWORD)
		
		try:
			conn = mariadb.connect(
				user=DB_USER,
				password=DB_PASSWORD,
				host=DB_HOST,
				port=DB_PORT,
				database=DB_DATABASE
		)
		except mariadb.Error as e:
			print(f"Error connecting to MariaDB Platform: {e}")
			sys.exit(1)
		
		# # Get Cursor
		cur = conn.cursor()
		newGroceryList = []

		allRecipes = get_all_recipes(cur, DB_QUERY_GET_ALL)
		
		n = 0

		r = range(n+1, len(allRecipes))

		data = random.sample(r, numberOfDishes)

		newDishList = []
		
		ingredients = ingredients_for_recipe(cur, data)
		for i in range (len(ingredients)):
			groceryRow = str(ingredients[i][0]) + " " + str(ingredients[i][1]).replace('None', '') + " " + str(ingredients[i][2])
			newGroceryList.append(groceryRow)
	
		newDishList = dishListForSelectedRecipes(cur, data)


		
		return json.dumps(list(newDishList))

@app.route('/Siri/Recipes', methods=['GET'])
def getRecepies():
	try:
		conn = mariadb.connect(
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT,
			database=DB_DATABASE
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()
	data = get_all_recipes(cur, DB_QUERY_GET_ALL)




	return json.dumps(list(data))

@app.route('/Siri/Ingredients', methods=['GET'])
def getIngredients():
	try:
		conn = mariadb.connect(
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT,
			database=DB_DATABASE
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()
	data = get_all_ingredients(cur, DB_QUERY_GET_ALL_INGREDIENTS)

	return json.dumps(list(data))

@app.route('/Siri/Units', methods=['GET'])
def getUnits():
	try:
		conn = mariadb.connect(
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT,
			database=DB_DATABASE
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()
	data = get_all_ingredients(cur, DB_QUERY_GET_ALL_UNITS)

	return json.dumps(list(data))


@app.route('/Siri/RecipesBasedOnIngredients', methods=['GET'])
def getRecepiesBasedOnIngredients():
	try:
		conn = mariadb.connect(
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT,
			database=DB_DATABASE
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()

	data = recipes_for_ingredinets(cur, [15])


	return json.dumps(list(data))

def instructions_for_book_recipes(cursor, selectedRecipes):
	try:
		selectedRecipesParsed = str(tuple(selectedRecipes))
		if len(selectedRecipes) == 1:
			selectedRecipesParsed = selectedRecipesParsed.replace(',', "")
		statement = "SELECT instructions, name from recipe where id in " + selectedRecipesParsed + " and instructions IS NOT NULL"
		instructionList = []
		cursor.execute(statement)

		for (instruction) in cursor:
			instructionList.append(instruction)
		return instructionList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")

def ingredients_for_recipe(cursor, selectedRecipes):
	try:
		selectedRecipesParsed = str(tuple(selectedRecipes))
		if len(selectedRecipes) == 1:
			selectedRecipesParsed = selectedRecipesParsed.replace(',', "")
		statement = DB_QUERY_INGREDIENTS_1 + " " + selectedRecipesParsed + " " + DB_QUERY_INGREDIENTS_2
		ingredientList = []
		cursor.execute(statement)

		for (ingredients) in cursor:
			ingredientList.append(ingredients)
		return ingredientList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")

def add_recipe(cursor, recipeInfo):
	try:
		recipeID = str(recipeInfo.get("recipe_id"))
		recipeName = str(recipeInfo.get("recipe_name"))
		recipeUrl = str(recipeInfo.get("recipe_url"))
		recipeWeekend = str(recipeInfo.get("recipe_weekend"))
		recipeImageUrl = str(recipeInfo.get("recipe_image_url"))
		recipeInstructions = str(recipeInfo.get("recipe_instructions"))

		if recipeInstructions == "None":
			values = (recipeID, recipeName, recipeUrl, recipeWeekend, recipeImageUrl)
			query = (DB_QUERY_ADD_RECIPE_INSTRUCTIONS_NULL)
			cursor.execute(query, values)
		
		elif recipeUrl == "None": 
			query = (DB_QUERY_ADD_RECIPE_URL_NULL)
			values = (recipeID, recipeName, recipeWeekend, recipeImageUrl, recipeInstructions)
			cursor.execute(query, values)

		else:
			query = (DB_QUERY_ADD_RECIPE)
			values = (recipeID, recipeName, recipeUrl, recipeWeekend, recipeImageUrl, recipeInstructions)
			cursor.execute(query, values)

	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")


def add_ingredient(cursor, ingredientInfo):
	try:
		recipe_ingredient_id = str(ingredientInfo.get("recipe_ingredient_id"))
		recipe_id = str(ingredientInfo.get("recipe_id"))
		amount = str(ingredientInfo.get("amount"))
		unit = str(ingredientInfo.get("unit"))
		ingredient = str(ingredientInfo.get("ingredient"))


		query = (DB_QUERY_ADD_INGREDIENT)
		values = (recipe_ingredient_id, recipe_id, amount, unit, ingredient)
		cursor.execute(query, values)

	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")

def recipes_for_ingredinets(cursor, selectedIngredients):
	try:
		selectedIngredientsParsed = str(tuple(selectedIngredients))
		print("SELECTED INGREDIENTS PARSED.----", selectedIngredientsParsed)
		if len(selectedIngredients) == 1:
			selectedIngredientsParsed = selectedIngredientsParsed.replace(',', "")
		statement_1 = DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_1
		statement_2 = DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_2
		statement_3 = DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_3

		totalStatement = statement_1 + selectedIngredientsParsed + statement_2 + selectedIngredientsParsed + statement_3

		print("TOTAL STATEMENT-----", totalStatement)

		ingredientList = []
		cursor.execute(totalStatement)

		for (ingredients) in cursor:
			ingredientList.append(ingredients)
		return ingredientList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")

def dishListForSelectedRecipes(cursor, selectedRecipes):
	try:
		selectedRecipesParsed = str(tuple(selectedRecipes))
		if len(selectedRecipes) == 1:
			selectedRecipesParsed = selectedRecipesParsed.replace(',', "")
		statement = DB_QUERY_GET_DISH_LIST + " " + selectedRecipesParsed;
		dishList = []
		cursor.execute(statement)

		for (dish) in cursor:
			dishList.append(dish)
		return dishList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")


def get_all_recipes(cursor, query):
	try:
		recipeList = []
		cursor.execute(query)
		for (recipe) in cursor:

			recipeList.append(recipe)
		return recipeList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")

def get_all_ingredients(cursor, query):
	try:
		ingredientsList = []
		cursor.execute(query)
		for (ingredient) in cursor:
			ingredientsList.append(ingredient)
		return ingredientsList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")




@app.route('/Siri/ReactRecipes', methods=['POST'])
def ReactRecepies():
		request_data = request.json
		recipes = request_data.get("idList")
		keep = gkeepapi.Keep()
		keep.login(KEEP_EMAIL, KEEP_PASSWORD)
		
		try:
			conn = mariadb.connect(
				user=DB_USER,
				password=DB_PASSWORD,
				host=DB_HOST,
				port=DB_PORT,
				database=DB_DATABASE
		)
		except mariadb.Error as e:
			print(f"Error connecting to MariaDB Platform: {e}")
			sys.exit(1)
		
		# # Get Cursor
		cur = conn.cursor()
		newGroceryList = []
		

		ingredients = ingredients_for_recipe(cur, recipes)
		instructions = instructions_for_book_recipes(cur, recipes)

		for i in range (len(ingredients)):
			groceryRow = str(ingredients[i][0]) + " " + str(ingredients[i][1]).replace('None', '') + " " + str(ingredients[i][2])
			newGroceryList.append(groceryRow)
		dishes = dishListForSelectedRecipes(cur, recipes)
		dishList = []
		newDishList = []
		for i in range (len(dishes)):
			dishRow = str(dishes[i][0]) + " " + str(dishes[i][1]).replace('None', '')
			newDishList.append(dishRow)
		for i in range(len(newDishList)):
			dishList.append(newDishList[i])
			dishList.append("False")
	
		dish_list_tuple = [x for x in zip(*[iter(dishList)]*2)]

		testList = []

		for i in range(len(newGroceryList)):
			testList.append(newGroceryList[i])
			testList.append("False")
		grocery_list_tuple= [x for x in zip(*[iter(testList)]*2)]


		now = datetime.now() # current date and time	
		date_time = now.strftime("%d/%m/%Y")	

	
		gnotes = keep.all()
		string_ingredients = 'Inköpslista PI - ' + date_time
		string_dishes = 'Matlista PI - ' + date_time

		for i in range(len(instructions)):
			keep.createNote(instructions[i][1], instructions[i][0])

		for i in range(len(gnotes)):
			if gnotes[i].title == string_ingredients or gnotes[i].title == string_dishes:
				gnotes[i].delete()
		keep.createList('Inköpslista PI - ' + date_time, 
			grocery_list_tuple
		)
		keep.createList('Matlista PI - ' + date_time, 
			dish_list_tuple
		)

		keep.sync()
			
		return json.dumps(list(grocery_list_tuple))


@app.route('/Siri/AddRecipe', methods=['POST'])
def addRecipe():

	request_data = request.json

	recipeInfo = request_data.get("recipeInfo")
	print("RECIPES: ", recipeInfo)


	try:
		conn = mariadb.connect(
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT,
			database=DB_DATABASE
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()

	data = add_recipe(cur, recipeInfo)
	conn.commit()

	return json.dumps(data)

@app.route('/Siri/AddIngredient', methods=['POST'])
def addIngredient():

	request_data = request.json

	ingredientInfo = request_data.get("ingredientInfo")
	print("INGREDIENTS: ", ingredientInfo)


	try:
		conn = mariadb.connect(
			user=DB_USER,
			password=DB_PASSWORD,
			host=DB_HOST,
			port=DB_PORT,
			database=DB_DATABASE
		)
	except mariadb.Error as e:
		print(f"Error connecting to MariaDB Platform: {e}")

	# Get Cursor
	cur = conn.cursor()

	data = add_ingredient(cur, ingredientInfo)
	conn.commit()

	return json.dumps(data)
	


if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=RECIPES_PORT, use_reloader=True)
	
