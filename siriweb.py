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

@app.route('/Siri/Senast', methods=['GET'])
def LiloSenast():
	config = configparser.ConfigParser()
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")	

	my_date = date.today()
	weekday = calendar.day_name[my_date.weekday()]

	config.read('lastDate.ini')
	if(config['DEFAULT']['LAST_DATE'] == '""' or not config['DEFAULT']['LAST_DATE']):
		return "Hittade inget senast datum"

	return "Lilo fick kortison senast" + " " + config['DEFAULT']['LAST_DATE']


def indices(lst, item):
	return [i for i, x in enumerate(lst) if x == item]

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
	# cur.execute("SELECT name, id from Recepies")

	selectedRecepies = [1, 2, 3]
	result = get_selected_recipe_db(cur, selectedRecepies)

	all_recipe_result = get_all_recipe(cur, DB_QUERY_GET_ALL)
	recipeNameList = []
	print("ALL RECIPE RESULT: ", all_recipe_result)
	# for i in range (len(all_recipe_result)):
	# 	recipeNameList.append(all_recipe_result[i][1])
	
	# # print("RECIPE NAME LIST: ", recipeNameList)
	# # print("RESULT-----: ", all_recipe_result[0][1])


	database_recepie_names = []
	
	return json.dumps(list(all_recipe_result))

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

@app.route('/Siri/AntalPromenader', methods=['GET'])
def LiloAntalPromendater():
	config = configparser.ConfigParser()

	config.read('walks.ini')

	print("LAST DATE: ", config['DEFAULT']['NBR_WALKS']) 
	nbrWalks = config['DEFAULT']['NBR_WALKS']
	totalTime = config['DEFAULT']['TOTAL_TIME']

	return "Lilo har gått " + " " + nbrWalks + " promenader " + "sedan 7e mars 2022. Hon har även varit ute i " + totalTime + " sekunder"
 

def StartTimer(config):
	t = Timer()
	t.start()
	
	while isOnWalk == True:
		time.sleep(1)
		print("TIMER COUNTING....")
	else: 
		print("TIMER STOPPED....")
		resultTime = t.stop()	
		retultTimeInt = int(resultTime)
		timeOutAlready = int(config['DEFAULT']['TOTAL_TIME'])
		totalTime = timeOutAlready + retultTimeInt
		config['DEFAULT']['CURRENT_WALK_TIME'] = str(retultTimeInt)
		config['DEFAULT']['TOTAL_TIME'] = str(totalTime)
		with open('walks.ini', 'w') as configfile:
			config.write(configfile)

@app.route('/Siri/Promenad', methods=['POST'])
def LiloPromenad():
	wentout = request.form['wentout']
	camehome = request.form['camehome']	
	config = configparser.ConfigParser()
	
	if wentout == "true":
		config.read('walks.ini')
		global isOnWalk
		isOnWalk = True
		nbr_walks = config.get("DEFAULT", "nbr_walks")
		newNumberWalks = int(nbr_walks) + 1
		config['DEFAULT']['NBR_WALKS'] = str(newNumberWalks)
		
		with open('walks.ini', 'w') as configfile:
			config.write(configfile)
		return StartTimer(config)
		
	if camehome == "true":
		isOnWalk = False
		time.sleep(3)
		config.read('walks.ini')
		current_walk_time = int(config.get("DEFAULT", "current_walk_time"))
		conversion = str(timedelta(seconds=current_walk_time))
		return "Totalt tid ute denna promenad med Lilo var: " + conversion

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


def get_selected_recipe_db(cursor, selectedRecepies):
	try:
		statement = DB_QUERY_INGREDIENTS
		ingredientList = []
		for obj in selectedRecepies:
			data = (obj,)
			cursor.execute(statement, data)
			for (ingredients) in cursor:
				ingredientList.append(ingredients)
		return ingredientList
	except mariadb.Error as e: print(f"Error retrieving entry from database: {e}")


def get_all_recipe(cursor, query):
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
		data = get_selected_recipe_db(cur, recepies)
		print("FINAL DATA----", type(data[0]))
		dishList = []
		dishListTmp = []
		groceryList = []
		for i in range(len(data[0])):
			dishList.append(data[0][i])

		for i in range(len(data[1])):
			groceryList.append(data[1][i])
		print("GROCERY: ", type(groceryList))

				
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

		for i in range(len(recepies)):
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

		priceList = 0

		
		f = open("grocerylist.txt", "w")
		for i in range (len(finalList[::2])):
			f.write(finalList[::2][i] + "\n")
		f.close()
		t = open("dishlist.txt", "w")
		for i in range (len(dishList)):
			t.write(dishList[i] + "\n")
		t.close()
		finalList.append(str(priceList))
		return json.dumps(list(finalList[::2]))

@app.route('/Siri/PromenadSummary', methods=['GET'])
def PromenadSummary():
	config = configparser.ConfigParser()
	config.read('walks.ini')
	current_walk_time = int(config.get("DEFAULT", "current_walk_time"))
	nbr_walks = int(config.get("DEFAULT", "nbr_walks"))
	total_time = int(config.get("DEFAULT", "total_time"))

	conversion_current_walk_time = str(timedelta(seconds=current_walk_time))

	conversion_total_time = str(timedelta(seconds=total_time))
	return "Senaste tid ute med lilo var " + conversion_current_walk_time + "...Totalt antal promenader är " + str(nbr_walks) + " stycken." + "...Total tid ute med lilo är " + conversion_total_time

def first2(s):
    return s[:2]

def getEverySecondDateInFuture(date):
	parsedDate = datetime.strptime(date, "%d/%m/%Y").date()
	dateList = []
	for i in range (20):
		td = timedelta(days=i+2)
		futureDate = parsedDate + td
		futureMedicationDates = futureDate.strftime("%d/%m/%Y")	
		dateList.append(futureMedicationDates)
	everyOtherDateList = dateList[::2]
	return everyOtherDateList


@app.route('/Siri/LiloStatus', methods=['GET'])
def LiloStatusSpeech():
	config = configparser.ConfigParser()
	config.read('lastDate.ini')
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")
	my_date = date.today()
	sense = SenseHat()
	weekday = calendar.day_name[my_date.weekday()]
	last_date = config['DEFAULT']['LAST_DATE']
	last_date_parsed = last_date.split(" ")[1]
	futureMedicationDates = getEverySecondDateInFuture(last_date_parsed)

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
	# testVar = json.loads(config.get("DEFAULT","futureMedicationDates"))
	# print("test var", testVar)
	match = veckodag + " " + date_time
	if (match == config['DEFAULT']['LAST_DATE'] and date_time in futureMedicationDates):
		return "Idag ska Lilo få medicin, men jag har redan skrivit upp att hon fått medicin idag " + config['DEFAULT']['LAST_DATE']
		
	if date_time in futureMedicationDates: 
		return ('Ja, idag ska Lilo få kortison. Lilo fick kortison senast ') + config['DEFAULT']['LAST_DATE'] + ('...När du gett henne medicinnnnn, säg Lilo fick medicin så skriver jag upp det')
	else: 
	
		return ('Nej, idag ska Lilo inte få kortison. Lilo fick kortison senast ') + config['DEFAULT']['LAST_DATE']
	
def LiloStatusLight():
	config = configparser.ConfigParser()
	config.read('lastDate.ini')
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")
	my_date = date.today()
	sense = SenseHat()
	weekday = calendar.day_name[my_date.weekday()]
	last_date = config['DEFAULT']['LAST_DATE']
	last_date_parsed = last_date.split(" ")[1]
	futureMedicationDates = getEverySecondDateInFuture(last_date_parsed)

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
	
		
	if date_time in futureMedicationDates: 
		while True:
			try:
				r = 0
				g = 255
				b = 0
				sense.clear((r, g, b))
				time.sleep(2)
				lastDate = config['DEFAULT']['LAST_DATE'].split(' ', 1)[1]
				now = datetime.now() # current date and time	
				date_time = now.strftime("%d/%m/%Y")	
				date_format = "%d/%m/%Y"
				a = datetime.strptime(date_time, date_format)
				b = datetime.strptime(lastDate, date_format)
				delta = a - b

				for i in range (delta.days):
					sense.clear((0, 0, 0))
					time.sleep(0.2)
					sense.clear((0, 255, 0))
					time.sleep(0.2)
					sense.clear((0, 0, 0))
								
				
			except AttributeError:
				time.sleep(2)
				continue

	else: 
		while True:
			try:
				r = 255
				g = 0
				b = 0
				sense.clear((r, g, b))
				time.sleep(2)
				lastDate = config['DEFAULT']['LAST_DATE'].split(' ', 1)[1]
				now = datetime.now() # current date and time	
				date_time = now.strftime("%d/%m/%Y")	
				date_format = "%d/%m/%Y"
				a = datetime.strptime(date_time, date_format)
				b = datetime.strptime(lastDate, date_format)
				delta = a - b

				for i in range (delta.days):
					sense.clear((0, 0, 0))
					time.sleep(0.2)
					sense.clear((255, 0, 0))
					time.sleep(0.2)
					sense.clear((0, 0, 0))
								
				
			except AttributeError:
				time.sleep(2)
				continue
		# r = 255
		# g = 0
		# b = 0

		# sense.clear((r, g, b))
		# time.sleep(0.5)
		# sense.clear((0, 255, 0))
		# time.sleep(0.5)
		# sense.clear((0, 0, 0))
		# time.sleep(0.5)
		# sense.clear((0, 0, 0))
		# time.sleep(0.5)
		
		# return ('Nej, idag ska Lilo inte få kortison. Lilo fick kortison senast ') + config['DEFAULT']['LAST_DATE']
	

@app.route('/Siri/LiloFick', methods=['POST'])
def LiloFick():
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")	
	config = configparser.ConfigParser()
	my_date = date.today()
	sense = SenseHat()
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
	r = 0
	g = 0
	b = 255
	config.read('lastDate.ini')
	match = veckodag + " " + date_time
	if (match == config['DEFAULT']['LAST_DATE']):
		return "Jag har redan skrivit upp att Lilo fick medicin idag " + config['DEFAULT']['LAST_DATE']
	else: 
		hasBeenGiven = True
		config['DEFAULT']['LAST_DATE'] = veckodag + " " + date_time
		with open('lastDate.ini', 'w') as configfile:
			config.write(configfile)
		sense.clear((r, g, b))
		return "Då noterar jag att Lilo fick medicin " + veckodag + " den " + date_time

if __name__ == '__main__':
	thread = Thread(target = LiloStatusLight)
	thread.start()
	app.run(debug=True, host=ip_address, port=PORT, use_reloader=False)
	
