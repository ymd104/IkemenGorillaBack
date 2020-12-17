# app.py
from flask import Flask, request, jsonify, g
import sqlite3
import sys
from datetime import datetime

app = Flask(__name__)

#DATABASE ACCESS CODE

DATABASE = 'ikemengori.db'

def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#-------------------------------------------------------------

#EXAMPLE OF GET
@app.route('/getecho/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    echo = request.args.get("echo", None)

    # For debugging
    print(f"got string {echo}")

    response = {}

    # Check if user sent a name at all
    if not echo:
        response["ERROR"] = "no string found, please send a string."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"The server echoes: {echo}"

    # Return the response in json format
    return jsonify(response)


#EXAMPLE OF POST

@app.route('/postecho/', methods=['POST'])
def post_something():
    param = request.form.get('echo')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": f"Server got via POST, the message: {param}",
            # Add this option to distinct the POST request
            "METHOD" : "POST"
        })
    else:
        return jsonify({
            "ERROR": "no string found, please send a string."
        })

#DATABASE ACCESS EXAMPLE

@app.route('/testdatabase/', methods=['GET'])
def testdatabase():
    cur = get_db().execute("SELECT * FROM User;")
    userinfo = cur.fetchall()
    cur.close()

    response = {}

    #example of printing on logs
    print("example of printing on logs")
    sys.stdout.flush()

    # Check if user sent a name at all
    if not userinfo[0]:
        response["ERROR"] = "test database, found 0 users"
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"The server found: {userinfo[0]}"

    # Return the response in json format
    return jsonify(response)


#-------------------------------------------------------------

#API ROUTES


@app.route('/zoos/recommended/', methods=['GET'])
def zoosRecommended():
    response = []

    #Getting random 8 zoos in a optimized manner
    cur = get_db().execute("SELECT CAST(ID AS TEXT) as id, name, image_url FROM Zoo WHERE ID IN (SELECT ID FROM Zoo ORDER BY RANDOM() LIMIT 8);")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
    
    cur.close()

    return jsonify(response)

@app.route('/contests/<int:contest_id>/sponsors', methods=['GET'])
def getContestSponsors(contest_id):
    response = []
    sponsorIDs = []

    #getting sponsor IDs based on contest id
    cur = get_db().execute("SELECT CAST(sponsorID AS TEXT) as id FROM Support WHERE contestID = "+str(contest_id)+";")
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        sponsorIDs.append(row[0])
    
    cur.close()
    
    #getting all information about each sponsor
    cur = get_db().execute("SELECT CAST(ID AS TEXT) as id, name, image_url, website_url FROM Sponsor WHERE ID IN ("+str(sponsorIDs).strip('[]')+");")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
   
    cur.close()

    return jsonify(response)


#TODO ADD PAGING
@app.route('/contests/<int:contest_id>/posts', methods=['GET'])
def getContestPosts(contest_id):
        entries = []
        # Retrieve url parameters
        status = request.args.get("status", None)
        page = request.args.get("page", None)

        #selecting Posts according to contest_id
        #this is a merge of Contest -> Entry -> Zoo/Animal -> Post entities. 
        cur = get_db().execute( \
            "SELECT p.created AS created_at, CAST(p.ID AS TEXT) AS id, p.image_url as image_url, CAST(a.ID AS TEXT) AS animal_id, a.name AS animal_name, \
            a.image_url AS animal_icon_url, p.description, CAST(z.ID AS TEXT) AS zoo_id, z.name AS zoo_name \
                FROM Entry e, Zoo z, Animal a, Post p WHERE e.animalID = a.ID AND a.zooID = z.ID AND p.animalID = a.ID AND e.contestID = "+str(contest_id)+" \
                LIMIT 12 OFFSET " + str(12 * int(page)) + ";")
        
        columns = [column[0] for column in cur.description]
        for row in cur.fetchall():
            entries.append(dict(zip(columns, row)))

        print (entries)
        cur.close()

        return jsonify(entries)


@app.route('/contests/<int:contest_id>/results', methods=['GET'])
def getContestResults(contest_id):
    response = []

    #getting animals and votes of each animal
    cur = get_db().execute("SELECT CAST(a.ID AS TEXT) as animal_id, a.name as animal_name, a.image_url as icon_url, SUM(v.count) as number_of_votes \
        FROM Animal a, Vote v, Entry e \
        WHERE e.animalID = a.ID AND v.entryID = e.ID AND e.contestID = "+str(contest_id)+" \
        GROUP BY a.ID ORDER BY number_of_votes DESC;")
    
    first = cur.fetchone()

    if(first == None):
        err = {}
        err["error"] = "this contest has 0 votes"
        response.append(err)
        return jsonify(response)
    else:
        columns = [column[0] for column in cur.description]
        #getting max number of votes in this contest
        firstPlace = []
        firstPlace = dict(zip(columns, first))
        firstPlace['max_of_votes'] = firstPlace['number_of_votes']
        response.append(firstPlace)

        for row in cur.fetchall():
            res = []
            res = dict(zip(columns, row))
            res['max_of_votes'] = firstPlace['number_of_votes']

            response.append(res)

    cur.close()

    return jsonify(response)

'''

#TODO ADD PAGINATION
@app.route('/animals/<int:animal_id>/posts', methods=['GET'])
def getAnimalPosts(animal_id):
    page = request.args.get("page", None)

    response = []

    #selecting Posts according to animal_id 
    cur = get_db().execute( \
        "SELECT p.created AS created_at, p.ID AS id, a.ID AS animal_id, a.name AS animal_name, \
        a.image_url AS animal_icon_url, p.description, z.ID AS zoo_id, z.name AS zoo_name, p.image_url \
        FROM Zoo z, Animal a, Post p WHERE a.zooID = z.ID AND p.animalID = a.ID AND a.ID = "+str(animal_id)+" \
        ;")
    
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))

    cur.close()

    return jsonify(response)

'''

@app.route('/zoos/<int:zoo_id>', methods=['GET'])
def zooByID(zoo_id):
    user = request.args.get("user_id", None)

    zoo = {}

    #getting zoo
    cur = get_db().execute("SELECT CAST(ID AS TEXT) AS id, name, address, latitude, longitude, image_url, description FROM Zoo WHERE ID = "+str(zoo_id)+";")
    columns = [column[0] for column in cur.description]
    zoo = dict(zip(columns, cur.fetchone()))
    
    #getting how many favorites
    cur = get_db().execute("SELECT COUNT(ID) as nfavorites FROM UserFanZoo WHERE zooID = "+str(zoo_id)+";")
    columns = [column[0] for column in cur.description]
    result = dict(zip(columns, cur.fetchone()))
    zoo["number_of_favorites"] = result["nfavorites"]

    #getting if this user has zoo as favorite
    cur = get_db().execute("SELECT COUNT(ID) as fan FROM UserFanZoo WHERE userID = "+str(user)+" AND zooID = "+str(zoo_id)+";")
    columns = [column[0] for column in cur.description]
    result = dict(zip(columns, cur.fetchone()))
    if(result["fan"] == 0):
        zoo["is_favorite"] = False
    else:
        zoo["is_favorite"] = True

    cur.close()

    return jsonify(zoo)

#TODO add pagination
@app.route('/zoos/<int:zoo_id>/posts', methods=['GET'])
def zooPosts(zoo_id):
    response = []
    page = request.args.get("page", None)

    #selecting Posts according to zoo_id
    cur = get_db().execute( \
        "SELECT p.created AS created_at, CAST(p.ID AS TEXT) AS id, CAST(a.ID AS TEXT) AS animal_id, a.name AS animal_name, \
        a.image_url AS animal_icon_url, p.description, CAST(z.ID AS TEXT) AS zoo_id, z.name AS zoo_name, p.image_url \
            FROM Zoo z, Animal a, Post p WHERE a.zooID = z.ID AND p.animalID = a.ID AND z.ID = "+str(zoo_id)+" \
            LIMIT 12 OFFSET " + str(12*int(page)) + ";")

    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))

    cur.close()

    return jsonify(response)

#TODO limit 8 contests AND add paging
@app.route('/animals/<int:animal_id>/contests', methods=['GET'])
def animalContests(animal_id):
    #variable got from parameters
    status = request.args.get("status", None)

    #finding all the contests which Entries have animal_id
    contests = []
    cur = get_db().execute("SELECT CAST(e.contestID AS TEXT) AS contestID FROM Entry e WHERE e.animalID ="+str(animal_id)+";")
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        contests.append(row["contestID"])
    cur.close()

    #getting the entire contests
    response = []    
    cur = get_db().execute("SELECT CAST(id AS TEXT) AS contest_id, name,start,end,catch_copy,image_url FROM Contest WHERE ID IN ("+str(contests).strip('[]')+");")
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        
        contest = {}
        contest = dict(zip(columns, row))

        #add status to contest based on start and end date
        startdate = row["start"]
        enddate = row["end"]
        format_str = '%d/%m/%Y' # The format
        startdate_obj = datetime.strptime(startdate, format_str)
        enddate_obj = datetime.strptime(enddate, format_str)
        presentdate = datetime.now()

        #test if contest ended
        if(enddate_obj < presentdate):
            contest["status"] = "ended"
        #test it contest is current
        elif(presentdate < enddate_obj and startdate_obj < presentdate):
            contest["status"] = "current"
        #else, contest didnt start yet
        else:
            contest["status"] = "upcoming"

        #filtering contests by the status given in parameters
        if(contest["status"] == status or status == None or status == ""):
            response.append(contest)    

    cur.close()

    return jsonify(response)

@app.route('/createuser', methods=['GET'])
def createUser():
    response = []
    newuser = {}

    cur = get_db().execute("INSERT INTO 'User' ('name', 'image_url', 'profile') VALUES ('','','');")
    get_db().commit()

    newuser["id"] = cur.lastrowid
    newuser["name"] = ""
    newuser["image_url"] = ""
    newuser["profile"] = ""

    response.append(newuser)

    cur.close()

    return jsonify(response)

#TODO add profile data
@app.route('/users/<int:user_id>', methods=['POST'])
def editUser(user_id):
    
    updateduser = {}
    #proper way to receive parameters in POST
    name = request.form.get('name')
    icon = request.form.get('icon_url')

    cur = get_db().execute("UPDATE 'User' SET name = '"+str(name)+"', 'image_url' = '"+str(icon)+"' WHERE ID = "+str(user_id)+";")
    get_db().commit()

    updateduser["id"] = user_id
    updateduser["name"] = name
    updateduser["icon_url"] = icon
    updateduser["profile"] = ""

    cur.close()

    response = []
    response.append(updateduser)

    return jsonify(response)

@app.route('/contests/<int:contest_id>/vote', methods=['POST'])
def vote(contest_id):
    
    response = {}

    #proper way to receive parameters in POST
    user = request.form.get('user_id')
    animal = request.form.get('animal_id')
    
    if(user == None or user=="" or animal =="" or animal == None):
        response["result"] = "error: user id or animal id missing."
        return jsonify(response)

    #selecting the Entry related to the vote
    cur = get_db().execute("SELECT * FROM 'Entry' WHERE contestID="+str(contest_id)+" AND animalID="+str(animal)+";")
    entry = cur.fetchone()

    if(entry != None):
        #see if user already voted
        cur1 = get_db().execute("SELECT * FROM 'Vote' WHERE entryID="+str(entry["ID"])+" AND userID="+str(user)+";")
        vote = cur1.fetchone()

        #if not then create a new Vote
        if( vote == None):
            #insert in table Vote
            cur2 = get_db().execute("INSERT INTO 'Vote'('entryID', 'userID', 'count', 'lastVoted') VALUES ('"+str(entry["ID"])+"','"+str(user)+"', 1, '"+datetime.today().strftime('%d/%m/%Y')+"');")
            get_db().commit()
            cur2.close()
            response["result"] = "ok"
        #else increase the count
        else:
            #test if user already voted 
            if(vote['lastVoted'] == datetime.today().strftime('%d/%m/%Y')):
                response["result"] = "error: already voted"
            else:
                voteID = str(vote['ID'])
                voteCount = vote['count'] + 1;
                cur2 = get_db().execute("UPDATE 'Vote' SET count="+str(voteCount)+", lastVoted='"+datetime.today().strftime('%d/%m/%Y')+"' \
                    WHERE ID = "+voteID+";")
                get_db().commit()
                cur2.close()
                response["result"] = "ok"

        cur1.close()

    else:
        response["result"] = "error: entry related to this vote doesnt exist"
    cur.close()

    return jsonify(response)


#TODO 
@app.route('/search', methods=['GET'])
def searchPosts():
    keyword = request.args.get("query", None)
    response = []

    #searching posts by animal name, zoo name, description, animal species 
    cur = get_db().execute( \
        "SELECT p.created AS created_at, CAST(p.ID AS TEXT) AS id, CAST(a.ID AS TEXT) AS animal_id, a.name AS animal_name, \
        a.image_url AS animal_icon_url, p.description, CAST(z.ID AS TEXT) AS zoo_id, z.name AS zoo_name, p.image_url \
        FROM Zoo z, Animal a, Post p \
        WHERE (a.zooID = z.ID AND p.animalID = a.ID) AND \
        (z.name='"+keyword+"' OR a.name='"+keyword+"' OR a.commonName='"+keyword+"' OR a.species='"+keyword+"' OR p.description LIKE '%"+keyword+"%') \
        LIMIT 24;")
    
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))

    cur.close()

    return jsonify(response)



#TODO limit 8 contests AND add paging
@app.route('/users/<int:user_id>/contests', methods=['GET'])
def votedContests(user_id):
    page = request.args.get("page", None)

    #finding all the contests which Entries were voted for by user
    contests = []
    cur = get_db().execute("SELECT e.contestID FROM Entry e, Vote v \
        WHERE v.userID ="+str(user_id)+" AND v.entryID = e.ID")
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        contests.append(row["contestID"])
    cur.close()

    #getting the entire contests
    response = []    
    cur = get_db().execute("SELECT CAST(id AS TEXT) AS id, name, start, end, catch_copy, image_url FROM Contest WHERE ID IN ("+str(contests).strip('[]')+") LIMIT 8 OFFSET " + str(8*int(page)) + ";")
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        
        contest = {}
        contest = dict(zip(columns, row))

        #add status to contest based on start and end date
        startdate = row["start"]
        enddate = row["end"]
        format_str = '%d/%m/%Y' # The format
        startdate_obj = datetime.strptime(startdate, format_str)
        enddate_obj = datetime.strptime(enddate, format_str)
        presentdate = datetime.now()

        #test if contest ended
        if(enddate_obj < presentdate):
            contest["status"] = "ended"
        #test it contest is current
        elif(presentdate < enddate_obj and startdate_obj < presentdate):
            contest["status"] = "current"
        #else, contest didnt start yet
        else:
            contest["status"] = "upcoming"

        response.append(contest)    
    cur.close()

    return jsonify(response)

@app.route('/zoos/<int:zoo_id>/favorite', methods=['POST'])
def favoriteZoo(zoo_id):
    
    response = {}

    #proper way to receive parameters in POST
    user = request.form.get('user_id')
    cur = get_db().execute("SELECT * FROM 'UserFanZoo' WHERE userID="+str(user)+" AND zooID="+str(zoo_id)+";")
    fan = cur.fetchone()
    if(fan == None):
        cur = get_db().execute("INSERT INTO 'UserFanZoo'('userID', 'zooID') VALUES ("+str(user)+", "+str(zoo_id)+");")
        get_db().commit()

        if(cur.lastrowid == "" or cur.lastrowid == None):
            response["error"] = "Insert in table failed."
            cur.close()
            return jsonify(response)
        else:
            response["result"] = "ok"
            cur.close()
            return jsonify(response)
    else:
        response["error"] = "User is already fan of this zoo."
        return jsonify(response)

@app.route('/animals/<int:animal_id>/fan', methods=['POST'])
def favoriteAnimal(animal_id):
    
    response = {}

    #proper way to receive parameters in POST
    user = request.form.get('user_id')

    cur = get_db().execute("SELECT * FROM 'UserFanAnimal' WHERE userID="+str(user)+" AND animalID="+str(animal_id)+";")
    fan = cur.fetchone()
    if(fan == None):
        cur = get_db().execute("INSERT INTO 'UserFanAnimal'('userID', 'animalID') VALUES ("+str(user)+", "+str(animal_id)+");")
        get_db().commit()

        if(cur.lastrowid == "" or cur.lastrowid == None):
            response["error"] = "Insert in table failed."
            cur.close()
            return jsonify(response)
        else:
            response["result"] = "ok"
            cur.close()
            return jsonify(response)
    else:
        response["error"] = "User is already fan of this animal."
        return jsonify(response)

#YAMADA

@app.route('/contests', methods=['GET'])
def contests():

    # Retrieve url parameters
    status = request.args.get("status", None)
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT Cast(id AS TEXT) AS id, name,start, end, catch_copy, image_url FROM Contest LIMIT 8 OFFSET " + str(8*int(page)) +  ";")
    #cur = get_db().execute("SELECT * FROM Contest;")
    #contestinfo = cur.fetchall()

    response = []

    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        d = dict(zip(columns, row))
        d["status"] = status
        response.append(d)

   
    cur.close()

    #CODE
    #if (status[0] and page[0]):
        #do code for it

    """
    if not contestinfo[0]:
        response["ERROR"] = "test database, found 0 contests"
    """

    return jsonify(response)



@app.route('/contests/<int:contest_id>', methods=['GET'])
def getContest(contest_id):
    response = {}
    status = request.args.get("status", None)

    cur = get_db().execute("SELECT Cast(id AS TEXT) AS id, name, image_url, start, end, catch_copy, description FROM Contest WHERE ID = "+str(contest_id)+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))

        response = dict(zip(columns, row))

        startdate = row["start"]
        enddate = row["end"]
        format_str = '%d/%m/%Y' # The format
        startdate_obj = datetime.strptime(startdate, format_str)
        enddate_obj = datetime.strptime(enddate, format_str)
        presentdate = datetime.now()

        #test if contest ended
        if(enddate_obj < presentdate):
            response["status"] = "ended"
        #test it contest is current
        elif(presentdate < enddate_obj and startdate_obj < presentdate):
            response["status"] = "current"
        #else, contest didnt start yet
        else:
            response["status"] = "upcoming"

   
    cur.close()

    
    cur = get_db().execute("SELECT COUNT(*) AS number_of_entries FROM Entry WHERE contestID = "+str(contest_id)+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response[columns[0]]=row[0]
   
    cur.close()

    
    cur = get_db().execute("SELECT COUNT(*) AS number_people_that_voted FROM Entry, Vote WHERE Entry.ID=Vote.entryID AND contestID = "+str(contest_id)+" GROUP BY userID ;")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response[columns[0]]=row[0]
   
    cur.close()


    cur = get_db().execute("SELECT COUNT(*) AS number_of_votes FROM Entry, Vote WHERE Entry.ID=Vote.entryID AND contestID = "+str(contest_id)+" ;")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response[columns[0]]=row[0]
        
    cur.close()

    return jsonify(response)



@app.route('/contests/<int:contest_id>/animals', methods=['GET'])
def getContestAnimal(contest_id):
    response = []
    # Retrieve url parameters
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT CAST(animalID AS TEXT) AS animal_id, Animal.name, Animal.image_url AS icon_url, Zoo.name AS zoo_name FROM Entry, Animal, Zoo WHERE contestID = "+str(contest_id)+" AND Entry.animalID = Animal.ID AND Animal.ZooID = Zoo.id LIMIT 8 OFFSET " + str(8*int(page)) + ";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
   
    cur.close()

    return jsonify(response)


@app.route('/contests/<int:contest_id>/awards', methods=['GET'])
def getContestAwards(contest_id):
    response = []

    cur = get_db().execute("SELECT CAST(animalID AS TEXT) as animal_id, Animal.name as animal_name, Animal.image_url AS icon_url, award AS award_name FROM Entry, Animal WHERE contestID = "+str(contest_id)+" AND Entry.animalID = Animal.ID;")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
   
    cur.close()

    return jsonify(response)



@app.route('/contests/<int:contest_id>/animals/<int:animal_id>', methods=['GET'])
def getContestAnimalPage(contest_id, animal_id):
    response = {}

    cur = get_db().execute("SELECT CAST(animalID AS TEXT) AS animal_id, Animal.name AS animal_name, Animal.image_url AS animal_icon_url, description FROM Animal, Entry WHERE Animal.ID = Entry.animalID AND Animal.ID = "+str(animal_id)+" AND Entry.contestID = "+str(contest_id)+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))
        response = dict(zip(columns, row))
    cur.close()

    subresponse = {}
    cur = get_db().execute("SELECT CAST(Zoo.ID AS TEXT) AS zoo_id, Zoo.name AS zoo_name, address AS zoo_address FROM Zoo, Animal WHERE Zoo.ID = Animal.zooID AND Animal.ID = "+str(animal_id)+";")
    columns = [column[0] for column in cur.description]
    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))
        subresponse = dict(zip(columns, row))
    response["is_voted_today"] = False
    cur.close()

    response.update(subresponse)

    return jsonify(response)



@app.route('/zoos/', methods=['GET'])
def getZoos():
    response = []

    cur = get_db().execute("SELECT CAST(ID AS TEXT) AS id, name, address, latitude, longitude, image_url FROM Zoo;")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
   
    cur.close()

    return jsonify(response)


@app.route('/zoos/<int:zoo_id>/animals', methods=['GET'])
def getZooAnimals(zoo_id):
    response = []
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT CAST(Animal.ID AS TEXT) AS id, Animal.name, Animal.image_url AS icon_url FROM Animal, Zoo WHERE Zoo.ID = "+str(zoo_id)+" AND Animal.ZooID = Zoo.id LIMIT 8 OFFSET "+ str(8*int(page)) +";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        d = dict(zip(columns, row))
        d["is_fan"] = False
        response.append(d)
   
    cur.close()

    return jsonify(response)


@app.route('/animals/<int:animal_id>', methods=['GET'])
def getAnimalPage(animal_id):
    response = {}

    cur = get_db().execute("SELECT CAST(ID AS TEXT) AS id, name, image_url AS icon_url, sex, birthday, description, Zoo.name AS zoo_name FROM Animal, Zoo WHERE Animal.zooID = Aoo.id AND Animal.id = "+str(animal_id)+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))
        response = dict(zip(columns, row))
    cur.close()


    cur = get_db().execute("SELECT COUNT(*) AS number_of_fans FROM UserFanAnimal WHERE animalID = "+str(animal_id)+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))
        response = dict(zip(columns, row))
    cur.close()

    response["is_fan"] = False


    return jsonify(response)



@app.route('/animals/<int:animal_id>/posts', methods=['GET'])
def getAnimalPosts(animal_id):
    response = []
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT CAST(Post.ID AS TEXT) AS id, CAST(Animal.ID AS TEXT) AS animal_id, Animal.name AS animal_name, Animal.image_url AS animal_icon_url, CAST(Animal.zooID AS TEXT) as zoo_id, Zoo.name AS zoo_name, Post.image_url AS image_url, Post.description AS description, created AS created_at FROM Animal, Post, Zoo WHERE Animal.ID = Post.animalID AND Animal.zooID = Zoo.ID AND Animal.id = "+str(animal_id)+" LIMIT 8 OFFSET " + str(8*int(page)) + ";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
        #response = dict(zip(columns, row))
    cur.close()

    return jsonify(response)


@app.route('/posts', methods=['GET'])
def getPosts():
    response = []
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT CAST(Post.ID AS TEXT) AS id, CAST(Animal.ID AS TEXT) AS animal_id, Animal.name AS animal_name, Animal.image_url AS animal_icon_url, CAST(Animal.zooID AS TEXT) as zoo_id, Zoo.name AS zoo_name, Post.image_url AS image_url, Post.description AS description, created AS created_at FROM Animal, Post, Zoo WHERE Animal.ID = Post.animalID AND Animal.zooID = Zoo.ID LIMIT 24 OFFSET "+ str(24*int(page)) +";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        response.append(dict(zip(columns, row)))
        #response = dict(zip(columns, row))
    cur.close()

    return jsonify(response)


@app.route('/users/<int:user_id>', methods=['GET'])
def getUser(user_id):
    response = {}

    cur = get_db().execute("SELECT CAST(ID AS TEXT) AS id, name, image_url AS icon_url, profile AS description FROM User WHERE ID = " + str(user_id) + ";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))
        response = dict(zip(columns, row))
    cur.close()

    return jsonify(response)


@app.route('/users/<int:user_id>/fans', methods=['GET'])
def getUserFans(user_id):
    response = []
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT CAST(animalID AS TEXT) AS id, Animal.name AS name, Animal.image_url AS icon_url, Zoo.name AS zoo_name FROM User, UserFanAnimal, Animal, Zoo WHERE Animal.ID = UserFanAnimal.animalID AND User.ID = UserFanAnimal.userID AND Zoo.ID = Animal.zooID AND User.ID = "+str(user_id)+" LIMIT 8 OFFSET "+str(8*int(page))+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        d = dict(zip(columns, row))
        d["is_fan"] = True
        response.append(d)
    cur.close()

    return jsonify(response)


@app.route('/users/<int:user_id>/zoos', methods=['GET'])
def getUserFansZoos(user_id):
    response = []
    page = request.args.get("page", None)

    cur = get_db().execute("SELECT CAST(zooID AS TEXT) AS id, name, image_url FROM UserFanZoo, Zoo WHERE userID = " + str(user_id) + " AND UserFanZoo.zooID = Zoo.ID LIMIT 8 OFFSET "+ str(8*int(page))+";")
    columns = [column[0] for column in cur.description]

    for row in cur.fetchall():
        #response.append(dict(zip(columns, row)))
        response = dict(zip(columns, row))
    cur.close()

    return jsonify(response)


@app.route('/zoos/<int:zoo_id>/favorite', methods=['POST'])
def favoriteZooDelete(zoo_id):
    
    response = {}

    #proper way to receive parameters in POST
    user = request.form.get('user_id')
    cur = get_db().execute("SELECT * FROM 'UserFanZoo' WHERE userID="+str(user)+" AND zooID="+str(zoo_id)+";")
    fan = cur.fetchone()
    if(fan != None):
        cur = get_db().execute("DELETE FROM UserFanZoo WHERE userID = "+ str(user) +" AND zooID = "+ str(zooID)+";")
        get_db().commit()

        if(cur.lastrowid == "" or cur.lastrowid == None):
            response["error"] = "Delete failed."
            cur.close()
            return jsonify(response)
        else:
            response["result"] = "ok"
            cur.close()
            return jsonify(response)
    else:
        response["error"] = "User is not fan of this zoo."
        return jsonify(response)


@app.route('/animals/<int:animal_id>/fan', methods=['POST'])
def favoriteAnimalDelete(animal_id):
    
    response = {}

    #proper way to receive parameters in POST
    user = request.form.get('user_id')

    cur = get_db().execute("SELECT * FROM 'UserFanAnimal' WHERE userID="+str(user)+" AND animalID="+str(animal_id)+";")
    fan = cur.fetchone()
    if(fan != None):
        cur = get_db().execute("DELETE FROM UserFanAnimal WHERE userID = "+ str(user) +" AND animalID = "+ str(animal_id)+";")
        get_db().commit()

        if(cur.lastrowid == "" or cur.lastrowid == None):
            response["error"] = "Delete failed."
            cur.close()
            return jsonify(response)
        else:
            response["result"] = "ok"
            cur.close()
            return jsonify(response)
    else:
        response["error"] = "User is not fan of this animal."
        return jsonify(response)

#-------------------------------------------------------------

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our IkemenGorilla server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)



