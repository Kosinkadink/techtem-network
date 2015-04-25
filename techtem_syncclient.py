#!/usr/bin/python2
import sys, socket, select, os, threading, sqlite3
from time import strftime, sleep, time
from hashlib import sha1, md5
from getpass import getpass

#initialization of the client
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran
passwordSet = False
password = None
username = None
version = '1.0'

if not os.path.exists(__location__+'/resources'): os.makedirs(__location__+'/resources')
if not os.path.exists(__location__+'/resources/protocols'): os.makedirs(__location__+'/resources/protocols') #for protocol scripts
if not os.path.exists(__location__+'/resources/cache'): os.makedirs(__location__+'/resources/cache') #used to store info for protocols and client
if not os.path.exists(__location__+'/resources/programparts'): os.makedirs(__location__+'/resources/programparts') #for storing protocol files
if not os.path.exists(__location__+'/resources/uploads'): os.makedirs(__location__+'/resources/uploads') #used to store files for upload
if not os.path.exists(__location__+'/resources/downloads'): os.makedirs(__location__+'/resources/downloads') #used to store downloaded files

#sync files start
if not os.path.exists(__location__+'/resources/programparts/sync'): os.makedirs(__location__+'/resources/programparts/sync')

if not os.path.exists(__location__+'/resources/programparts/sync/serverlist.txt'):
	with open(__location__+'/resources/programparts/sync/serverlist.txt', "a") as seeds:
		seeds.write("""##################################################################################################################
##The format is: ||ip:port||
##Files will be sent to and from these servers
##Only lines starting with || will be read
##################################################################################################################""")
#sync files end

if os.path.exists(__location__+'/resources/protocols/protlist.txt'):
	os.remove(__location__+'/resources/protocols/protlist.txt')
if not os.path.exists(__location__+'/resources/protocols/protlist.txt'):
	with open(__location__+'/resources/protocols/protlist.txt', "a") as protlist: #file used for identifying what protocols are available
		pass

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

def boot():
	clear()
	print "TechTem Sync Client started"
	print "Version " + version
	print "Type help for command list\n"

#function for client splash screen
def serverterminal():
	boot()
	while 1:
		inp = raw_input("")
		if inp:
			if inp.split()[0] == 'quit' or inp.split()[0] == 'leave' or inp.split()[0] == 'exit':
				quit()
			elif inp.split()[0] == 'clear':
				boot()
			elif inp.split()[0] == 'time':
				connectTime()
			elif inp.split()[0] == 'help' or inp.split()[0] == '?':
				print "\nclear: clears screen\nexit: closes program"
			elif inp.split()[0] == 'login':
				login()
			elif inp.split()[0] == 'newacc':
				connectCreateNew()
			elif inp.split()[0] == 'check':
				connectCheckAuth()
			elif inp.split()[0] == 'createsync':
				createSyncState()
			elif inp.split()[0] == 'sync':
				connectSync()
			elif inp.split()[0] == 'size':
				checkSize()
			elif inp.split()[0] == 'sum':
				checkChecksum(inp.split()[1])
			else:
				print "Invalid command"

def checkSize():
	username = raw_input("Username: ")
	try:
		start = time()
		print sizeDir(__location__ + '/resources/programparts/sync/%s' % username.lower())
		end = time()
		print str(end-start)
	except Exception,e:
		print str(e)

def checkChecksum(type):
	username = raw_input("Username: ")
	try:
		if type == 'md':
			start = time()
			list = checksumList(__location__ + '/resources/programparts/sync/%s' % username.lower(), 'md')
			end = time()
			print list
			print str(end-start)

		elif type == 'sh':
			start = time()
			list = checksumList(__location__ + '/resources/programparts/sync/%s' % username.lower(), 'sh')
			end = time()
			print list
			print str(end-start)
	except Exception,e:
		print str(e)



def createSyncState():
	global username
	try:
		valid = connectCheckAuth()
		if not valid:
			raise ValueError("authentication error")
		if not os.path.exists(__location__+'/resources/programparts/sync/%s' % username):
			os.makedirs(__location__+'/resources/programparts/sync/%s' % username)
			with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
				timedoc.write("""00000000000000""")
		else:
			if not os.path.exists(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username):
				with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
					timedoc.write("""00000000000000""")
			else:
				os.remove(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username)
				timestamp = connectTime()
				with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
					timedoc.write(timestamp)
		with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
			list = checksumList(__location__ + '/resources/programparts/sync/%s' % username.lower(), 'sh')
			for item in list:
				timedoc.write('\n' + item)
		#with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "rb") as timedoc:
		#	liststuff = []
		#	liststuff += [timedoc.readline()]
		#	print liststuff
	except Exception,e:
		print str(e) + '\n'

def connectSync():
	global username
	try:
		valid = connectCheckAuth()
		if not valid:
			raise ValueError("authentication error")
		if not os.path.exists(__location__+'/resources/programparts/sync/%s' % username):
			os.makedirs(__location__+'/resources/programparts/sync/%s' % username)
			with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
				timedoc.write("""00000000000000""")
		else:
			if not os.path.exists(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username):
				with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
					timedoc.write("""00000000000000""")
			#else:
			#	os.remove(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username)
			#	timestamp = connectTime()
			#	with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
			#		timedoc.write(timestamp)
		print connectToServer('sync','sync')

	except Exception,e:
		print str(e) + '\n'

def login():
	global username, password
	try:
		username = raw_input("Username: ").lower()
		password = getpass("Password: ")
		# make sure lengths are okay
		if len(username) < 19 and len(password) < 129:
			print "Username and Password entered"
			return True
		else:
			print "Improper number of characters, try again."
			raise ValueError("incorrect # of characters")
	except Exception,e:
		print str(e)
		username = None
		password = None
		return False

def loginnew():
	global username, password
	try:
		username = raw_input("Username: ").lower()
		password = getpass("Password: ")
		password2 = getpass("Re-enter Password: ")
		# make sure passwords match and lengths are okay
		if password == password2 and len(username) < 19 and len(password) < 129:
			print "Username and Password entered"
			return True
		else:
			print "Passwords do not match, try again."
			raise ValueError("password mismatch")
	except Exception,e:
		print str(e)
		username = None
		password = None
		return False

def sizeDir(folder): # get size of directory and all subdirectories
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath):
			total_size += os.path.getsize(itempath)
			#checksum(itempath)
		elif os.path.isdir(itempath):
			total_size += sizeDir(itempath)
	return total_size

def checksumList(itempath, type):
	folder = itempath
	checksumlist = []
	if type == 'md':
		for item in os.listdir(folder):
			itempath = os.path.join(folder, item)
			if os.path.isfile(itempath):
				checksumlist += [itempath+checksum(itempath)]
				#checksum(itempath)
			elif os.path.isdir(itempath):
				checksumlist += checksumList(itempath, type)
		return checksumlist
	elif type == 'sh':
		for item in os.listdir(folder):
			itempath = os.path.join(folder, item)
			if os.path.isfile(itempath):
				checksumlist += [itempath+checksum2(itempath)]
				#checksum(itempath)
			elif os.path.isdir(itempath):
				checksumlist += checksumList(itempath, type)
		return checksumlist

def checksum(itempath):
	if os.path.getsize(itempath) < 50240000:
		data = md5(open(itempath).read()).hexdigest()
		print '[%s]' % data
		return ':' + data
	else:
		print '['
		with open(itempath) as file:
			datamult = ':'
			while True:
				data = file.read(50240000)
				if data:
					data = md5(data).hexdigest()
					datamult += data
					print data
				else:
					break
			print ']' 
			#print 'Checksum complete.'
			return datamult


def sizeDir2(folder): # get size of directory and all subdirectories
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath):
			total_size += os.path.getsize(itempath)
			checksum2(itempath)
		elif os.path.isdir(itempath):
			total_size += sizeDir2(itempath)
	return total_size

def checksum2(itempath):
	if os.path.getsize(itempath) < 50240000:
		data = sha1(open(itempath).read()).hexdigest()
		print '[%s]' % data
		return ':' + data
		
	else:
		print '['
		with open(itempath) as file:
			datamult = ':'
			while True:
				data = file.read(50240000)
				if data:
					data = sha1(data).hexdigest()
					datamult += data
					print data
				else:
					break
			print ']' 
			#print 'Checksum complete.'
			return datamult
		

def connectCheckAuth():
	global username, password
	try:
		valid = login()
		if valid:
			pass
		if not valid:
			raise ValueError("login entry error")
		return connectToServer('checkAuth','checkauth')

	except Exception,e:
		print str(e) + '\n'

def connectCreateNew():
	global username, password
	try:
		valid = loginnew()
		if valid:
			pass
		if not valid:
			raise ValueError("login entry error")
		connectToServer('createAccount','newuser')

	except Exception,e:
		print str(e) + '\n'

def connectTime():
	time = connectToServer('savedtime','time')
	print time
	return time

def connectToServer(data,command):
	with open(__location__+'/resources/programparts/sync/serverlist.txt', "r") as seeds:
		for line in seeds:
			if line.startswith('||'):
				try: #connect to ip, save data, issue command
					return connectip(line.split("||")[1],data,command)
				except Exception,e:
					print str(e) + "\n"
	print ''

def connectip(ip,data,command): #connect to ip
	try:
		host = ip.split(':')[0]
		port = int(ip.split(':')[1])
	except:
		return 'invalid host/port provided\n'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
	try:
		s.connect((host, port))
	except:
		s.close
		return "Seed at " + ip + " not available\n"
	print "\nConnection successful to " + ip
	return connectprotocolclient(s,data,command)

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
			sent = 0
			while True:
				sys.stdout.write(str((float(recvd)/filelength)*100)[:4]+ '%' + '\r')
				sys.stdout.flush()
				data = f.read(10240)
				if not data:
					break
				sent += len(data)
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

def sendCommand(s, data): #send sync files to server
	global username
	folder = __location__+'/resources/programparts/sync/%s/' % username

	if data == 'sync':
		filessent = sendSyncFiles(s, folder)
		print filessent
		s.sendall('n')
		s.recv(2)
		files = '@%$%@'
		for fileloc in filessent:
			files += fileloc + '@%$%@'
		sendFileList(s, files)
	elif data == 'spec':
		sendSpecFiles(s, folder)
	else:
		s.sendall('n')
		return 'unknown response'

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

def sendSpecFiles(s, folder):
	pass

def receiveCommand(s, data): # loops receiving files until master denies
	global username
	while True:
		sending = s.recv(1)
		s.sendall('ok')
		if sending == 'y':
			seed_recv_file(s, username)
		else:
			break
	s.sendall('ok')
	files = recv_file_list(s)
	files = files.split('@%$%@')[1:-1]
	folder = __location__+'/resources/programparts/sync/%s/' % username
	print folder
	if os.name == 'nt':
		folder = folder.replace('\\','/')
	localfiles = []
	print folder
	for file in files:
		splitfile = file.split('/resources/programparts/sync/%s/' % username)[1]
		localfiles += [folder + splitfile]
	print localfiles
	print 'location: %s' % __location__
	print 'folder: %s' % folder
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
	print 'file names download complete'
	return list

def syncCommand(s, data):
	valid = checkAuthCommand(s, data)
	if not valid:
		return "authentication error"
	with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "rb") as timedoc:
		timestamp = timedoc.readline()
	s.sendall(timestamp)
	works = s.recv(2)
	if works != 'ok':
		s.sendall('ok')
		response = s.recv(128)
		return response
	s.sendall('ok')
	action = s.recv(4)
	if action == 'send':
		sendCommand(s, data)
	elif action == 'recv':
		receiveCommand(s, data)
	elif action == 'same':
		return 'already synced'

def checkAuthCommand(s, data):
	global username, password
	s.sendall(username)
	valid = s.recv(1)
	if valid == 'n':
		print 'Username is invalid'
		return False
	s.sendall(password)
	match = s.recv(1)
	if match == 'y':
		print 'Correct Username/Password Combo'
		return True
	else:
		print 'Incorrect Username/Password Combo'
		return False

def newUserCommand(s, data):
	global username, password
	s.send(username)
	proper = s.recv(1)
	if proper == 'y':
		s.send(password)
		response = s.recv(1)
		if response == 'y':
			s.send('ok')
			print 'Account created.'
			if not os.path.exists(__location__+'/resources/programparts/sync/%s' % username):
				os.makedirs(__location__+'/resources/programparts/sync/%s' % username)
				with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
					timedoc.write("""00000000000000""")
			else:
				if not os.path.exists(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username):
					with open(__location__+'/resources/programparts/sync/%s/timestamp.txt' % username, "a") as timedoc:
						timedoc.write("""00000000000000""")
		else:
			s.send('ok')
			print s.recv(128)
	else:
		s.send('ok')
		print s.recv(128)

def timeCommand(s, data):
	s.sendall('send')
	time = s.recv(128)
	return time

def distinguishCommand(ser, data, command): #interpret what to tell seed
	if command == 'sync':
		order = 'sync'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
			return syncCommand(ser, data)
		else:
			print 'command not understood by seed'
	elif command == 'time':
		order = 'time'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
			return timeCommand(ser, data)
		else:
			print 'command not understood by seed'
	elif command == 'newuser':
		order = 'newuser'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
			return newUserCommand(ser, data)
		else:
			print 'command not understood by seed'
	elif command == 'checkauth':
		order = 'checkauth'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
			return checkAuthCommand(ser, data)
		else:
			print 'command not understood by seed'
			


def connectprotocolclient(s, data, command): #communicate via protocol to command seed
	global password
	ser = s
	identity = ser.recv(1024)
	compat = 'n'
	scriptname,function = identity.split(':')
	if scriptname == 'sync' and function == 'sync_client':
		compat = 'y'
	if compat == 'y':
		ser.sendall(compat)
		print 'success initiated'
		return distinguishCommand(ser, data, command)

	else:
		ser.sendall(compat)
		resp = ser.recv(1024)
		print resp
		ser.close
		return 'failure. closing connection...'

	ser.close
	return 'connection closed'

def clear(): #clear screen, typical way
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

serverterminal()