import sqlite3
import csv
import requests
from csv import writer

fli = sqlite3.connect('FlightsDBTest.db')
flights = fli.cursor()

def loadaircrafttypes():
  file = open("AircraftTypes.csv", "r")
  csvreader = csv.reader(file)
  for row in csvreader:
    flights.execute('INSERT INTO AircraftTypes VALUES (?);', row)
  file.close()
  fli.commit()

def loadairlines():
  flights.execute('DELETE FROM Airlines')
  file = open("Airlines.csv", "r")
  csvreader = csv.reader(file)
  for row in csvreader:

    if row != '':
      flights.execute('INSERT INTO Airlines VALUES (?);', row)
  file.close()
  fli.commit()

def setdummydata():
  file = open('dummydata.csv')
  csvreader = csv.reader(file)
  for row in csvreader:
    flights.execute('INSERT INTO Flights VALUES(?, ?, ?, ?, ?, ?, ?);', row)
  file.close()
  fli.commit()

def reset():
  clear()
  loadaircrafttypes()
  loadairlines()
  setdummydata()
  fli.commit()

def clear():
  flights.execute("DROP TABLE IF EXISTS Flights")
  flights.execute("DROP TABLE IF EXISTS AircraftTypes")
  flights.execute("DROP TABLE IF EXISTS Airlines")
  createTables()

def createTables():
  flights.execute(""" 
  CREATE TABLE Flights(
    airline	      TEXT,
    flightnumber  TEXT,
    type          TEXT,
    reg           TEXT,
    origin	      TEXT,
    destination   TEXT,
    date          DATE,
    CONSTRAINT IDPK PRIMARY KEY (flightnumber, date));
  """)
  flights.execute(""" 
  CREATE TABLE AircraftTypes(
    type	      TEXT,
    CONSTRAINT IDPK PRIMARY KEY (type));
  """)
  flights.execute(""" 
  CREATE TABLE Airlines(
    airline	      TEXT,
    CONSTRAINT IDPK PRIMARY KEY (airline));
  """)

def listContainsAirline(airline):
  flights.execute("SELECT airline FROM Airlines WHERE airline = ?", (airline,))
  data = flights.fetchall()
  if len(data) == 0 :
    return 0
  else:
    return 1

def addflight(args):
  try:
    flights.execute('INSERT INTO Flights VALUES(?, ?, ?, ?, ?, ?, ?);', args)
    print("Flight added!")
  except sqlite3.IntegrityError:
    print("Flight already added!")
  fli.commit()

def addAirline(airline):
  with open('Airlines.csv', 'a', newline='') as f_object:  
    writer_object = writer(f_object)
    writer_object.writerow([airline])  
    f_object.close()
  loadairlines()

def getAirlineSearchResults(query):
  url = "https://aviation-reference-data.p.rapidapi.com/airline/search"
  querystring = {"name":query}
  headers = {
	  "X-RapidAPI-Key": "c619aef76amshc85efbf6b097b12p1beb9bjsn603e2baf2a5d",
	  "X-RapidAPI-Host": "aviation-reference-data.p.rapidapi.com"
  }
  response = requests.request("GET", url, headers=headers, params=querystring)
  results = response.json()
  return(results)

def getAircraftType():
  aircrafttypeuserinput = input("Aircraft Type: ")
  aircrafttype = ""
  file = open("AircraftTypes.csv", "r")
  csvreader = csv.reader(file)
  for row in csvreader:
    if row[0] == aircrafttypeuserinput:
      aircrafttypeuserinput = aircrafttype
      break
  if aircrafttypeuserinput != aircrafttype:
    print("NO!")
    getAircraftType()
  else:
    return

def getflightinput():
    airline = input("Airline: ")
    print("Choose airline (y/n): ")
    results = getAirlineSearchResults(airline)
    if (len(results) > 0):
      counter = 1
      for i in results:
        print("(" + str(counter) + ")", i["name"])
        counter += 1
      index = int(input(""))
      airline = results[index-1]["name"]
      iataCode = results[index-1]["iataCode"]
    else:
      print("Airline not found. Please input airline again")
      getflightinput()
    flightnumber = iataCode + input("Flight Number: ")

    aircrafttype = getAircraftType()
    
    reg = input("Registration: ")
    origin = input("Origin: ")
    destination = input("Destination: ")
    date = input("Date (YYYY-MM-DD): ")
    addflight((airline, flightnumber, aircrafttype, reg, origin, destination, date))

action = ""
while action != "exit":
  print()
  action = input("Enter command: ")
  if action == "r":
    reset()
  if action == "s":
    setdummydata()
  if action == "a":
    getflightinput()
  if action == "c":
    clear()

fli.commit()
fli.close()