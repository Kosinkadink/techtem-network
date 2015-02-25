#!/usr/bin/python2
import sys, socket, select, os, threading
from datetime import datetime
from random import randint
from time import sleep
from hashlib import sha1

#initialization of the server
host = ''
socketlist = []
port = 9009
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran

if not os.path.exists(__location__+'/resources'): os.makedirs(__location__+'/resources')
if not os.path.exists(__location__+'/resources/protocols'): os.makedirs(__location__+'/resources/protocols') #for protocol scripts
if not os.path.exists(__location__+'/resources/cache'): os.makedirs(__location__+'/resources/cache') #used to store info for protocols and client
if not os.path.exists(__location__+'/resources/programparts'): os.makedirs(__location__+'/resources/programparts') #for storing protocol files
if not os.path.exists(__location__+'/resources/uploads'): os.makedirs(__location__+'/resources/uploads') #used to store files for upload
if not os.path.exists(__location__+'/resources/downloads'): os.makedirs(__location__+'/resources/downloads') #used to store downloaded files

if os.path.exists(__location__+'/resources/protocols/protlist.txt'):
	os.remove(__location__+'/resources/protocols/protlist.txt')
if not os.path.exists(__location__+'/resources/protocols/protlist.txt'):
	with open(__location__+'/resources/protocols/protlist.txt', "a") as protlist: #file used for identifying what protocols are available
		pass

### server specific files start ###
if not os.path.exists(__location__+'/resources/programparts/radchat'): os.makedirs(__location__+'/resources/programparts/radchat')
if not os.path.exists(__location__+'/resources/programparts/radchat/logs'): os.makedirs(__location__+'/resources/programparts/radchat/logs')
if not os.path.exists(__location__+'/resources/programparts/radchat/admintrip.txt'):
	with open(__location__+'/resources/programparts/radchat/admintrip.txt', "a") as makeprot:
		pass
if not os.path.exists(__location__+'/resources/programparts/radchat/maliciouswords.txt'):
	with open(__location__+'/resources/programparts/radchat/maliciouswords.txt', "a") as makeprot:
		pass
### server specific files end ###

addedprots = [] #list for protocols already in protlist.txt
folderprots = [] #list of all protocols in folder
with open(__location__+'/resources/protocols/protlist.txt', "r+") as protlist:
	for line in protlist:
		if line.endswith('\n'):
			addedprots += [line[:-1]]
		else:
			addedprots += [line]
	for file in os.listdir(__location__+'/resources/protocols/'):
		if file.endswith('.py'):
			folderprots += [file.split('.py')[0]]
	for item in folderprots: #add any protocols to protlist.txt that are in folder but not already in file
		if item not in addedprots:
			protlist.write(item + '\n')

#with a working protlist.txt, the protocol scripts are now imported
with open(__location__+'/resources/protocols/protlist.txt') as protlist:
	for line in protlist:
		try:
			prot = line.split('\n')[0]
		except:
			prot = line
		if line != '':
			filename = __location__ + '/resources/protocols/' + prot + '.py'
			directory, module_name = os.path.split(filename)
			module_name = os.path.splitext(module_name)[0]

			path = list(sys.path)
			sys.path.insert(0,directory)
			try:
				module = __import__(module_name) #cool import command
			finally:
				sys.path[:] = path




with open(__location__+'/resources/programparts/radchat/admintrip.txt', "r") as admintripfile: admintrip = admintripfile.readline().replace("\n", "")

maliciouswords = []
#read maliciouswords file and append each line to the list of malicious words

with open(__location__+'/resources/programparts/radchat/maliciouswords.txt', "r") as maliciouswordsfile:
	for line in maliciouswordsfile:
		maliciouswords.append(line.replace("\n",""))

def searchlogfor(timestamp):
	target = None
	with open(__location__+'/resources/programparts/radchat/logs/'+date(), "r") as log:
		for line in log:
			if timestamp in line.split()[0]:
				#find the addr associated with that timestamp
				global targetaddr
				targetaddr = line.split()[-1]
				target = socketlist[addrlist.index(targetaddr)]
	return target

def date():
	return datetime.now().strftime("%Y-%m-%d")

def timestamp():
	return "<{}>".format(datetime.now().strftime("%H:%M:%S.%f"))

def serverterminal(): #used for server commands
	while 1:
		inp = raw_input("")
		if inp:
			if inp == 'exit':
				quit()

def servergen():

	global serversocket
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversocket.bind((host, port))
	serversocket.listen(10)
	display="" 
	# add server socket object to the list of readable connections
	socketlist.append(serversocket)
	global addrlist
	addrlist = [host]
	with open(__location__+'/resources/programparts/radchat/logs/'+date(), "a") as log:
		log.write("Server has started. {}\n".format(timestamp()))


	while 1:
		sleep(.1)
		# get the list sockets which are ready to be read through select
		# 4th arg, time_out  = 0 : poll and never block
		ready_to_read,ready_to_write,in_error = select.select(socketlist,[],[],0)

		for sock in ready_to_read:
			# a new connection request recieved
			if sock == serversocket:
				#This is partially a placeholder variable, but also makes sense because the current socet is the server socket
				clientsocket,addr = serversocket.accept()
				print("Got a connection from %s" % str(addr))
				try:
					clientsocket.sendall('radchat:chat_client')
					compat = clientsocket.recv(1)
					if compat != 'y':
						clientsocket.sendall('need *radchat* protocol\n')
						print 'does not have protocol'
						clientsocket.close
					else:
						print 'HAS protocol'
						socketlist.append(clientsocket)
						addr = addr[0]
						#because the IP and socket are appended to their corresponding lists at the same time, they will share the same index value
						addrlist.append(addr)
						#turn the sock ID into a 4-digit string to make it easier to read from the log
						broadcast(addr, "{}: Someone has entered the chat. There is currently {} people in the chatroom.".format(timestamp(), len(socketlist)-1))
				except Exception,e:
					print str(e) + '\n'
				# a message from a client, not a new connection
			else:
				#figure out what the IP is for the sending client
				addr = addrlist[socketlist.index(sock)]
				# process data recieved from client
				try:
					# receiving data from the socket.
					data = sock.recv(4096)
				except:
					broadcast(addr, "{}: Someone has disconnected. There is currently {} people in the chatroom.".format(timestamp(), len(socketlist)-1))
					continue
				if data:
					message = ""
					name = ""
					tripcode = ""
					pm = False
					target = ""
					command = ""
					malicious = False

					try:
						#message, name, tripcode = data.splitlines()
						message = data.splitlines()[0]
						name = data.splitlines()[1]
					except:
						sock.send("invalid message")
					try:
						tripcode = data.splitlines()[2]
					except:
						pass

					tobesent = timestamp()
					if message.split()[0] =="/pm":
						pm = True
						if len(message.split()) > 2:
							target = message.split()[1]
							target = searchlogfor(target)
							message = message[len(message.split()[0]) + len(message.split()[1]) + 1:]
							tobesent += " ##pm##"
						else:
							message = ""
					if admintrip and tripcode == admintrip:
						tobesent += " ##admin##"
					else:
						if not name.replace(" ", ""):
							name = "Anonymous"
						tobesent += " [{}]".format(name)
						if tripcode:
							tobesent+= " {{{}}}".format(sha1(tripcode).hexdigest()[-7:-1])
					if not pm and message[0] == "/":
						command = message.split()[0]
					tobesent += ": {}".format(message)

					for phrase in maliciouswords:
						if phrase in message:
							malicious = True

					if command:
						if command == "/peoplecount":
							sock.send("there is currently {} people in the chatroom".format(len(socketlist)-1))
						else:
							sock.send("invalid command")
					elif pm:
						if message:
							if target:
								try:
									target.send(tobesent)
									with open(__location__+'/resources/programparts/radchat/logs/'+date(), "a") as log: log.write("{} [sent to IP: {}] {}\n".format(tobesent, targetaddr, addr))
								except:
									sock.send("that person is disconnected")
							else:
								sock.send("target not found")
						else:
							sock.send("poorly formatted pm")
					elif malicious:
						broadcast(addr, "{} {} has said malicious words".format(timestamp(), name))
					else:
						broadcast(addr, tobesent)
				else:
					# remove the socket that's broken
					if sock in socketlist:
						addrlist.remove(addrlist[socketlist.index(sock)])
						socketlist.remove(sock)
						# at this stage, no data means probably the connection has been broken
						broadcast(addr, "{}: Someone has disconnected. There is currently {} people in the chatroom.".format(timestamp(), len(socketlist)-1))

	serversocket.close()

# broadcast chat messages to all connected clients
def broadcast (addr, message):
	for socket in socketlist:
		# send the message only to peer
		if socket != serversocket:
			try :
				socket.send(message)
			except :
				# broken socket connection
				socket.close()
				# broken socket, remove it
				if socket in socketlist:
					socketlist.remove(socket)
	with open(__location__+'/resources/programparts/radchat/logs/'+date(), "a") as log:
		log.write(message + " " + addr + "\n")

threads = []
serverprocess = threading.Thread(target=servergen)
threads.append(serverprocess)
serverprocess.daemon = True
serverprocess.start()
serverterminal()
