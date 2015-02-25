#!/usr/bin/python2
import sys, socket, select, os, threading
from time import strftime, sleep

#initialization of the server
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
if not os.path.exists(__location__+'/resources/programparts/name'): os.makedirs(__location__+'/resources/programparts/name')
if not os.path.exists(__location__+'/resources/programparts/name/techtemurls.txt'):
	with open(__location__+'/resources/programparts/name/techtemurls.txt', "a") as makeprot:
		makeprot.write("")
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



def serverterminal(): #used for server commands
	while 1:
		inp = raw_input("")
		if inp:
			if inp == 'exit':
				quit()

def searchurls(rqst):
	ip = '404'
	with open(__location__+'/resources/programparts/name/techtemurls.txt') as file:
		for line in file:
			if line.startswith('||'):
				url = line.split("||")
				if url[1] == rqst:
					ip = url[2]
					break
	return ip

def name_server(s):

	clientsocket = s									   

	rqst = clientsocket.recv(1024)
	print rqst
	message = searchurls(rqst.lower())
	print message
	clientsocket.sendall(message)

def servergen():
	print 'server started\n'
	# create a socket object
	serversocket = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM) 

	# get local machine name
	host = ""					   
	port = 9010										   

	# bind to the port
	serversocket.bind((host, port))								  

	# queue up to 10 requests
	serversocket.listen(10)										   

	while 1:
		# establish a connection
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))
		try:
			clientsocket.sendall('name:name')
			compat = clientsocket.recv(1)
			if compat != 'y':
				clientsocket.sendall('need *name* protocol\n')
				print 'does not have protocol'
				clientsocket.close
			else:
				print 'HAS protocol'
				try:
					name_server(clientsocket)
				except:
					pass
				clientsocket.close
			print("Disconnection by %s with data received\n" % str(addr))
		except Exception,e:
			print str(e) + '\n'
	
	print 'closing now'		
	serversocket.close()

threads = []
serverprocess = threading.Thread(target=servergen)
threads.append(serverprocess)
serverprocess.daemon = True
serverprocess.start()
serverterminal()