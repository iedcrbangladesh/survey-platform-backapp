import os
from flask import Flask,request,jsonify, json
from flask_cors import CORS, cross_origin
from app import app
from db import my_col
from bson.objectid import ObjectId
from util import *
from datetime import datetime

TOKEN_EXPIRATION=os.environ["TOKEN_EXPIRATION"]

#CORS(app)
import jwt
key = "secret"
@app.route("/api/users", methods=['GET'])
def list_user():
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    total=my_col('users').count_documents({"role":2})
    cursor = my_col('users').find({"role":2}).skip(per_page*(page-1)).limit(per_page)
    total_pages = int(total / per_page) * per_page
    #list_cur = list(cursor)
    #json_data = dumps(list_cur, indent = 2) 
    data_json = MongoJSONEncoder().encode(list(cursor))
    data_obj = json.loads(data_json)


    return jsonify({
        "page":page,
        "per_page":per_page,
        "total":total,
        "total_pages":total_pages,
        "data":data_obj
    })

@app.route("/api/users/<string:id>", methods=['GET'])
def view_user(id:str):
    user = my_col('users').find_one(
        {"_id":ObjectId(id)},
        {"_id":0,"password":0}
        )


    return jsonify({
        "user":user
    })

@app.route("/api/user-create", methods=['POST'])
def create_user():
    if request.method == 'POST':
      name  =  request.form.get('name') 
      username = request.form.get('username')
      email  =  request.form.get('email')
      password  =  request.form.get('password')
      #exit()
      x = my_col('users').insert_one({
        "name":name,
        "username":username,
        "email":email,
        "password":password,
        "role":2,
        "created_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })


    return jsonify({
        "userid":str(x.inserted_id)
    })


@app.route("/api/user-create/<string:id>", methods=['POST'])
def update_user(id:str):
    if request.method == 'POST':
      name  =  request.form.get('name')
      username = request.form.get('username')
      email  =  request.form.get('email')
      password  =  request.form.get('password')

      myquery = { "_id" :ObjectId(id)}
      newvalues = { "$set": { 
          "name": name,
          "username":username,
          "email":email,
          "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
          } 
       }
      if(password != ""):
         newvalues = { "$set": { 
             "name": name,
             "username":username,
             "email":email,
             "password":password, 
             "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S') } }

      
      my_col('users').update_one(myquery, newvalues)
      


    return jsonify({
        "user":my_col('users').find_one(myquery,{"_id":0,"password":0})
    })

@app.route("/api/login", methods=['POST'])
def login_user():
   if request.method == 'POST':
        data = json.loads(request.data)

        email = data['email']
        password = data['password']

        myquery = { "$or":[
            {"email" :email},
            {"username":email}
        ]}
        global key

        user = my_col('users').find_one(myquery)
        
        #check user is already logged in
        if(user!=None and user['token'] != None):
            print(user)
            return({
                "user":None
            })

        #check user already logged in

        if(user!=None and "suspended_at" in user and user["suspended_at"] != None):
            

            return({
                "user":None
            })


        if(user !=None and user['password'] == password):
            #data_json = MongoJSONEncoder().encode(user)
            #data_obj = json.loads(data_json)
            
            id = str(user["_id"])

            token = jwt.encode({"user": id}, key, algorithm="HS256")
            #print(token)
            newvalues = { "$set": { "token": token } }
            myquery = { "_id" :ObjectId(user["_id"])}

            my_col('users').update_one(myquery, newvalues)
            return jsonify({
             
                 "localId":id,
                 "displayName":user["name"],
                 "idToken":token,
                 "role":user["role"],
                 "expiresIn":TOKEN_EXPIRATION
             
           })
        
        if(user !=None and user['password'] != password):
            return({
                #"user":None,
                "password":None
            })    
        
        return({
        "user":None
        })

@app.route("/api/login-user", methods=['POST'])
def login_user_staff():
   if request.method == 'POST':
        data = json.loads(request.data)

        email = data['email']
        password = data['password']

        myquery = { 
        'role':2,
        "$or":[
            {"email" :email},
            {"username":email}
        ]}
        global key

        user = my_col('users').find_one(myquery)
        #print(user)
        #one login at a time
        '''
        if(user!=None and user['token'] != None):
            print(user)
            return({
                "user":None
            })
        '''
        #end one login at a time

        if(user!=None and "suspended_at" in user and user["suspended_at"] != None):
            return({
                "user":None
            })


        if(user !=None and user['password'] == password):
            #data_json = MongoJSONEncoder().encode(user)
            #data_obj = json.loads(data_json)
            
            id = str(user["_id"])

            token = jwt.encode({"user": id}, key, algorithm="HS256")
            #print(token)
            newvalues = { "$set": { "token": token } }
            myquery = { "_id" :ObjectId(user["_id"])}

            my_col('users').update_one(myquery, newvalues)

            #set log
            logquery = {
                'user_id':user["_id"]                                
            }
            user_log = my_col('user_log').find_one(logquery)            
                
            if((user_log and ('log_in_time' in user_log and 'log_out_time' in user_log)) or user_log == None):
                my_col('user_log').insert_one({
                  'user_id':user["_id"],
                   'log_in_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   'log_out_time':None

                })


                                    
            #print(TOKEN_EXPIRATION)
            #end set log
            return jsonify({
             
                 "localId":id,
                 "displayName":user["name"],
                 "idToken":token,
                 "role":user["role"],
                 "expiresIn":TOKEN_EXPIRATION
             
           })
        
        if(user !=None and user['password'] != password):
            return({
                #"user":None,
                "password":None
            })    
        
        return({
        "user":None
        })

@app.route("/api/userby/<string:tag>/<string:userid>/<string:token>", methods=['GET'])
def userby(tag:str,userid:str,token:str):
    decoded = jwt.decode(token, key, algorithms="HS256")
    user = userid if decoded["user"] == userid else None
    return({
        "user":user
    })

@app.route("/api/userbyemail/<string:userid>", methods=['POST'])
def userbyEmail(userid:str):
    if request.method == 'POST':
        data = json.loads(request.data)
        email = data['email']
        #print(token)
        #exit()
        
        unexpected_token_value = ["undefined", "null"]
        user_self = None
        if(userid not in unexpected_token_value):
            myquery = { "_id" :ObjectId(userid)}
            user_self = my_col('users').find_one(myquery)
            
        myquery = { "email" :email}
        user = my_col('users').find_one(myquery)

        found = True

        if(user_self and email == user_self['email']):
            found = True
        elif((user and user_self) and email != user_self['email']):
            found = False
        elif(user and user_self == None):
            found = False        
        elif(user== None and user_self == None):
            found=True
        
    return({
        "success":found
    })

@app.route("/api/userbyusername/<string:userid>", methods=['POST'])
def userbyUsername(userid:str):
    if request.method == 'POST':
        data = json.loads(request.data)
        username = data['username']
        #print(token)
        #exit()
        
        unexpected_token_value = ["undefined", "null"]
        user_self = None
        if(userid not in unexpected_token_value):
            myquery = { "_id" :ObjectId(userid)}
            user_self = my_col('users').find_one(myquery)
            
        myquery = { "username" :username}
        user = my_col('users').find_one(myquery)

        found = True

        if(user_self and ('username' in user_self and  username == user_self['username'])):
            found = True
        elif((user and user_self) and ('username' in user_self and username != user_self['username'])):
            found = False
        elif(user and user_self == None):
            found = False        
        elif(user== None and user_self == None):
            found=True
        
    return({
        "success":found
    })



@app.route("/api/logout", methods=['POST'])
def logout_user():
   if request.method == 'POST':
        data = json.loads(request.data)

        token = data['token']
        global key
        
        decoded = jwt.decode(token, key, algorithms="HS256")
        print(decoded)
        if(decoded):
            myquery = { "_id" :ObjectId(decoded['user'])}
            newvalues = { "$set": { "token": None } }
            my_col('users').update_one(myquery, newvalues)
            return({"logout":1})
        
        return({"logout":0})


@app.route("/api/logout-staff", methods=['POST'])
def logout_user_staff():
   if request.method == 'POST':
        data = json.loads(request.data)

        token = data['token']
        #logout_by_click = data['logout_by_click']
        global key
        
        decoded = jwt.decode(token, key, algorithms="HS256")
        print(decoded)
        if(decoded):
            myquery = { "_id" :ObjectId(decoded['user'])}
            newvalues = { "$set": { "token": None } }
            my_col('users').update_one(myquery, newvalues)
            # set log user
            logquery = {
                'user_id':ObjectId(decoded['user']),
                'log_out_time':None                                
            }
            user_log = my_col('user_log').find_one(logquery)
            #print(user_log)

            if(user_log!=None):
                            
                #if('log_out_time' not in user_log):
                    print(user_log)

                    log_out_time = datetime.now()

                    log_in_time = datetime.strptime(user_log['log_in_time'],'%Y-%m-%d %H:%M:%S')

                    log_in_logout_diff = log_out_time - log_in_time

                    newvalues = { "$set": 
                        { 
                            "log_out_time": log_out_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "duration" :int(log_in_logout_diff.total_seconds()),
                            #"logout_by_click":logout_by_click
                        } 
                    }
                    my_col('user_log').update_one(logquery, newvalues)
                

            #end upfate log user

            return({"logout":1})
        
        return({"logout":0})


@app.route('/api/suspend_user/<string:id>/<string:action>', methods=['GET'])
async def suspend_user(id:str,action:str):
    myquery = { "_id" :ObjectId(id)}
    user = my_col('users').find_one(myquery)
    message = user["name"]+" suspended succssfully"
    newvalues = { "$set": { 
        "suspended_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  
        } }
    
    if(action == '1'):
        newvalues = { "$set": { 
        "suspended_at":None,
        "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  
        } }
    
    my_col('users').update_one(myquery, newvalues)
    count_done=1

    return jsonify({
        "message":message,
        "done_delete":count_done

    })