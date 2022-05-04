import os
import time
from datetime import datetime, date, timedelta
from flask import Flask, request
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

from config import (
	IP_ADDRESS,
	PORT,
	MY_DATES,
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
	CHECKOUT_CATEGORY
)
hostname = socket.gethostname()
isOnWalk = False
ip_address = IP_ADDRESS
app = Flask(__name__)

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

@app.route('/Siri/Matlista', methods=['GET'])
def Matlista():	
	randomlist = []
	recept = RECEPIES
	nbrDishesPerWeek = 5
	nbrRecepies = len(recept)
	final_recepie = []
	randomlist = random.sample(range(nbrRecepies), nbrDishesPerWeek)
	keep = gkeepapi.Keep()
	success = keep.login(KEEP_EMAIL, KEEP_PASSWORD)
	dishList = []
	groceryList = []
	
	for i in range(0,nbrDishesPerWeek):
		final_recepie.append(recept[randomlist[i]])
	f= open("matlista_dishes.txt","w+")
	for i in range(nbrDishesPerWeek):
		f.write(final_recepie[i][0] + "\n")
		dishList.append(str(final_recepie[i][0]))
		dishList.append("False")
	f.close()
	f= open("matlista_ingredients.txt","w+")

	for i in range(nbrDishesPerWeek):
		for j in range(len(final_recepie[i])-1):
			f.write(str(final_recepie[i][j+1]) + "\n")
			groceryList.append(str(final_recepie[i][j+1]))
	f.close()

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
	
	finalList = []

	for x in newListBread:
		finalList.append(x)
	for x in newListDairies:
		finalList.append(x)
	for x in newListSpices:
		finalList.append(x)
	for x in newListFrozen:
		finalList.append(x)
	for x in newListVegos:
		finalList.append(x)
	for x in newListCheese:
		finalList.append(x)
	for x in newListPasta:
		finalList.append(x)
	for x in newListCheckout:
		finalList.append(x)
	for x in newOtherList:
		finalList.append(x)

	duplicates = [item for item, count in collections.Counter(finalList).items() if count > 1]

	duplicatesIndexList = []

	for i in range(len(duplicates)):
		duplicatesIndexList.append(indices(finalList, duplicates[i]))

	numberOfDuplicatesList = []
	indexToRemoveList = []
	firstIndexList = []

	for i in range(len(duplicatesIndexList)):
		numberOfDuplicatesList.append(len(duplicatesIndexList[i]))
		indexToRemoveList.append(duplicatesIndexList[i][1:])
		firstIndexList.append(duplicatesIndexList[i][0])

	for i in range(len(firstIndexList)):
		finalList[firstIndexList[i]] = str(numberOfDuplicatesList[i]) + " x " + str(finalList[firstIndexList[i]])
	
	for i in range(len(duplicates)):
		finalList.remove(duplicates[i])
	


	# print("FINAL LIST AFTER: ", finalList)
	# print("FINAL LIST AFTER LENGTH: ", len(finalList))


	# # check for subsets
	# for i in range(len(finalList)):
	# 	for j in range(len(finalList)):
	# 		if i==j: continue # same index
	# 		if (set(finalList[i].split()) & set(finalList[j].split())) == set(finalList[i].split()): # if subset
	# 			print("FOUND DUPLICATE PART: ", finalList[i], "INDEX: ", i, "CORRESPONDING POS: ", j)
	# 			finalList[i]="" # clear string

	# # a = [x for x in a if len(x)]  # remove empty strings

	# b = []
	# for x in finalList:  # each string in a
	# 	if len(x) > 0: # if not empty
	# 		b.append(x)  # add to final list  

	# finalList = b
    

	superFinalList = []
	for x in finalList:
		superFinalList.append(x)
		superFinalList.append("False")


	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")	
	my_date = date.today()
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

	lst_tuple_grocery = [x for x in zip(*[iter(superFinalList)]*2)]
	dish_list_tuple = [x for x in zip(*[iter(dishList)]*2)]

	gnotes = keep.all()
	for i in range(len(gnotes)):
		if gnotes[i].title == "Inköpslista PI" or gnotes[i].title == "Matlista PI":
			gnotes[i].delete()
	
	glist = keep.createList('Inköpslista PI - ' + match, 
		lst_tuple_grocery
	)
	glist = keep.createList('Matlista PI - ' + match, 
		dish_list_tuple
	)

	# Sync up changes
	keep.sync()

	return "Jag har nu gjort en inköpslista i Google Keep. Det är " + str(nbrDishesPerWeek) + " av " + str(nbrRecepies) + " recept totalt"

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

@app.route('/Siri/LiloStatus', methods=['GET'])
def LiloStatus():
	config = configparser.ConfigParser()
	config.read('lastDate.ini')
	now = datetime.now() # current date and time	
	date_time = now.strftime("%d/%m/%Y")
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
	# testVar = json.loads(config.get("DEFAULT","my_dates"))
	# print("test var", testVar)
	match = veckodag + " " + date_time
	if (match == config['DEFAULT']['LAST_DATE'] and date_time in MY_DATES):
		return "Idag ska Lilo få medicin, men jag har redan skrivit upp att hon fått medicin idag " + config['DEFAULT']['LAST_DATE']
		
	if date_time in MY_DATES: 
		r = 0
		g = 255
		b = 0
		sense.clear((r, g, b))

		return ('Ja, idag ska Lilo få kortison. Lilo fick kortison senast ') + config['DEFAULT']['LAST_DATE'] + ('...När du gett henne medicin, säg Lilo fick medicin så skriver jag upp det')
	else: 
		r = 255
		g = 0
		b = 0

		sense.clear((r, g, b))
		return ('Nej, idag ska Lilo inte få kortison. Lilo fick kortison senast ') + config['DEFAULT']['LAST_DATE']
	

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
		sense.clear((r, g, b))
		return "Då noterar jag att Lilo fick medicin " + veckodag + " den " + date_time

if __name__ == '__main__':
	LiloStatus()
	app.run(debug=True, host=ip_address, port=PORT)
