#!/usr/bin/python2
import sys, socket, select, os, threading, subprocess, random, sqlite3
from time import strftime, sleep, time
from hashlib import sha1, md5
from datetime import datetime

#initialization of the server
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran
char = """ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"""
saltlength = 16
version = '1.0'
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
if not os.path.exists(__location__+'/resources/programparts/sync'): os.makedirs(__location__+'/resources/programparts/sync')
if not os.path.exists(__location__+'/resources/programparts/sync/syncdatabase.sqlite3'):
	conn = sqlite3.connect(__location__+'/resources/programparts/sync/syncdatabase.sqlite3')
	cur = conn.cursor()

	cur.execute('CREATE TABLE Accounts (salt TEXT, username TEXT, password TEXT, sizelim INTEGER)')

	conn.close()
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
			if inp == 'help':
				print "clear - clears screen"
				print "help - displays this window"
				print "exit - close seed"
			elif inp == 'exit':
				exit()
			elif inp == 'clear':
				clear()


def seed_recv_file(s, username): #receives files from client
	gene = s.recv(1024)
	s.send('ok')
	filelocpre = gene.split('/resources/programparts/sync/%s/' % username, 1)[1]
	filename = filelocpre.split('/')[-1]
	filelocpre = filelocpre.split('/')[:-1]
	fileloc = ''
	for file in filelocpre:
		fileloc += file + '/'


	downloadslocation = __location__ + '/resources/programparts/sync/%s/' % username + fileloc

	has = s.recv(2)
	if has != 'ok':
		return '404'
	else:
		s.sendall('ok')
		size = s.recv(16)
		size = int(size.strip())
		recvd = 0
		print filename + ' download in progress...'
		if not os.path.exists(downloadslocation):
			os.makedirs(downloadslocation)
		q = open(os.path.join(downloadslocation, filename), 'wb')
		while size > recvd:
			sys.stdout.write(str((float(recvd)/size)*100)[:4]+ '%' + '\r')
			sys.stdout.flush()
			data = s.recv(10240)
			if not data: 
				break
			recvd += len(data)
			q.write(data)
		s.sendall('ok')
		q.close()
		sys.stdout.write('100.0%\n')
		print filename + ' download complete'
		return '111'

def recv_file_list(s): #receives files from client

	size = s.recv(16)
	size = int(size.strip())
	recvd = 0
	print  'file names download in progress...'
	list = ''
	while size > recvd:
		sys.stdout.write(str((float(recvd)/size)*100)[:4]+ '%' + '\r')
		sys.stdout.flush()
		data = s.recv(1024)
		if not data: 
			break
		recvd += len(data)
		list += data
	s.sendall('ok')
	sys.stdout.write('100.0%\n')
	print 'filenames download complete'
	return list

def receiveAllFiles(s, username): # loops receiving files until master denies
	while True:
		sending = s.recv(1)
		if sending == 'y':
			s.sendall('ok')
			seed_recv_file(s, username)
		else:
			break
	s.sendall('ok')
	files = recv_file_list(s)
	files = files.split('@%$%@')[1:-1]
	folder = __location__+'/resources/programparts/sync/%s/' % username
	if os.name == 'nt':
		folder = folder.replace('\\','/')
	localfiles = []
	for file in files:
		splitfile = file.split('/resources/programparts/sync/%s/' % username)[1]
		print splitfile
		localfiles += [folder + splitfile]
	print localfiles
	removeUnsyncedFiles(s, folder, localfiles)

def removeUnsyncedFiles(s, folder, files):
	#total_size = os.path.getsize(folder)
	syncedfiles = []
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.name == 'nt':
			itempath = itempath.replace('\\','/')
		if os.path.isfile(itempath):
			syncedfiles += [itempath]
			if not itempath in files:
				print 'removing %s' % itempath
				os.remove(itempath)
		elif os.path.isdir(itempath):
			syncedfiles += removeUnsyncedFiles(s, itempath, files)

	removeUnsyncedFolders(folder)

	return syncedfiles

def removeUnsyncedFolders(folder):
	files = os.listdir(folder)
	#remove empty subfolders
	if len(files):
		for f in files:
			#if os.name == 'nt':
			#	f = f.replace('\\','/')
			fullpath = os.path.join(folder, f)
			if os.path.isdir(fullpath):
				removeUnsyncedFolders(fullpath)
	#if folder empty, delete it
	files = os.listdir(folder)
	if len(files) == 0:
		os.rmdir(folder)



def timeCommand(s): # returns timestamp
	s.recv(4)
	now = datetime.now()
	timestamp = now.strftime("%Y%m%d%H%M%S.%f")
	s.sendall(timestamp)
	print timestamp


def syncCommand(s):
	item = checkAuthCommand(s)
	if not item[0]:
		print "authentication error"
		return "authentication error"
	clienttimestamp = s.recv(32)
	username = item[1]
	if not os.path.exists(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username):
		with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
			timedoc.write("""00000000000000""")
	with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "rb") as timedoc:
		servertimestamp = timedoc.readline()
	print clienttimestamp
	print servertimestamp
	try:
		clienttimestamp = float(clienttimestamp)
		servertimestamp = float(servertimestamp)
		s.sendall('ok')
	except Exception,e:
		print str(e)
		s.sendall('no')
		s.recv(2)
		s.sendall('timestamp error')
		return 'timestamp error'
	s.recv(2)
	if servertimestamp < clienttimestamp:
		s.sendall('send')
		receiveAllFiles(s, username)
	elif servertimestamp > clienttimestamp:
		s.sendall('recv')
		filessent = sendSyncFiles(s, __location__+'/resources/programparts/sync/%s/' % username)
		print filessent
		s.sendall('n')
		s.recv(2)
		files = '@%$%@'
		for fileloc in filessent:
			files += fileloc + '@%$%@'
		sendFileList(s, files)
	elif servertimestamp == clienttimestamp:
		s.sendall('same')
		print 'client and server already synced'
		return 'already synced'

def sendSyncFiles(s, folder):
	#total_size = os.path.getsize(folder)
	syncedfiles = []
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.name == 'nt':
			itempath = itempath.replace('\\','/')
		if os.path.isfile(itempath):
			syncedfiles += [itempath]
			s.sendall('y')
			s.recv(2)
			sendItem(s,itempath)
		elif os.path.isdir(itempath):
			syncedfiles += sendSyncFiles(s, itempath)
	return syncedfiles

def sendItem(s,data): #send file to seed

	print 'sending data'								   
	s.sendall(data)
	print 'awaiting reply'
	s.recv(2)

	#file_name,destination = data.split("@@")
	file = data

	uploads = __location__ + '/resources/uploads/'

	file_name = data.split('/')[-1]

	#print os.path.join(uploads, file_name)
	print file
	if os.path.exists(file):
		print file_name + " found"
		s.sendall('ok')
		s.recv(2)

		filelength =  os.path.getsize(file)
		s.sendall('%16d' % filelength)
		with open(file, 'rb') as f:
			print file_name + " sending..."
			while True:
				data = f.read(10240)
				if not data:
					break
				s.sendall(data)
		#print 'program: %s' % str(len(data))
		#print str(os.path.getsize(file))

		#print file_name + " sending..."
		#s.sendall(data)
		s.recv(2)
		print file_name + " sending successful"
		
	else:
		print file_name + " not found"

def sendFileList(s, files): #send file list
		data = files
		s.sendall('%16d' % len(data))
		print "file list sending..."
		s.sendall(data)
		s.recv(2)
		print "file list sending successful"

def newUserCommand(s):
	global char, saltlength
	improperChar = '|' # list of improper characters
	username = s.recv(32).lower()
	proper = True
	error = 'empty error string'
	for item in improperChar:
		if item in username:
			proper = False
			error = 'improper characters used'

	conn = sqlite3.connect(__location__+'/resources/programparts/sync/syncdatabase.sqlite3')
	cur = conn.cursor()
	cur.execute('SELECT username from Accounts WHERE username=?',(username,))
	exists = cur.fetchone()

	if exists != None:
		proper = False
		error = 'username already exists'

	if not proper:
		s.sendall('n')
		print error
		s.recv(2)
		s.sendall(error)
		return
	else:
		s.sendall('y')
		salt = ''
		for n in range(0,saltlength):
			salt += char[random.randrange(0,len(char))]
		try:
			passwordHash = sha1(salt + s.recv(128)).hexdigest()
			s.sendall('y')
		except Exception,e:
			print str(e)
			s.sendall('n')
			s.recv(2)
			s.sendall(e)
			return

		cur.execute('INSERT INTO Accounts (salt, username, password, sizelim) VALUES (?,?,?,?)', (salt,username,passwordHash,1280000000))
		conn.commit()
		print 'User %s added.' % username
		createUserDir(username)
	cur.close()

def createUserDir(username):
	if not os.path.exists(__location__+'/resources/programparts/sync/%s' % username):
		os.makedirs(__location__+'/resources/programparts/sync/%s' % username)
		with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
			timedoc.write("""00000000000000""")

def checkAuthCommand(s):
	username = s.recv(32).lower()
	info = isUser(username)
	if not info[0]:
		s.sendall('n')
		return (False,None)
	s.sendall('y')
	passwordHash = sha1(info[1] + s.recv(128)).hexdigest()
	match = passwordMatch(username,passwordHash)
	if match:
		s.sendall('y')
		return (True,username)
	else:
		s.sendall('n')
		return (False,None)


def isUser(username): #check is username exists
	username = username.lower()
	exists = False
	salt = None

	conn = sqlite3.connect(__location__+'/resources/programparts/sync/syncdatabase.sqlite3')
	cur = conn.cursor()
	cur.execute('SELECT salt from Accounts WHERE username=?',(username,))
	data = cur.fetchone()
	if data != None:
		exists = True
		salt = data[0]

	return (exists,salt)

def passwordMatch(username,passwordHash): #check if password is a match
	match = False
	conn = sqlite3.connect(__location__+'/resources/programparts/sync/syncdatabase.sqlite3')
	cur = conn.cursor()
	cur.execute('SELECT password from Accounts WHERE username=?',(username,))
	data = cur.fetchone()
	if data != None:
		passwordStored = data[0]
		if passwordHash == passwordStored:
			match = True

	#cur.execute('SELECT * from Accounts')
	#data = cur.fetchone()
	#for row in data:
	#	print row

	return match


def sizeDir(folder): # get size of directory and all subdirectories
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath):
			total_size += os.path.getsize(itempath)
		elif os.path.isdir(itempath):
			total_size += getFolderSize(itempath)
	return total_size

def sizeCommand(s):
	pass


def distinguishCommand(s): # interpret what master requests
	order = s.recv(128)
	print 'command is: %s' % order

	if order == 'sync': # sync
		s.send('ok')
		print 'command understood, performing: %s' % order
		syncCommand(s)
	elif order == 'time': # send time
		s.send('ok')
		print 'command understood, performing: %s' % order
		timeCommand(s)
	elif order == 'newuser': # send time
		s.send('ok')
		print 'command understood, performing: %s' % order
		newUserCommand(s)
	elif order == 'checkauth': # send time
		s.send('ok')
		print 'command understood, performing: %s' % order
		checkAuthCommand(s)
	elif order == 'size': # send size of user files if right perms
		s.send('ok')
		print 'command understood, performing: %s' % order
		sizeCommand(s)

	else: # unknown command
		s.send('no')
		print 'command not understood'

def servergen():
	global version
	print 'server started - version ' + version + '\n'
	# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

	# get local machine name
	host = ""
	port = 9015

	# bind to the port
	serversocket.bind((host, port))						  

	# queue up to 10 requests
	serversocket.listen(10)							   

	while 1:
		# establish a connection
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))
		try:
			clientsocket.sendall('sync:sync_client') #check if sync_client is connecting
			compat = clientsocket.recv(1)
			if compat != 'y': #not a sync_client, so respond with 
				clientsocket.sendall('need *sync* protocol\n')
				print 'does not have protocol'
				clientsocket.close
			else:
				print 'HAS protocol'
				syncthread = threading.Thread(target=distinguishCommand,args=(clientsocket,))
				syncthread.daemon = True
				syncthread.start()

				clientsocket.close
			print("Disconnection by %s with data received" % str(addr))

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