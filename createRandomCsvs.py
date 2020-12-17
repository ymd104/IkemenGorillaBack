import sys
import csv
import sqlite3
import random
import datetime
import os
from random import randint
from csv import reader
from datetime import datetime

DATABASE = 'ikemengori.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.text_factory = str
    return db

print("Starting creating csv files...")

ncontests = input("---> How many contests exist? ")
nsponsors = input("---> How many sponsors exist? ")

#removing files if they already exist
if os.path.exists("csvfiles/support.csv"):
  os.remove("csvfiles/support.csv")
if os.path.exists("csvfiles/userfanzoo.csv"):
  os.remove("csvfiles/userfanzoo.csv")
if os.path.exists("csvfiles/userfananimal.csv"):
  os.remove("csvfiles/userfananimal.csv")
if os.path.exists("csvfiles/entry.csv"):
  os.remove("csvfiles/entry.csv")
if os.path.exists("csvfiles/vote.csv"):
  os.remove("csvfiles/vote.csv")
if os.path.exists("csvfiles/post.csv"):
  os.remove("csvfiles/post.csv")

#creating csv for table support
with open('csvfiles/support.csv', mode='w') as baseFile:
    csvWriter = csv.writer(baseFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(['sponsorID', 'contestID'])
    nsponallowed = input("---> How many sponsors are allowed per contest? (cant be less than number of contests) ")

    for contestID in range(1,int(ncontests)+1):
        #max sponsors allowed is 5, min 1
        sponsorNumber = randint(1, int(nsponallowed)+1)
        #list of all sponsor ids
        sponsors = list(range(1, int(nsponsors)+1))
        for sponsor in range(1, sponsorNumber):
            chosenSponsor = random.choice(sponsors)
            #writing rows to csv
            csvWriter.writerow([contestID, chosenSponsor])
            sponsors.remove(chosenSponsor)

    print("Created support.csv")

nusers =input("---> How many users exist? ")
nzoos = input("---> How many zoos exist? ")

#creating csv for table userfanzoo
with open('csvfiles/userfanzoo.csv', mode='w') as baseFile:
    csvWriter = csv.writer(baseFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(['userID', 'zooID'])
    nzooallowed = input("---> How many zoos are allowed per person to like? (cant be less than number of zoos) ")

    for userID in range(1,int(nusers)+1):
    	#max fictional likes is 6, min 1
    	likesNumber = randint(1,int(nzooallowed)+1)
    	#list of all zoos ids
    	zoos = list(range(1, int(nzoos)+1))
    	for like in range(1, likesNumber):
    		chosenZoo = random.choice(zoos)
    		#writing rows to csv
    		csvWriter.writerow([userID, chosenZoo])
    		zoos.remove(chosenZoo)

    print("Created userfanzoo.csv")

nanimals = input("---> How many animals exist? ")

#creating csv for table userfananimal
with open('csvfiles/userfananimal.csv', mode='w') as baseFile:
    csvWriter = csv.writer(baseFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(['animalID', 'userID'])
    naniallowed = input("---> How many animals are allowed per person to like? (cant be less than number of animals) ")

    for userID in range(1,int(nusers)+1):
    	#max fictional likes is 6, min 1
    	likesNumber = randint(1,int(naniallowed)+1)
    	#list of all zoos ids
    	animals = list(range(1, int(nanimals)+1))
    	for like in range(1, likesNumber):
    		chosenAnimal = random.choice(animals)
    		#writing rows to csv
    		csvWriter.writerow([userID, chosenAnimal])
    		animals.remove(chosenAnimal)

    print("Created userfananimal.csv")

totalentries = 0

#creating csv for table entry
with open('csvfiles/entry.csv', mode='w') as baseFile:
    csvWriter = csv.writer(baseFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(['placement', 'created', 'contestID', 'animalID', 'award'])

    nentries = int(nanimals) + 1;
    while(int(nentries) > int(nanimals)):
        nentries = input("---> How many maximum entries allowed for a contest? (must be less than total animals)")
        if(int(nentries) > int(nanimals)):
            print("entries was more than the total animals")

    #random entries for this contest
    nentriesContest = randint(3, int(nentries)+1)

    for contest in range(1,int(ncontests)+1):
        entriesAnimals = random.sample(range(1,int(nanimals)),nentriesContest)
        for animal in entriesAnimals:
            csvWriter.writerow([0, datetime.today().strftime('%d/%m/%Y'), contest, animal, "Cute Award"])
            totalentries = totalentries +1
    print("Created entry.csv")


#creating csv for table vote
with open('csvfiles/vote.csv', mode='w') as baseFile:
    csvWriter = csv.writer(baseFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(['entryID', 'userID', 'count', 'lastVoted'])

    nmaxusers = int(nusers)+1
    while(int(nmaxusers) > int(nusers)):
        nmaxusers = input("---> How many maximum users allowed to vote for entry? (must be less than total users)")
        if(int(nmaxusers) > int(nusers)):
            print("max users was more than the total users")

    for entry in range(1, totalentries+1):
        #number of users who voted for this entry
        nusersvoted = randint(1, int(nmaxusers))
        #which users voted
        userswhovoted = random.sample(range(1, int(nusers)+1), nusersvoted)
        for user in userswhovoted:
            totalvotes = randint(1,100)
            csvWriter.writerow([entry, user, totalvotes, datetime.today().strftime('%d/%m/%Y')])

    print("Created vote.csv")

#creating csv for table post

with open('csvfiles/post.csv', mode='w') as baseFile:
    csvWriter = csv.writer(baseFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(['image_url', 'created', 'description', 'animalID', 'zookeeperID'])
    
    imagescsv = input("---> What is the name of the animal&pictures csv? ")

    csvfile = open("csvfiles/"+imagescsv, 'r')
    csv_reader = reader(csvfile)
    next(csv_reader) #skipping header row
            
    picturesData = list(map(tuple, csv_reader))
    for row in picturesData:
        cursor = get_db()
        animalID = cursor.execute("SELECT ID FROM Animal WHERE commonName ='"+row[0]+"'").fetchone()
        if(animalID != None):
            for i in range(1, len(row)):
                if(row[i] != None and row[i] != ""):
                    csvWriter.writerow([row[i], datetime.today().strftime('%d/%m/%Y'), row[0], animalID[0], 0])
        else:
            print("no animal named "+row[0]+ " found.")
    csvfile.close()
    print("Created post.csv")


print("Done.")
