from flask import Flask, request
from numpy import double
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
uri = "mongodb+srv://admin:admin@ecosorter.x4owlln.mongodb.net/?retryWrites=true&w=majority&appName=EcoSorter"
disc_gaz = 0
disc_electricitate = 0
ok = False
@app.route("/", methods=['POST'])
def showHomePage():
    # response from the server
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        points = request.form.get('points')
        discount_gaz = request.form.get('discount_gaz')
        discount_ele = request.form.get('discount_electricitate')
        print("Received data: ", user, " ", password, " ", points, " ", discount_gaz, " ", discount_ele)

        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            mydb = client["EcoSorter"]
            mycol = mydb["accounts"]
            mydict = {"username": user, "password": password, "points": points, "discount_gaz": discount_gaz, "discount_electricitate": discount_ele}
            x = mycol.insert_one(mydict)
        except Exception as e:
            print(e)
    return "Hello World"
@app.route("/redeem", methods=['POST'])
def redeem():
    if request.method == 'POST':
        res = "ok"
        username = request.form.get('username')
        cod = request.form.get('code')
        print("Received data: ", username, " ", cod)
        # Here you can add the logic to validate the username and password
        #Search if this code exists in the colection Redeen_code
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            my_query = {"code": (int)(cod)}
            mydb = client["EcoSorter"]
            mycol = mydb["Redeem_code"]
            mydoc = mycol.find(my_query)
            mydoc = list(mydoc)
            print(len(mydoc))
            if(len(mydoc)==0):
                return "Invalid code"
            else:
                #Add the points to the user
                #delte the code from the collection
                mycol.delete_one(my_query)

                mycol = mydb["accounts"]
                myquery = {"username": username}
                mydoc = mycol.find(myquery)
                mydoc = list(mydoc)
                pointes = (int)(mydoc[0]["points"])
                pointes += 100
                print(pointes)
                #Update with the new points
                myquery = {"username": username}
                newvalues = {"$set": {"points": pointes}}
                mycol.update_one(myquery, newvalues)
                print(mydoc[0]["points"])
                res = (str)(pointes)
        except Exception as e:
            print(e)
            res = "Error"
        print(res)
        return res
@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Here you can add the logic to validate the username and password
        # and return a response accordingly
        print("Received data: ", username, " ", password)
        return "Login successful"
    else:
        username = request.args.get('username')
        password = request.args.get('password')
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            mydb = client["EcoSorter"]
            mycol = mydb["accounts"]
            #Get all the documents in the collection that has the username and password
            myquery = {"username": username, "password": password}
            #print(myquery)
            mydoc = mycol.find(myquery)
            #Get the number of documents that has the username and password
            mydoc = list(mydoc)

            if mydoc== []:
                return "Invalid username or password"
            else:

                ponts = mydoc[0]["points"]
                disc_gaz = mydoc[0]["discount_gaz"]
                disc_electricitate = mydoc[0]["discount_electricitate"]
                print("Points: ", ponts)
                print("Discount gaz: ", disc_gaz)
                print("Discount electricitate: ", disc_electricitate)
                #Get all the data from location collection
                mycol = mydb["location"]
                mydoc = mycol.find()
                mydoc = list(mydoc)
                Lat_and_Long = {}
                for x in mydoc:
                    print(x['latitude'], " ",  x['longitude'] )
                    Lat_and_Long[x['latitude']] = x['longitude']
                print("Login successful ")
                return   str(ponts)
                #yield "Points: " + str(ponts) + "\n"

        except Exception as e:
            print(e)
            return "Error"

@app.route("/red", methods=['GET'])
def gaz_red():
    if request.method == 'GET':
        #Get all the data from location collection
        username = request.args.get('user')
        points = request.args.get('points')
        red_gaz = request.args.get('red_gaz')
        red_electricitate = request.args.get('red_electricitate')
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            mydb = client["EcoSorter"]
            mycol = mydb["accounts"]
           #Update with the new points
            myquery = {"username": username}
            print("Points: ", points)
            print("Red gaz: ", red_gaz)
            print("Red electricitate: ", red_electricitate)
            poitterus_updateus = (double)(points)- (double)(red_gaz) - (double)(red_electricitate)
            #Set precision of 4 decimals
            poitterus_updateus = round(poitterus_updateus, 4)
            newvalues = {"$set": {"points": poitterus_updateus, "discount_gaz": red_gaz, "discount_electricitate": red_electricitate}}
            mycol.update_one(myquery, newvalues)
            print("Updated")
            ok = False
            return "Updated"
        except Exception as e:
            print(e)
            return "Error"

if __name__ == '__main__':
    app.run(host="0.0.0.0")
        #ngrok http --domain=alien-amused-especially.ngrok-free.app http://192.168.100.31:5000
#host="192.168.110.23"d