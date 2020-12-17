# resetDB.py
import sqlite3
import sys
import csv
from csv import reader

## YOU CAN USE THIS FILE TO RUN ANY SQLITE CODE

DATABASE = 'ikemengori.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.text_factory = str
    return db

if(len(sys.argv) < 2):
	print("To use this program to run sqlite code type: python execDB -e <SQLITE CODE FILENAME>")
	print("To use this program to insert data in a table from .csv file type: python execDB -i <TABLE NAME> <CSV FILE NAME>")
else:
	if(sys.argv[1] == "-e" and len(sys.argv) > 2):
		filename = sys.argv[2]
		file = open(filename, "r")
		dbCode = file.read()

		print("Running sqlite code...")
		cursor = get_db().executescript(dbCode)
		get_db().commit()
		cursor.close()
		print("Done!")

	elif(sys.argv[1] == "-i" and len(sys.argv) > 3):
		
		print("Inserting into table "+sys.argv[2]+"...")
		
		table = sys.argv[2].lower()
		
		csvfilename = sys.argv[3]
		
		csvfile = open(csvfilename, 'r')
		csv_reader = reader(csvfile)
		next(csv_reader) #skipping header row
		
		data = list(map(tuple, csv_reader))

		if(table == "animal"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Animal' ('name', 'commonName','species', 'sex', 'birthday', 'image_url', 'description','zooID') VALUES (?,?,?,?,?,?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "zoo"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Zoo' ('name', 'image_url', 'description', 'address', 'latitude', 'longitude') VALUES (?,?,?,?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "support"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Support' ('sponsorID', 'contestID') VALUES (?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "contest"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Contest' ('name', 'start', 'end', 'catch_copy', 'image_url', 'description') VALUES (?,?,?,?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "vote"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Vote' ('entryID', 'userID', 'count', 'lastVoted') VALUES (?,?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "userfanzoo"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'UserFanZoo' ('userID', 'zooID') VALUES (?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "post"): 
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Post' ('image_url', 'created', 'description', 'animalID', 'zookeeperID') VALUES (?,?,?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "user"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'User' ('name', 'image_url', 'profile') VALUES (?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "entry"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Entry' ('placement', 'created', 'contestID', 'animalID', 'award') VALUES (?,?,?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "sponsor"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'Sponsor' ('name', 'image_url', 'website_url') VALUES (?,?,?)", data)
			cursor.commit()
			cursor.close()

		elif(table == "userfananimal"):
			cursor = get_db()
			cursor.executemany("INSERT INTO 'UserFanAnimal' ('animalID', 'userID') VALUES (?,?)", data)
			cursor.commit()
			cursor.close()

		else:
			print("Table "+sys.argv[2]+" does not exist in the database.")
			print("Tables that exist are:")
			print("Animal, Zoo, Picture, Support, Contest, Vote, UserFanZoo, Post, User, Entry, Sponsor, UserFanAnimal")
		print("Program done. Byebye!!")
	else:
		print("To use this program to run sqlite code type: python execDB -e <SQLITE CODE FILENAME>")
		print("To use this program to insert data in a table from .csv file type: python execDB -i <TABLE NAME> <CSV FILE NAME>")
