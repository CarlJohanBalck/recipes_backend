from datetime import datetime, date, timedelta
from flask import Flask, request
from flask_cors import CORS
import socket
import random
import gkeepapi
import json
import mysql.connector as mariadb;
from decimal import *



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
	DB_QUERY_GET_DISH_LIST,
	DB_QUERY_INGREDIENTS_1,
	DB_QUERY_INGREDIENTS_2
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

@app.route('/Siri/Recepies', methods=['GET'])
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
		sys.exit(1)

	# Get Cursor
	cur = conn.cursor()
	data = get_all_recipes(cur, DB_QUERY_GET_ALL)




	return json.dumps(list(data))



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

def dishListForSelectedRecipes(cursor, selectedRecipes):
	try:
		selectedRecipes = str(tuple(selectedRecipes))
		statement = DB_QUERY_GET_DISH_LIST + " " + selectedRecipes;
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




@app.route('/Siri/ReactRecepies', methods=['POST'])
def ReactRecepies():

		request_data = request.json
		recepies = request_data.get("idList")

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
		
		ingredients = ingredients_for_recipe(cur, recepies)
		for i in range (len(ingredients)):
			groceryRow = str(ingredients[i][0]) + " " + str(ingredients[i][1]).replace('None', '') + " " + str(ingredients[i][2])
			newGroceryList.append(groceryRow)
		dishes = dishListForSelectedRecipes(cur, recepies)
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


if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=RECIPES_PORT, use_reloader=True)
	
