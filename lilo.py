import os
import time
from datetime import datetime, date, timedelta
from tkinter import E
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
g = (0, 255, 0)

e = (0, 0, 0)
y = (0, 0, 0)

b = (0,0,255)

r = (255,0,0)
blue = [
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b,
	b, b, b, b, b, b, b, b
]
smiley_face = [
   y, y, y, y, y, y, y, y,
   y, y, y, y, y, y, y, y,
   y, b, b, y, y, b, b, y,
   y, b, b, y, y, b, b, y,
   y, y, y, y, y, y, y, y,
   y, b, b, y, y, b, b, y,
   y, y, y, b, b, y, y, y,
   y, y, y, y, y, y, y, y
]

green_one = [
	e, e, e, g, g, e, e, e,
	e, g, g, g, g, e, e, e,
	e, g, g, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e
]
green_two = [
	e, g, g, g, g, g, e, e,
	e, g, g, g, g, g, e, e,
	e, e, e, g, g, g, e, e,
	e, e, e, g, g, g, e, e,
	e, g, g, g, g, e, e, e,
	e, g, g, e, e, e, e, e,
	e, g, g, g, g, g, e, e,
	e, g, g, g, g, g, e, e
]
green_three = [
	e, g, g, g, g, g, e, e,
	e, g, g, g, g, g, e, e,
	e, e, e, e, g, g, e, e,
	e, g, g, g, g, g, e, e,
	e, g, g, g, g, g, e, e,
	e, e, e, e, g, g, e, e,
	e, g, g, g, g, g, e, e,
	e, g, g, g, g, g, e, e
]
green_four = [
	e, e, e, g, g, e, e, e,
	e, g, g, g, g, e, e, e,
	e, g, g, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e,
	e, e, e, g, g, e, e, e
]

red_one = [
	e, e, e, r, r, e, e, e,
	e, r, r, r, r, e, e, e,
	e, r, r, r, r, e, e, e,
	e, e, e, r, r, e, e, e,
	e, e, e, r, r, e, e, e,
	e, e, e, r, r, e, e, e,
	e, e, e, r, r, e, e, e,
	e, e, e, r, r, e, e, e
]
red_two = [
	e, r, r, r, r, r, e, e,
	e, r, r, r, r, r, e, e,
	e, e, e, r, r, r, e, e,
	e, e, e, r, r, r, e, e,
	e, r, r, r, r, e, e, e,
	e, r, r, e, e, e, e, e,
	e, r, r, r, r, r, e, e,
	e, r, r, r, r, r, e, e
]
red_three = [
	e, r, r, r, r, r, e, e,
	e, r, r, r, r, r, e, e,
	e, e, e, e, r, r, e, e,
	e, r, r, r, r, r, e, e,
	e, r, r, r, r, r, e, e,
	e, e, e, e, r, r, e, e,
	e, r, r, r, r, r, e, e,
	e, r, r, r, r, r, e, e
]

hasBeenGiven = False

ip_address = IP_ADDRESS
app = Flask(__name__)
CORS(app)

print('\n Hostname of your Pi: ' + hostname)
print(' IP address of Pi: ' + ip_address)

sense = SenseHat()

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


def received_medicine(event):
	if event.action == 'pressed':
		
		LiloFick()
		
def LiloStatusLight():
	print("START LILO STATUS LIGHT")
	config = configparser.ConfigParser()
	config.read('lastDate.ini')
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")
	my_date = date.today()
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
			sense.stick.direction_middle = received_medicine
			try:
				# sense.clear((r, g, b))
				config = configparser.ConfigParser()
				config.read('lastDate.ini')
				# time.sleep(2)
				lastDate = config['DEFAULT']['LAST_DATE'].split(' ', 1)[1]
				now = datetime.now() # current date and time	
				date_time = now.strftime("%d/%m/%Y")	
				date_format = "%d/%m/%Y"
				a = datetime.strptime(date_time, date_format)
				b = datetime.strptime(lastDate, date_format)
				delta = a - b
				sense.set_rotation(180)

				number = 0


				if(delta.days == 1):
					number = green_one
				elif (delta.days == 2):
					number = green_two
				elif (delta.days == 3):
					number = green_three
				elif(delta.days == 0):
					number = smiley_face

				sense.set_pixels(number)

				# for i in range (delta.days):
				# 	sense.clear((0, 0, 0))
				# 	time.sleep(0.2)
				# 	sense.set_pixels(number)
				# 	time.sleep(0.2)
				# 	sense.clear((0, 0, 0))
								
				
			except AttributeError:
				print("ATTRIBUTE ERROR")
				time.sleep(2)
				continue

	else: 
		while True:
			sense.stick.direction_middle = received_medicine
			try:
				config = configparser.ConfigParser()
				config.read('lastDate.ini')
				lastDate = config['DEFAULT']['LAST_DATE'].split(' ', 1)[1]
				now = datetime.now() # current date and time	
				date_time = now.strftime("%d/%m/%Y")	
				date_format = "%d/%m/%Y"
				a = datetime.strptime(date_time, date_format)
				b = datetime.strptime(lastDate, date_format)
				delta = a - b
				sense.set_rotation(180)

				number = 0


				if(delta.days == 1):
					number = red_one
				elif (delta.days == 2):
					number = red_two
				elif (delta.days == 3):
					number = red_three
				elif(delta.days == 0):
					number = smiley_face

				sense.set_pixels(number)
				
			except AttributeError:
				time.sleep(2)
				continue
	
	

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
		config['DEFAULT']['LAST_DATE'] = veckodag + " " + date_time
		with open('lastDate.ini', 'w') as configfile:
			config.write(configfile)
		sense.set_pixels(smiley_face)
		return "Då noterar jag att Lilo fick medicin " + veckodag + " den " + date_time

if __name__ == '__main__':
	thread = Thread(target = LiloStatusLight)
	thread.start()
	app.run(debug=True, host=ip_address, port=PORT, use_reloader=False)
	
