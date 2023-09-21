import os
from flask import Flask,request,jsonify, json,send_from_directory
from flask_cors import CORS, cross_origin
from app import app
from db import my_col
from bson.objectid import ObjectId
from datetime import datetime
import asyncio
import jwt
from util import *
import sys

key = "secret"

@app.route('/api/save-question', methods=['POST'])
async def save_question():


    data = json.loads(request.data)

    userid = data['userid']
    contactnumber = data['contactnumber']
    done = data['done']
    data =data['data'] if 'data' in data else None
    #contactId = data['contactId']

    myquery = { "_id" :ObjectId(userid)}
    user = my_col('users').find_one(myquery)
    operator = {
        'user_id':user['_id'],
        'name':user['name'],
        'username':user['username']
    }

    #myquery = { "contact_id":ObjectId(contactid)}    
    myquery = { "contact_number":contactnumber,'user_id':ObjectId(userid),'schedule_time':None}
    contact_question = my_col('contact_question').find_one(myquery)

    if(contact_question == None):
        myquery = { "contact_number":contactnumber,'user_id':ObjectId(userid)}
        contact_question = my_col('contact_question').find_one(myquery)

    #print(contact_question)
    #sys.exit()

    contact_question_id = None 

    #print(data)
    #sys.exit()

    contactquery = {
          'user_id':ObjectId(userid),
          'mobile_no':contactnumber,
          'status':0
    }
    user_contact = my_col('user_contact').find_one(contactquery)
    user_contact_status = 0

    


    if(contact_question == None):
        contact_question = my_col('contact_question').insert_one({           
            'contact_number':contactnumber,
            #'contact_id':contactId,
            'user_id':ObjectId(userid),
            'operator':operator,
            'data':data,
            'done':done,
            "created_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        contact_question_id = str(contact_question.inserted_id)    
    else:
        if(data != None):
            #data = contact_question['data']
            if(user_contact != None):
                newvalues = { "$set": { 
                "status":done,
                #"dispose_status": None,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                } }
                user_contact_query = {"_id":user_contact['_id']}
                my_col('user_contact').update_one(user_contact_query, newvalues)
                user_contact_status = 1

            if(user_contact_status> 0):
                update_data = { "$set": 
                    { 
                    #'operator':operator,
                    'data':data,
                    'done':done,
                    "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    } 
                }
                my_col('contact_question').update_one(myquery, update_data)
        
        contact_question_id = str(contact_question['_id'])

    

    
    
    
    return jsonify({
        "contact_question_id":contact_question_id,
        
        #"userid":1
    })

@app.route('/api/get-question/<string:contactId>', methods=['GET'])
async def get_question(contactId:str):

    #myquery = { "contact_number":contactnumber,'user_id':ObjectId(userid)}
    myquery = {"_id":ObjectId(contactId)}
    contact_question = my_col('contact_question').find_one(myquery)

    data = {
        "contact_question_id":None,
        "data":None
    }
    if(contact_question!=None):
        data["contact_question_id"]= str(contact_question["_id"])
        data["data"]= contact_question["data"]

    return(data)



@app.route('/api/contact-status', methods=['POST'])
async def contact_status():
       if request.method == 'POST':
        data = json.loads(request.data)
        user_id = data['userid']
        dispose_status = data['dispose_status']
        mobile_no = data['mobile_no']

        contactquery = {
          'user_id':ObjectId(user_id),
          'mobile_no':mobile_no,
          'status':0
        }
        user_contact = my_col('user_contact').find_one(contactquery)
        user_contact_status = 0
        if(user_contact):
            newvalues = { "$set": { 
            "status":1,
            "dispose_status": dispose_status,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            } }
            myquery = {"_id":user_contact['_id']}
            my_col('user_contact').update_one(myquery, newvalues)
            user_contact_status = 1

        return({
            "user_contact_status":user_contact_status
        })

@app.route('/api/contact-running-status', methods=['POST'])
async def contact_running_status():
       if request.method == 'POST':
        data = json.loads(request.data)
        user_id = data['userid']
        dispose_status = data['dispose_status']        
        mobile_no = data['mobile_no']
        contact_question_id = data['questionid']

        data = data['data']

        contactquery = {
          'user_id':ObjectId(user_id),
          'mobile_no':mobile_no,
          'status':0
        }
        user_contact = my_col('user_contact').find_one(contactquery)

        myquery = { "_id":ObjectId(contact_question_id)}
        contact_question = my_col('contact_question').find_one(myquery)

        user_contact_status = 0
        contact_question_status = 0


        if(user_contact!=None and contact_question!=None):
            
            newvalues = { "$set": { 
            "status":1,
            "dispose_status": dispose_status,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            } }
            myquery = {"_id":user_contact['_id']}
            my_col('user_contact').update_one(myquery, newvalues)
            user_contact_status = 1

            update_data = { "$set": 
            { 
                
                'data':data,
                'done':1,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                } 
            }
            myquery = {"_id":contact_question['_id']}
            my_col('contact_question').update_one(myquery, update_data)
            contact_question_status = 1
        

            
            



        return({
            "user_contact_status":user_contact_status,
            "contact_question_status":contact_question_status
        })

@app.route('/api/list-contact-schedule-time', methods=['GET'])
async def list_contact_schedule_time():
    page = 1
    per_page = 10
    #total=my_col('contact_schedule').count_documents({})

    cursor_cat = my_col('contact_schedule').find({
        'picked':0,
        'schedule_time':{
            "$regex": datetime.now().strftime('%Y-%m-%d'),
        }
    }).skip(per_page*(page-1)).limit(per_page)
    #total_pages = int(total / per_page) * per_page
    list_cur = [todo for todo in cursor_cat]
    data_json = MongoJSONEncoder().encode(list_cur)
    data_obj = json.loads(data_json)
    return jsonify({
        "page":page,
        "per_page":per_page,
        #"total":total,
        #"total_pages":total_pages,
        "data":data_obj
    })


@app.route('/api/contact-schedule-time', methods=['POST'])
async def contact_schedule_time():
       if request.method == 'POST':
        data = json.loads(request.data)
        user_id = data['userid']
        #dispose_status = data['dispose_status']        
        mobile_no = data['mobile_no']
        contact_question_id = data['questionid']
        schedule_time = data['schedule_time']

        data = data['data']

        user_query = { "_id" :ObjectId(user_id)}
        user = my_col('users').find_one(user_query)
        operator = {
            'user_id':user['_id'],
            'name':user['name'],
            'username':user['username']
        }

        contactquery = {
          'user_id':ObjectId(user_id),
          'mobile_no':mobile_no,
          'status':0
        }
        user_contact = my_col('user_contact').find_one(contactquery)

        myquery = { "_id":ObjectId(contact_question_id)}
        contact_question = my_col('contact_question').find_one(myquery)

        schedule_query = {
            'user_id':ObjectId(user_id),
            'mobile_no':mobile_no,
            'schedule_time':schedule_time,
            'question_id':ObjectId(contact_question_id)
        }
        contact_schedule = my_col('contact_schedule').find_one(schedule_query)


        user_contact_status = 0
        contact_question_status = 0
        contact_schedule_status = 0
        contact_schedule_id = None

        if(contact_schedule == None):
            contact_schedule = my_col('contact_schedule').insert_one({           
            'contact_number':mobile_no,
            #'contact_id':contactId,
            'user_id':ObjectId(user_id),
            'operator':operator,
            'schedule_time':schedule_time,
            'question_id':ObjectId(contact_question_id),
            "created_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'picked':0,
            'picked_by':None
            
            })
            contact_schedule_status = 1
            contact_schedule_id = str(contact_schedule.inserted_id)

        if(user_contact!=None and contact_question!=None):
            
            newvalues = { "$set": { 
            "status":2,
            #"dispose_status": dispose_status,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            } }
            myquery = {"_id":user_contact['_id']}
            my_col('user_contact').update_one(myquery, newvalues)
            user_contact_status = 1

            update_data = { "$set": 
            { 
                
                'data':data,
                'done':0,
                'schedule_time':schedule_time,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                } 
            }
            myquery = {"_id":contact_question['_id']}
            my_col('contact_question').update_one(myquery, update_data)
            contact_question_status = 1
        

            
            



        return({
            "user_contact_status":user_contact_status,
            "contact_question_status":contact_question_status,
            "contact_schedule_status":contact_schedule_status,
            "contact_schedule_id":contact_schedule_id
        })



@app.route('/api/pick-schedule', methods=['POST'])
async def pick_schedule():


    data = json.loads(request.data)

    userid = data['userid']
    contactnumber = data['contactnumber']
    questionid = data['questionid']
    scheduleid = data['scheduleid']
    #contactId = data['contactId']

    
    #schedule information
    schedule_query = {
        '_id':ObjectId(scheduleid)        
    }
    contact_schedule = my_col('contact_schedule').find_one(schedule_query)

    #contact question information
    contact_question_query = {
        '_id':ObjectId(questionid)
    }
    contact_question = my_col('contact_question').find_one(contact_question_query)
    contact_question_id = None
    user_contact_id = None
    contact_schedule_status = 0

    #now we will insert all new 
    if(contact_question!= None and contact_schedule!=None):
        #inserted user contact
        contactquery = {
          #'user_id':ObjectId(userid),
          'mobile_no':contactnumber,
          'status':0
        }
        user_contact = my_col('user_contact').find_one(contactquery)
        print(userid)
        #print(ObjectId(user_contact['user_id']) == ObjectId(userid))
        #sys.exit()
        if(user_contact == None):
            user_contact = my_col('user_contact').insert_one({
                'user_id':ObjectId(userid),
                'status':0,
                'dispose_status':None,
                'mobile_no':contactnumber,
                'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            user_contact_id = str(user_contact.inserted_id)
        else:
            if(ObjectId(user_contact['user_id']) == ObjectId(userid)):
                userid = str(user_contact['user_id'])
                user_contact_id = str(user_contact['_id'])
            else:
                user_contact_id = None

        #print(ObjectId(user_contact['user_id']) == ObjectId('64b91bb7dd9bb78cbdce7a31'))
        #sys.exit()

        #picker information
        user_query = { "_id" :ObjectId(userid)}
        user = my_col('users').find_one(user_query)
        picked_by = {
            'user_id':user['_id'],
            'name':user['name'],
            'username':user['username']
        }
        #print(picked_by)    
        #sys.exit()

        #inserted contact question

        myquery = { 
        "contact_number":contactnumber,
        #'user_id':ObjectId(userid),
        "schedule_time":None}
        already_contact_question = my_col('contact_question').find_one(myquery)

        
        if(already_contact_question == None):
            contact_question = my_col('contact_question').insert_one({           
                'contact_number':contactnumber,
                #'contact_id':contactId,
                'user_id':ObjectId(userid),
                'operator':picked_by,
                'data':contact_question['data'],
                'done':0,
                "schedule_time":None,
                "created_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at":datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            contact_question_id = str(contact_question.inserted_id)
        else:
            #print(ObjectId(already_contact_question['user_id']) == ObjectId('64b91bb7dd9bb78cbdce7a31'))
            #sys.exit()
            if(ObjectId(already_contact_question['user_id']) == ObjectId(userid)):
                userid = str(contact_question['user_id'])
                contact_question_id = str(contact_question["_id"])
            else:
                contact_question_id = None
        
        
        #print(contact_question_id)
        #sys.exit()
        
        #print(userid)
        #print(picked_by)
        #sys.exit()

        #updating the schedules
        if(user_contact_id!=None and contact_question_id!=None):
            newvalues = { "$set": { 
                "picked":1,
                'picked_by': picked_by,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            } }
            
            my_col('contact_schedule').update_one(schedule_query, newvalues)
            contact_schedule_status = 1

        #print(contact_schedule_status)
        #sys.exit()
            
    
    
    
    return jsonify({
        "user_contact_id":user_contact_id,
        "contact_question_id":contact_question_id,
        "contact_schedule_status":contact_schedule_status
        
        #"userid":1
    })