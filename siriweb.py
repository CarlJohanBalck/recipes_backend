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
from icalendar import Calendar, Event, vCalAddress, vText
from pathlib import Path
import os
import mysql.connector as mariadb;
from decimal import *
from threading import Thread


from config import (
	IP_ADDRESS,
	PORT
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
	app.run(debug=True, host=ip_address, port=PORT, use_reloader=True)
	
