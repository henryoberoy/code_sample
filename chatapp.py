from telethon import TelegramClient
from telethon.tl.functions.auth import SignInRequest,SignUpRequest
from flask import Flask,request,jsonify,make_response,render_template,session
from flask_restful import Resource, Api
from telethon.errors.rpc_error_list import (
    RPCError, UnauthorizedError, PhoneCodeEmptyError, PhoneCodeExpiredError,
    PhoneCodeHashEmptyError, PhoneCodeInvalidError, LocationInvalidError,
    SessionPasswordNeededError, FileMigrateError, PhoneNumberUnoccupiedError,
    PhoneNumberOccupiedError, UsernameNotOccupiedError,PhoneNumberInvalidError
)
#from config import api_id,api_hash,username
import psycopg2

app = Flask(__name__)

@app.route('/admin/login', methods = ['POST'])
def login():
	myConnection = psycopg2.connect( host='host_ip_address', user='postgres', password='password', dbname='chatdb' )
	cur = myConnection.cursor()
	if(request.is_json):
		content = request.get_json()
		username = content['username']
		password = content['password']
		cur.execute("Select count(*) from account where username='"+username+"' and password = '"+password+"'")
		x=cur.fetchone()
		print(x)
		if(x[0]==1):
			return jsonify({"status":"login successful"})
		else:
			return jsonify({"status":"Invalid credentials"})

#for listing the app
@app.route('/')
@app.route('/edit')
def edit():
	con=psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password', database='chatdb')
	cur=con.cursor()
	cur.execute('select * from applist')
	data=cur.fetchall()
	app_name_list=[i[1] for i in data]
	print(app_name_list)
	return jsonify({'app_list':app_name_list})

# edit and save the app details
@app.route('/<appid>/save', methods=['POST'])
def save(appid):
        con = psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password',database='chatdb')
        cur = con.cursor()
        if(request.is_json):
                content = request.get_json()
                pageId = content['pageid']
                pageTitle = content['pagetitle']
                pageText_1 = content['pagetext_1']
                pageText_2 = content['pagetext_2']
                pageText_3 = content['pagetext_3']
                button_text_1 = content['button_text_1']
                button_text_2 = content['button_text_2']
                appid = content['appid']
                cur.execute("update app_pages set pageid = '"+pageId+"' , pagetitle = '"+pageTitle+"' , pagetext_1 = '"+pageText_1+"',pagetext_2 = '"+pageText_2+"',pagetext_3 = '"+pageText_3+"', button_text_1 = '"+button_text_1+"',button_text_2 = '"+button_text_2+"' where appid='"+appid+"'")
#                data = cur.fetchall()
                con.commit()
                con.close()
                return 'data edit and saved successfully'

# fetch a app based on its app id
@app.route('/edit/<appid>', methods=['POST'])
def editapp(appid):
	d={}
	con=psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password', database='chatdb')
	cur=con.cursor()
	cur.execute('select * from app_pages where appid = '+appid)
	data=cur.fetchall()
	d['pageid']=data[0][0]
	d['appid']=data[0][1]
	d['pageTitle']=data[0][2]
	d['pageText_1']=data[0][3]
	d['pageText_2']=data[0][4]
	d['pageText_3']=data[0][5]
	d['buttontext_1']=data[0][6]
	d['buttontext_2']=data[0][7]
	return jsonify(d)

# view all users of the app

@app.route('/viewAllUsers',methods = ['GET'])
def viewAllUsers():
	con = psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password',database='chatdb')
	cur = con.cursor()
	try:
		cur.execute("select * from users")
		data=cur.fetchall()
		l=[]
		for i in range(len(data)):
			x = {"phone":data[i][2],"app_id":data[i][1],"first_name":data[i][3],"last_name":data[i][4],"created_on":data[i][5],"last_login":data[i][6],"is_activated":data[i][7]}
			l.append(x)
	except Exception as e:
		x = jsonify({"Error":str(e)})
	return jsonify(l)

#to edit a user profile
@app.route('/editProfile',methods = ['PUT'])
def editProfile():
	con = psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password',database='chatdb')
	cur = con.cursor()
	try:
		if(request.is_json):
			content = request.get_json()
			phone = content['phone']
			first_name = content['first_name']
			last_name = content['last_name']
			is_activated = content['is_activated']
			try:
				cur.execute("update users set first_name = '"+first_name+"' , last_name = '"+last_name+"' , is_activated = '"+is_activated+"' where mobile_number='"+phone+"'")
				con.commit()
				con.close()
				x = jsonify({"status":"User Profile Edited Successfully"})
			except Exception as e:
				x = jsonify({"Error":e})
	except Exception as e:
		x = jsonify({"Error":"Bad Request"}),400
	return x

# get a channels pertaining to a app
@app.route('/getChannel/<appid>', methods=['POST'])
def getChannel(appid):
	l=[]
	x={}
	con=psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password', database='chatdb')
	cur=con.cursor()
#	appid = request.args.get('appid')
#	print('reached')
	cur.execute('select * from master_channel where appid = '+appid)
	data=cur.fetchall()
	for i in range(len(data)):
		x={'channelid':data[i][0], 'channel_name':data[i][1], 'channel_desc':data[i][2], 'created_on':data[i][3],'craeted_by':data[i][4],'enabled':data[i][5],'iamge_url':data[i][6]}
		l.append(x)
	return jsonify(l)


#get users of a channel
@app.route('/getUsers/<channelid>', methods=['POST'])
def getUsers(channelid):
	l=[]
	x={}
	userids=[]
	names=[]
	subscribe=[]
	con=psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password', database='chatdb')
	cur=con.cursor()
	cur.execute('select * from channel_user where channelid = '+channelid)
	data=cur.fetchall()
	cur.execute('select channel_name from master_channel where channelId='+channelid)
	data2=cur.fetchall()
	for i in range(len(data)):
		x={'id':data[i][0], 'channelid':data[i][1],'channel_name': data2[0][0],'userid':data[i][2],'appid':data[i][3], 'subscribed':data[i][4], 'unsubscribed':data[i][5]}
		userids.append(data[i][2])
		subscribe.append(data[i][4])
		for ids in userids:
			cur.execute('select first_name, last_name from users where id='+str(ids))
			data3=cur.fetchall()
			names.append(data3[0][0]+' '+data3[0][1])
		x['details']=[{'name':i[0], 'subscribedOn':i[1]} for i in zip(names, subscribe)]
		l.append(x)
	return jsonify(l)


# get all channels for a user
@app.route('/getChannelbyUserId/<userId>', methods=['POST'])
def getChannelbyUserId(userId):
	l=[]
	x={}
	con=psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password', database='chatdb')
	cur=con.cursor()
	cur.execute('select * from channel_user where userId = '+userId)
	data=cur.fetchall()
	for i in range(len(data)):
		x={'id':data[i][0], 'channelid':data[i][1], 'userid':data[i][2], 'appid':data[i][3], 'subscribed':data[i][4], 'unsubscribed':data[i][5]}
		l.append(x)
	return jsonify(l)


#search for a user
@app.route('/searchUser',methods = ['GET'])
def searchUser():
	con = psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password',database='chatdb')
	cur = con.cursor()
	try:
		search_string = str(request.args.get('query'))
		extended_search_string = search_string.split(' ')
		l=[]
		if(len(extended_search_string) == 1):
			cur.execute("SELECT * FROM users WHERE mobile_number LIKE '%"+search_string+"%' OR first_name ILIKE '"+search_string+"%' OR last_name ILIKE '"+search_string+"%'")
			data=cur.fetchall()
			if(len(data) == 0):
				return jsonify([]),400
			else:
				for i in range(len(data)):
					x = {"phone":data[i][2],"app_id":data[i][1],"first_name":data[i][3],"last_name":data[i][4],"created_on":data[i][5],"last_login":data[i][6],"is_activated":data[i][7]}
					l.append(x)
		elif(len(extended_search_string) == 2):
			cur.execute("SELECT * FROM users WHERE first_name ILIKE '"+extended_search_string[0]+"%' AND last_name ILIKE '"+extended_search_string[1]+"%'")
			data=cur.fetchall()
			if(len(data) == 0):
				return jsonify([]),400
			else:
				for i in range(len(data)):
					x = {"phone":data[i][2],"app_id":data[i][1],"first_name":data[i][3],"last_name":data[i][4],"created_on":data[i][5],"last_login":data[i][6],"is_activated":data[i][7]}
					l.append(x)
		else:
			return jsonify([]),400
	except Exception as e:
		x = jsonify({"Error":str(e)})
	con.close()
	return jsonify(l)


# edit a channel's info
@app.route('/editChannel/<channelid>', methods=['POST'])
def editChannel(channelid):
	con = psycopg2.connect(host='host_ip_address',port='5432',user='postgres',password='password',database='chatdb')
	cur = con.cursor()
	try:
		if(request.is_json):
			content = request.get_json()
			description = content['description']
			image_url = content['image_url']
			enabled = content['enabled']
			try:
				cur.execute("update master_channel set channel_description = '"+description+"' , image_url = '"+iamge_url+"' , enabled = '"+enabled+"' where channelId='"+channelid+"'")
				con.commit()
				con.close()
				x = jsonify({"status":"Channel Edited Successfully"})
			except Exception as e:
				x = jsonify({"Error":e})
	except Exception as e:
		x = jsonify({"Error":"Bad Request"}),400
	return x



#	app.run(host='0.0.0.0',port=5001)
app.run(port= 5000)
