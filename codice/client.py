# -*- coding: utf-8 -*-
from config import *
from socket import *
import time
import signal
from beautifultable import BeautifulTable
from libs import *

def menu():

	while 1:
		print("MENU\n 1.Gioca\n 2.Classifica\n 3.Esci")
		ans=raw_input("Cosa vuoi fare? ")
		if ans=="1":
			return 'play'
		elif ans=="2":
			return 'table'
		elif ans=="3":
			return 'exit'
		else:
			print("\n Scelta non riconosciuta")

def getPlayerMove(freeSlots):
	if(DEBUG):
		print("[DEBUG] Slot liberi: " + str(freeSlots))

	while 1:
		ans=raw_input("Mossa? ")
		if ans in freeSlots:
			return ans
		else:
			print("\n Mossa non valida")

def showGrid(data):
    # This function prints out the board that it was passed.
	grid = ["","1","2","3","4","5","6","7","8","9"]
	freeSlots = ["1","2","3","4","5","6","7","8","9"]

	playersNames = data['play'].keys()

	for index in data['play'][playersNames[0]]['done']:
		grid[int(index)] = data['play'][playersNames[0]]['player']
		freeSlots.remove(index)

	for index in data['play'][playersNames[1]]['done']:
		grid[int(index)] = data['play'][playersNames[1]]['player']
		freeSlots.remove(index)

	# # "grid" is a list of 10 strings representing the board (ignore index 0)
	print('   |   |')
	print(' ' + grid[1] + ' | ' + grid[2] + ' | ' + grid[3])
	print('   |   |')
	print('-----------')
	print('   |   |')
	print(' ' + grid[4] + ' | ' + grid[5] + ' | ' + grid[6])
	print('   |   |')
	print('-----------')
	print('   |   |')
	print(' ' + grid[7] + ' | ' + grid[8] + ' | ' + grid[9])
	print('   |   |')


	return freeSlots

def sendExit():
	msg = {"cmd":"exit","data":{"usr":usr}}
	clientSocket.send(message(msg).encode())
	clientSocket.close()
	exit(1)

def sigint_handler(signum, frame):
    sendExit()

if __name__ == '__main__':
	signal.signal(signal.SIGINT, sigint_handler)
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((SERVER_HOST,SERVER_PORT))

	msg = {'response':None}
	while(msg['response'] != 'ok'):
		usr = raw_input('usr: ')
		psw = raw_input('psw: ')

		msg = {"cmd":"login","data":{"usr":usr, "psw":psw}}

		clientSocket.send(message(msg).encode())
		msg = clientSocket.recv(1024)
		
		if(DEBUG):
			print '[DEBUG] Dal server: ', msg

		msg = message(msg).decode()
		
		if(DEBUG):
			print '[DEBUG] Decoded: ', json.dumps(msg)
		
		print "\n"

	# Player logged
	print("Ciao " + usr + " .." + "\n")

	cmd = menu()
	while(cmd != 'exit'):
		msg = {"cmd":cmd,"data":{"usr":usr}}
		clientSocket.send(message(msg).encode())
		response = clientSocket.recv(1024)
		response = message(response).decode()
		
		if(DEBUG):
			print ("[DEBUG] from server: " + json.dumps(response))

		if(cmd == 'table'):
			table = BeautifulTable()
			table.column_headers = ["usr","games","won","lastGame"]

			for row in response['data']:
				table.append_row(row)

			print table
		elif(cmd == 'play'):
			if(response['response'] == 'waiting'):
				print ".. aspettando un avversario .." + "\n"
				
				response = {'data':{'status':'inplay'}}
				
				while(1):
					response = clientSocket.recv(1024)
					response = message(response).decode()
					if(DEBUG):
						print "[DEBUG] " + str(response)

					if(response['data']['status'] == 'start'):
						print "Trovato avversario"
						print "Sei il giocatore " + response['data']['player']
						if(response['data']['first']==1):
							print "Il primo turno è il tuo!"
							freeSlot = showGrid(response['data'])
							move = getPlayerMove(freeSlot)

							#prepare the message for the server
							response.pop("response",None)
							response["data"].pop('player',None)
							response["data"].pop('first',None)
							response["cmd"] = 'game'
							response["data"]["status"] = 'inplay'
							response["data"]["play"][usr]['done'].append(move)
							response["data"]["last_play"] = {}
							response["data"]["last_play"]["move'"] = move
							response["data"]["last_play"]["usr"] = usr

							clientSocket.send(message(response).encode())

						else:
							print ".. Aspettando la prima mossa dell'avversario .."
					elif(response['data']['status'] == 'inplay'):
						freeSlot = showGrid(response['data'])
						move = getPlayerMove(freeSlot)

						#prepare the message for the server
						response.pop('response',None)
						response['data'].pop('player',None)
						response['cmd'] = 'game'
						response['data']['status'] = 'inplay'
						response['data']['play'][usr]['done'].append(move)
						response['data']['last_play']['move'] = move
						response['data']['last_play']['usr'] = usr
						clientSocket.send(message(response).encode())
					else:
						break	
		

				showGrid(response['data'])
				if(response['data']['winner'] == 'none'):
					print "Nessun vincitore!"
				elif(response['data']['winner'] == usr):
					print "Complimenti! Sei il vincitore!"
				else:
					print "Mi dispiace, non hai vinto!"

			else:
				print(response['response'])
		
		cmd = menu()

	sendExit()