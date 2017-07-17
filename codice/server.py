# -*- coding: utf-8 -*-
from config import *
import sqlite3
import socket
import threading
import sys
import numpy
import hashlib
import datetime
from libs import *

class User(object):
	def __init__(self, username, password,connection):
		self.connection = connection
		self.username = username
		self.password = hashlib.md5(password).hexdigest()
		# self.users = {'user1':'pass', 'user2':'pass', 'user3':'pass'}

	def login(self):
		if(DEBUG):
			print("[DEBUG] trying to signin usr -> " + str(self.username))
		
		if(self.isLogged()):
			self.response('alreadylogged')
		elif(self.isRegistered()):
			self.logUser()
			self.response('ok')
		else:
			self.response('notknown')

		if(DEBUG):
			print("[DEBUG] usrsLogged -> " + str(playersLogged))

	def logUser(self):
		playersLogged[self.username] = self.connection

	def isLogged(self):
		return self.username in playersLogged.keys()

	def isRegistered(self):
		sql = "SELECT * FROM users WHERE usr='"+self.username+"' AND psw='"+self.password+"'"

		conn = sqlite3.connect('data.db')
		cursor = conn.cursor()    

		cursor.execute(sql)

		count = len(cursor.fetchall())
		cursor.close()

		if(count!=0):
			return True

		return False

	def response(self, msg):
		response = {"response":msg}
		if(DEBUG):
			print "[DEBUG] response to client: " + json.dumps(response)

		self.connection.send(message(response).encode())

class UserConnection(object):
	def __init__(self, username, connection):
		self.connection = connection
		self.username = username

	def readyToPlay(self):
		if(DEBUG):
			print("[DEBUG] usr want to play -> " + str(self.username))
		
		self.addToReady()
		self.response('waiting')

		if(DEBUG):
			print("[DEBUG] usrsReady -> " + str(playersReady))

		return True

	def addToReady(self):
		playersReady.append(self.username)

	def response(self, msg):
		response = {"response":msg}
		if(DEBUG):
			print "[DEBUG] response to client: " + json.dumps(response)

		self.connection.send(message(response).encode())

class Table(object):
	def __init__(self, usr):
		self.connection = playersLogged[usr]
		self.get()

	def get(self):
		sql = "SELECT usr,games,won,lastGame FROM users ORDER BY won desc"

		conn = sqlite3.connect('data.db')
		cursor = conn.cursor()
		cursor.execute(sql)
		users = cursor.fetchall()
		cursor.close()

		self.response(users)

	def response(self, msg):
		response = {"response":'table','data':msg}
		if(DEBUG):
			print "[DEBUG] response to client: " + json.dumps(response)

		self.connection.send(message(response).encode())

class Database(object):
	def __init__(self):
		self.conn = sqlite3.connect('data.db')
		
	def executeQuery(self,sql):
		cursor = self.conn.cursor()
		cursor.execute(sql)
		self.conn.commit()
		return cursor.fetchall()

	def close(self):
		self.conn.close()

class Game(object):
	def __init__(self, data):
		self.data = data
		self.winnerCases = [['1','2','3'],['4','5','6'],['7','8','9'],['1','4','7'],['2','5','8'],['3','6','9'],['1','5','9'],['3','5','7']]
		self.play()
	
	def play(self):
		for winnerCase in self.winnerCases:
			done = self.data['play'][self.data['last_play']['usr']]['done']
			# print "done: " + str(done)

			intersect = numpy.intersect1d(done,winnerCase)
			# print "intersect: " + str(intersect)
			
			if(numpy.array_equal(intersect,winnerCase)):
				self.data['status'] = "end"
				self.data['winner'] = self.data['last_play']['usr']

				##notify all players
				playersNames = self.data['play'].keys()
				self.response(self.data, playersLogged[playersNames[0]])
				self.response(self.data, playersLogged[playersNames[1]])

				#update users in sql
				db = Database()
				
				sql = "UPDATE users SET games = games + 1, lastGame='" + str(datetime.datetime.now()) + "' WHERE usr='"+playersNames[0]+"' OR usr='"+playersNames[1]+"';"
				print "sql: " + sql
				db.executeQuery(sql)			

				sql = "UPDATE users SET won = won + 1 WHERE usr='"+self.data['last_play']['usr']+"';"
				print "sql: " + sql
				db.executeQuery(sql)

				db.close()

				return True

		playersNames = self.data['play'].keys()
		if(len(self.data['play'][playersNames[0]]['done']) + len(self.data['play'][playersNames[1]]['done']) == 9):
			##notify all players that no one has won
			self.data['status'] = "end"
			self.data['winner'] = 'none'

			self.response(self.data, playersLogged[playersNames[0]])
			self.response(self.data, playersLogged[playersNames[1]])

			#update users in sql
			db = Database()
			
			sql = "UPDATE users SET games = games + 1, lastGame='" + str(datetime.datetime.now()) + "' WHERE usr='"+playersNames[0]+"' OR usr='"+playersNames[1]+"';"
			print "sql: " + sql
			db.executeQuery(sql)
			db.close()

			return True


		##notify next player to play
		playersNames = self.data['play'].keys()
		nextPlayer = playersNames[0]
		if(playersNames[1] != self.data['last_play']['usr']):
			nextPlayer = playersNames[1]

		self.response(self.data, playersLogged[nextPlayer])
		return False

	def response(self, msg, connection):
		response = {"response":"game","data":self.data}
		if(DEBUG):
			print "[DEBUG] response to client: " + json.dumps(response)

		connection.send(message(response).encode())

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(MAX_QUEUE)
        while True:
            client, address = self.sock.accept()
            # client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()
            # self.listenToClient(client,address)
    def listenToClient(self, client, address):
		global playersReady
		global playersLogged

		size = 1024
		while True:
			# try:
			data = client.recv(size)
			if data:
				print "\n"
				if(DEBUG):
					print "[DEBUG] Received: " + str(data) + " from " + str(address)

				data = message(data).decode()
				print "Decoded: " + str(data)
				if(DEBUG):
					print("[DEBUG] " + str(data))

				if(data['cmd']=='login'):
					User(data['data']['usr'],data['data']['psw'],client).login()
				elif(data['cmd']=='play'):

					res = UserConnection(data['data']['usr'],client).readyToPlay()

					## Check if there're at least 2 clients in ready status
					if(res and len(playersReady)>=2):
						# playersNames = playersReady.keys()
						
						msg = {"cmd":"game","data":{"player":"O","first":0,"play":{playersReady[0]:{"player":"O","done":[]},playersReady[1]:{"player":"X","done":[]}},"last_play":None,'status':'start'}}
						playersLogged[playersReady[0]].send(message(msg).encode())
						
						msg['data']['first'] = 1
						msg['data']['player'] = "X"
						playersLogged[playersReady[1]].send(message(msg).encode())

						playersReady[0:2] = []

				elif(data['cmd']=='game'):
					game = Game(data['data'])
				elif(data['cmd']=='table'):
					Table(data['data']['usr'])
				elif(data['cmd']=='exit'):
					
					playersLogged.pop(data['data']['usr'], None)
					
					if(data['data']['usr'] in playersReady):
						playersReady.remove(data['data']['usr'])

				else:
					if(DEBUG):
						print("[DEBUG] cmd not known")

			else:
				if(DEBUG):
					print("[DEBUG] a client is disconnected")

				if(len(playersLogged)==1):
					playersLogged = {}
				# playersReady = []
				return False
					#todo manage if is playing or is in ready status

			# except Exception as e:
			# 	print str(e)
			# 	client.close()
			# 	return False

if __name__ == "__main__":
  		
	sql = 'create table if not exists users (usr TEXT, psw TEXT, games INT, won INT, lastGame TIMESTAMP, PRIMARY KEY (usr))'
	db = Database()
	db.executeQuery(sql) 

	sql = "INSERT OR IGNORE INTO users(usr,psw,games,won,lastGame) VALUES('user1','1a1dc91c907325c69271ddf0c944bc72',0,0,0);"
	db.executeQuery(sql) 
	sql = "INSERT OR IGNORE INTO users(usr,psw,games,won,lastGame) VALUES('user2','1a1dc91c907325c69271ddf0c944bc72',0,0,0);"
	db.executeQuery(sql) 
	sql = "INSERT OR IGNORE INTO users(usr,psw,games,won,lastGame) VALUES('user3','1a1dc91c907325c69271ddf0c944bc72',0,0,0);"
	db.executeQuery(sql)

	if(len(sys.argv) == 2 and sys.argv[1] == 'flushstats'):
		sql = "UPDATE users SET games=0,won=0,lastGame=0;"
		db.executeQuery(sql)

	db.close()

	playersLogged= {} # players logged
	playersReady = [] # players ready to play


	playersLogged= {} # players logged
	playersReady = [] # players ready to play

	ThreadedServer(SERVER_HOST,SERVER_PORT).listen()
