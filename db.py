import pymongo
from dotenv import load_dotenv
import os
load_dotenv()

#MONGO_HOST=os.getenv("MONGO_HOST") #'192.168.10.55
#MONGO_PORT=os.getenv("MONGO_PORT") #'64000

MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
#print(MONGO_PORT)
#exit()
myclient = pymongo.MongoClient(
    host = f"{MONGO_HOST}:{MONGO_PORT}",
    username=MONGO_USER,
    password=MONGO_PASSWORD
)
mydb = myclient["question-data"]

def my_col(name):
    return mydb[name]