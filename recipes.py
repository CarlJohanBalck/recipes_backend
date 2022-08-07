import os
import time
from datetime import datetime, date, timedelta
from flask import Flask, request
from flask_cors import CORS
import socket
import time
from timer import Timer
import configparser
import calendar
from sense_hat import SenseHat
import random
import gkeepapi
import re
import collections
from icalendar import Calendar, Event, vCalAddress, vText
from pathlib import Path
import os
import pytz
import json
import mysql.connector as mariadb;
from decimal import *
from threading import Thread


from config import (
	IP_ADDRESS,
	PORT,
	RECEPIES,
	KEEP_EMAIL,
	KEEP_PASSWORD,
	BREAD_CATEGORY,
	DAIRY_CATEGORY,
	SPICES_CATEGORY,
	FROZEN_CATEGORY,
	VEGETABLES_CATEGORY,
	CHEESE_CATEGORY,
	PASTA_CATEGORY,
	CHECKOUT_CATEGORY,
	DB_USER,
	DB_PASSWORD,
	DB_HOST,
	DB_PORT,
	DB_DATABASE,
	DB_QUERY_GET_ALL,
	DB_QUERY_INGREDIENTS
)
hostname = socket.gethostname()
isOnWalk = False

hasBeenGiven = False

ip_address = IP_ADDRESS
app = Flask(__name__)
CORS(app)

print('\n Hostname of your Pi: ' + hostname)
print(' IP address of Pi: ' + ip_address)


@app.route('/Siri/Recepies', methods=['GET'])
def getRecepies():
	# recepies = RECEPIES
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




@app.route('/Siri/Matlista', methods=['GET'])
def Matlista():	

	recept = RECEPIES

	weekday = 3
	weekend = 2
	nbrDishesPerWeek = weekday + weekend
	nbrRecepies = len(recept)
	final_recepie = []
	# keep = gkeepapi.Keep()
	# success = keep.login(KEEP_EMAIL, KEEP_PASSWORD)
	dishList = []
	dishListTmp = []
	groceryList = []
	weekday_list = []
	weekend_list = []

	for i in range (len(recept)):
		if recept[i][0][-1] == "h":
			weekend_list.append(recept[i])
		elif recept[i][0][-1] == "v":
			weekday_list.append(recept[i])

	randomlist_weekday = random.sample(range(len(weekday_list)), weekday)
	randomlist_weekend = random.sample(range(len(weekend_list)), weekend)

	for i in range(0,weekday):
			final_recepie.append(weekday_list[randomlist_weekday[i]])
	for i in range(0,weekend):
			final_recepie.append(weekend_list[randomlist_weekend[i]])
	

	for i in range(nbrDishesPerWeek):
		dishList.append(str(final_recepie[i][0][:-2]))
		dishList.append("False")
		dishListTmp.append(str(final_recepie[i][0]))
	

	for i in range(nbrDishesPerWeek):
		for j in range(len(final_recepie[i])-1):
			groceryList.append(str(final_recepie[i][j+1]))

	newListBread = []
	newListDairies = []
	newListSpices = []
	newListFrozen = []
	newListVegos = []
	newListCheese = []
	newListPasta = []
	newListCheckout = []
	newOtherList = []
	print("GROCERY LIST LENGTH: ", len(groceryList))

	## sort grocerylist into sub-category grocerylists

	for x in groceryList:
		if any(word in x.lower() for word in BREAD_CATEGORY):
			newListBread.append(x)
		elif any(word in x.lower() for word in DAIRY_CATEGORY):
			newListDairies.append(x)
		elif any(word in x.lower() for word in SPICES_CATEGORY):
			newListSpices.append(x)
		elif any(word in x.lower() for word in FROZEN_CATEGORY):
			newListFrozen.append(x)
		elif any(word in x.lower() for word in VEGETABLES_CATEGORY):
			newListVegos.append(x)
		elif any(word in x.lower() for word in CHEESE_CATEGORY):
			newListCheese.append(x)
		elif any(word in x.lower() for word in PASTA_CATEGORY):
			newListPasta.append(x)
		elif any(word in x.lower() for word in CHECKOUT_CATEGORY):
			newListCheckout.append(x)
		else:
			newOtherList.append(x)
	tmpList = []

	for x in newListBread:
		tmpList.append(x)
	for x in newListDairies:
		tmpList.append(x)
	for x in newListSpices:
		tmpList.append(x)
	for x in newListFrozen:
		tmpList.append(x)
	for x in newListVegos:
		tmpList.append(x)
	for x in newListCheese:
		tmpList.append(x)
	for x in newListPasta:
		tmpList.append(x)
	for x in newListCheckout:
		tmpList.append(x)
	for x in newOtherList:
		tmpList.append(x)

	duplicates = [item for item, count in collections.Counter(tmpList).items() if count > 1]

	duplicatesIndexList = []
	for i in range(len(duplicates)):
		duplicatesIndexList.append(indices(tmpList, duplicates[i]))

	numberOfDuplicatesList = []
	indexToRemoveList = []
	firstIndexList = []

	for i in range(len(duplicatesIndexList)):
		numberOfDuplicatesList.append(len(duplicatesIndexList[i]))
		indexToRemoveList.append(duplicatesIndexList[i][1:])
		firstIndexList.append(duplicatesIndexList[i][0])

	for i in range(len(firstIndexList)):
		tmpList[firstIndexList[i]] = str(numberOfDuplicatesList[i]) + " x " + str(tmpList[firstIndexList[i]])
	
	for i in range(len(duplicates)):
		tmpList.remove(duplicates[i])
	
	finalList = []
	for x in tmpList:
		finalList.append(x)
		finalList.append("False")


	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")	
	my_date = date.today()
	dishDays = []

	for i in range(nbrDishesPerWeek):
		td = timedelta(days=i+1)
		dishDayTmp = now + td
		dishDay = dishDayTmp.strftime("%d/%m/%Y")	
		dishDays.append(str(dishDay))

	dishDayList = list(zip(dishDays, dishListTmp))
	#init the calendar
	cal = Calendar()
	# Some properties are required to be compliant
	cal.add('prodid', '-//My calendar product//example.com//')
	cal.add('version', '2.0')

	for i in range(len(dishDayList)):
		# Add subcomponents
		event = Event()
		t = 0
		n = 1 # N. . .
		dishes = [x[n] for x in dishDayList]
		days = [x[t] for x in dishDayList]
		dateTmp = [int(d) for d in str(days[i]).split('/') if d.isdigit()]
		event.add('summary', dishes[i])
		event.add('dtstart', datetime(dateTmp[2], dateTmp[1], dateTmp[0], 16, 0, 0, tzinfo=pytz.utc))
		event.add('dtend', datetime(dateTmp[2], dateTmp[1], dateTmp[0], 17, 0, 0, tzinfo=pytz.utc))
		cal.add_component(event)
	#Write to disk
	directory = Path.cwd() / 'DishListCal'
	try:
   		directory.mkdir(parents=True, exist_ok=True)
	except FileExistsError:
   		print("Folder already exists")
	else:
   		print("Folder was created")
 
	f = open(os.path.join(directory, 'dishlist.ics'), 'wb')
	f.write(cal.to_ical())
	f.close()

	weekday = calendar.day_name[my_date.weekday()]
	if(weekday == "Sunday"):
		veckodag = "Söndag"
	if(weekday == "Monday"):
		veckodag = "Måndag"
	if(weekday == "Tuesday"):
		veckodag = "Tisdag"
	if(weekday == "Wednesday"):
		veckodag = "Onsdag"
	if(weekday == "Thursday"):
		veckodag = "Torsdag"
	if(weekday == "Friday"):
		veckodag = "Fredag"
	if(weekday == "Saturday"):
		veckodag = "Lördag"

	match = veckodag + " " + date_time
	
	lst_tuple_grocery = [x for x in zip(*[iter(finalList)]*2)]
	dish_list_tuple = [x for x in zip(*[iter(dishList)]*2)]

	f = open("grocerylist.txt", "w")
	for i in range (len(finalList[::2])):
		f.write(finalList[::2][i] + "\n")
	f.close()
	t = open("dishlist.txt", "w")
	for i in range (len(dishList[::2])):
		t.write(dishList[::2][i] + "\n")
	t.close()

	# gnotes = keep.all()
	# string_ingredients = 'Inköpslista PI - ' + match
	# string_dishes = 'Matlista PI - ' + match
	# for i in range(len(gnotes)):
	# 	if gnotes[i].title == string_ingredients or gnotes[i].title == string_dishes:
	# 		gnotes[i].delete()
	
	# glist = keep.createList('Inköpslista PI - ' + match, 
	# 	lst_tuple_grocery
	# )
	# glist = keep.createList('Matlista PI - ' + match, 
	# 	dish_list_tuple
	# )

	# #Sync up changes
	# keep.sync()
	dishesSummary = ""
	for i in range (len(dishList[::2])):
		dishesSummary += str(re.sub(r"\([^()]*\)","", dishList[::2][i])) + ", "
	return "Denna vecka blir det " + dishesSummary




def get_data(cursor, recepies):
	try:
		statement = "SELECT name, ingredients FROM Recepies WHERE id=%s"
		ingredientList = []
		recepieList = []
		for recepie in recepies:
			data = (recepie,)
			cursor.execute(statement, data)
			for (name, ingredients) in cursor:
				ingredientList.append(ingredients)
				recepieList.append(name)
		return recepieList, ingredientList
		# for (name) in cursor:
		# 	print(f"Successfully retrieved {name}")	
		# 	return {name}
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")



def ingredients_for_recipe(cursor, selectedRecipes):
	try:
		selectedRecipes = str(tuple(selectedRecipes))
		statement = "SELECT ri.amount AS 'Amount', un.name AS 'Unit of Measure', i.name AS 'Ingredient' FROM recipe r JOIN recipe_ingredient ri on r.id = ri.recipe_id JOIN ingredient i on i.id = ri.ingredient_id LEFT OUTER JOIN unit un on un.id = ri.unit_id WHERE r.id in" + " " + selectedRecipes + " " + "ORDER BY i.category_id;"
		ingredientList = []
		cursor.execute(statement)

		for (ingredients) in cursor:
			ingredientList.append(ingredients)
		return ingredientList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")

def dishListForSelectedRecipes(cursor, selectedRecipes):
	try:
		selectedRecipes = str(tuple(selectedRecipes))
		statement = "SELECT r.name AS 'Name', r.url AS 'URL' FROM recipe r WHERE r.id in" + " " + selectedRecipes;
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
		data = request.json
		recepies = data.get("idList")
		
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
		data = ingredients_for_recipe(cur, recepies)
		print("DATA----", data)
		for i in range (len(data)):
			groceryRow = str(data[i][0]) + " " + str(data[i][1]).replace('None', '') + " " + str(data[i][2])
			newGroceryList.append(groceryRow)
		newDishList = dishListForSelectedRecipes(cur, recepies)


		dishList = newDishList
		groceryList = newGroceryList
		
		
		f = open("grocerylist.txt", "w")
		for i in range (len(groceryList)):
			f.write(groceryList[i] + "\n")
		f.close()
		t = open("dishlist.txt", "w")
		for i in range (len(dishList)):
			t.write(str(dishList[i]) + "\n")
		t.close()
		return json.dumps(list(groceryList))


if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=PORT, use_reloader=True)
	
