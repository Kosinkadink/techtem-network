#!/usr/bin/python2
import sys, socket, select, os, threading, subprocess
from time import strftime, sleep
from hashlib import sha1

#initialization of the server
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran
passwordSet = False
continueReceive = True
password = None
version = '1.0'
filestorun = []
filesrunning = []
processID = 0


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
if not os.path.exists(__location__+'/resources/programparts/filetransfer'): os.makedirs(__location__+'/resources/programparts/filetransfer')
if not os.path.exists(__location__+'/resources/programparts/filetransfer/approvedfiles.txt'):
	with open(__location__+'/resources/programparts/filetransfer/approvedfiles.txt', "a") as makeprot:
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
	global continueReceive
	while 1:
		inp = raw_input("")
		if inp:
			if inp == 'help':
				print "setpass [password] - set password"
				print "return - show password hash"
				print "Rec - print if seed continues receiving"
				print "doRec - keep receiving after master commands"
				print "dontRec - stop receiving after master commands"
				print "exit - close seed"
			elif inp == 'exit':
				exit()
			elif inp == 'clear':
				clear()
			elif inp == 'return':
				print password
			elif inp.split(None, 1)[0] == 'setpass':
				try:
					setPass(inp.split(None, 1)[1])
				except Exception,e:
					print str(e)
			elif inp == 'doRec':
				continueReceive = True
			elif inp == 'dontRec':
				continueReceive = False
			elif inp == 'Rec':
				print continueReceive
			

def setPass(pswrd): #sets password, stores it as SHA1 hash
	global password, passwordSet
	password = sha1(pswrd).hexdigest()[-10:-1]
	passwordSet = True

def seed_recv_file(s): #receives files from master
	global filestorun
	gene = s.recv(512)
	s.send('ok')
	name,destination = gene.split('@@')
	if destination.endswith("%"):
		destination = destination[:-1]
		if destination == 'HOME':
			filestorun += ['/' +name]
		else:
			filestorun += [destination+name]
	if destination == 'HOME':
		downloadslocation = __location__
	else:
		downloadslocation = __location__ + destination

	has = s.recv(2)
	if has != 'ok':
		return '404'
	else:
		s.sendall('ok')
		size = s.recv(16)
		size = int(size.strip())
		recvd = 0
		print name + ' download in progress...'
		if not os.path.exists(downloadslocation):
			os.makedirs(downloadslocation)
		q = open(os.path.join(downloadslocation, name), 'wb')
		while size > recvd:
			sys.stdout.write(str((float(recvd)/size)*100)[:4]+ '%' + '\r')
			sys.stdout.flush()
			data = s.recv(1024)
			if not data: 
				break
			recvd += len(data)
			q.write(data)
		s.sendall('ok')
		q.close()
		sys.stdout.write('100.0%\n')
		print name + ' download complete'
		return '111'

def receiveAllFiles(s): # loops receiving files until master denies
	global processID, filestorun, filesrunning
	clientsocket = s
	while True:
		sending = clientsocket.recv(1)
		clientsocket.sendall('ok')
		if sending == 'y':
			seed_recv_file(clientsocket)
		else:
			break

	print filestorun
	#serversocket.shutdown(socket.SHUT_RDWR)
	for file in filestorun:
		print 'attempting to start ' + file
		processname = 'process' + str(processID)
		globals()[processname] = subprocess.Popen('python ' + __location__+file, shell=True)
		threads.append(globals()[processname])
		print file + ' started'
		processID += 1

	filestorun = []
	print filestorun

def distinguishCommand(s): # interpret what master requests
	order = s.recv(128)
	print 'command is: %s' % order

	if order == 'receive': # receive all files sent by master
		s.send('ok')
		print 'command understood, performing: %s' % order
		receiveAllFiles(s)

	elif order == 'send': # send all files requested by master
		s.send('no')
		print 'command not understood'
	elif order == 'replace': # replace seed with another version
		s.send('no')
		print 'command not understood'

	elif order == 'diagnostics': # run diagnostics requested by master
		s.send('ok')
		print 'command understood, performing: %s' % order
		diagnosticsToRun(s)

	elif order == 'runproc': # run a process from file already on seed
		s.send('no')
		print 'command not understood'
	elif order == 'killproc': # kill a process from file already on seed
		s.send('no')
		print 'command not understood'

	elif order == 'closeseed': # close seed, killing all processes
		s.send('ok')
		print 'command understood, performing: %s' % order
		s.close
		exit()

	elif order == 'burnseed': # close all processes related to seed, delete all files including seed
		s.send('no')
		print 'command not understood'
	else:
		s.send('no')
		print 'command not understood'


def servergen():
	global password, version
	print 'server started - version ' + version + '\n'
	# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

	# get local machine name
	host = ""
	port = 9008

	# bind to the port
	serversocket.bind((host, port))						  

	# queue up to 10 requests
	serversocket.listen(10)							   

	while 1:
		# establish a connection
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))
		try:
			clientsocket.sendall('seedtransfer:seedtransfer_client') #check if master is connecting
			compat = clientsocket.recv(1)
			if compat != 'y': #not a master, so respond with 
				clientsocket.sendall('need *master* protocol\n')
				print 'does not have protocol'
				clientsocket.close
			else:
				print 'HAS protocol'
				clientsocket.sendall('pass')
				masterpass = clientsocket.recv(len(password))
				if masterpass != password:
					clientsocket.sendall('n')
					print 'master has invalid password'
					clientsocket.close
				else:
					clientsocket.sendall('y')
					print 'master has valid password'
					distinguishCommand(clientsocket)

				clientsocket.close
			print("Disconnection by %s with data received" % str(addr))

			if not continueReceive: #break receiving from a master if set to False
				print 'closing connectivity to master'
				break

		except Exception,e:
			print str(e) + '\n'
	
	#print 'closing seed server now\n'
	
	#sys.exit()

def clear(): #clear screen, typical way
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

def exit(): #kill all processeses for a tidy exit
	#global threads
	#for operation in threads:
	#	operation._Thread_stop()
	#	print 'thread %s stopped successfully' % operation
	quit()

threads = []
serverprocess = threading.Thread(target=servergen)
threads.append(serverprocess)
serverprocess.daemon = True
serverprocess.start() #starts server process in another thread
serverterminal() #starts command input