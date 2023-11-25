import os
import time
from datetime import datetime, date, timedelta
from tkinter import E
from flask import Flask, request
from flask_cors import CORS
import socket
import time
import configparser
import calendar
from sense_hat import SenseHat
import os
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
	e, g, g, e, e, g, g, e,
	e, g, g, e, e, g, g, e,
	e, g, g, g, g, g, g, e,
	e, g, g, g, g, g, g, e,
	e, e, e, e, e, g, g, e,
	e, e, e, e, e, g, g, e,
	e, e, e, e, e, g, g, e,
	e, e, e, e, e, g, g, e
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
red_four = [
	e, r, r, e, e, r, r, e,
	e, r, r, e, e, r, r, e,
	e, r, r, r, r, r, r, e,
	e, r, r, r, r, r, r, e,
	e, e, e, e, e, r, r, e,
	e, e, e, e, e, r, r, e,
	e, e, e, e, e, r, r, e,
	e, e, e, e, e, r, r, e
]

hasBeenGiven = False

ip_address = IP_ADDRESS
app = Flask(__name__)
CORS(app)

print('\n Hostname of your Pi: ' + hostname)
print(' IP address of Pi: ' + ip_address)

sense = SenseHat()


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

def received_medicine(event):
	if event.action == 'pressed':
		
		LiloFick()
		
def LiloStatusLight():
	config = configparser.ConfigParser()
	config.read('lastDate.ini')
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")
	last_date = config['DEFAULT']['LAST_DATE']
	last_date_parsed = last_date.split(" ")[1]
	futureMedicationDates = getEverySecondDateInFuture(last_date_parsed)

	if date_time in futureMedicationDates: 
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
					number = green_one
				elif (delta.days == 2):
					number = green_two
				elif (delta.days == 3):
					number = green_three
				elif (delta.days == 4):
					number = green_four
				elif(delta.days == 0):
					number = smiley_face

				sense.set_pixels(number)

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
				elif (delta.days == 4):
					number = red_four
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
	
