#!/usr/bin/python2
import sys, socket, select, os, threading
from time import strftime, sleep
from hashlib import sha1

#initialization of the client
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran
passwordSet = False
password = None
version = '1.0'

if not os.path.exists(__location__+'/resources'): os.makedirs(__location__+'/resources')
if not os.path.exists(__location__+'/resources/protocols'): os.makedirs(__location__+'/resources/protocols') #for protocol scripts
if not os.path.exists(__location__+'/resources/cache'): os.makedirs(__location__+'/resources/cache') #used to store info for protocols and client
if not os.path.exists(__location__+'/resources/programparts'): os.makedirs(__location__+'/resources/programparts') #for storing protocol files
if not os.path.exists(__location__+'/resources/uploads'): os.makedirs(__location__+'/resources/uploads') #used to store files for upload
if not os.path.exists(__location__+'/resources/downloads'): os.makedirs(__location__+'/resources/downloads') #used to store downloaded files

#master files start
if not os.path.exists(__location__+'/resources/programparts/master'): os.makedirs(__location__+'/resources/programparts/master')

if not os.path.exists(__location__+'/resources/programparts/master/seeds.txt'):
	with open(__location__+'/resources/programparts/master/seeds.txt', "a") as seeds:
		seeds.write("""##################################################################################################################
##The format is: ||ip:port||filetosend.extension@@/destination/||
##Destination is relative to the location of the seed script. To place in resources folder, /resources/
##If destination is same directory as location of the seed script, destination is: HOME
##If the file is to be ran after download of all files, use % after destination. Example: /resources/% or HOME%
##Only line starting with || will be read. Any line not starting with || will not be read.
##################################################################################################################""")
#master files end

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
	print "TechTem Network Master started"
	print "Version " + version
	print "Type help for command list\n"

#function for client splash screen
def serverterminal():
	boot()
	while 1:
		inp = raw_input("")
		if inp:
			if inp.split()[0] == 'pingall':
				pingall()
			elif inp.split()[0] == 'ping':
				try:
					ip = inp.split()[1]
				except:
					ip = None 
				print ping(ip)+'\n'
			elif inp.split()[0] == 'startall':
				connectall()
			elif inp.split()[0] == 'quit' or inp.split()[0] == 'leave' or inp.split()[0] == 'exit':
				quit()
			elif inp.split()[0] == 'clear':
				boot()
			elif inp.split()[0] == 'help' or inp.split()[0] == '?':
				print "ping + (address): check if seed at address is online\npingall: check if all seeds in file are online\nsetpass + (password): set password\nclear: clears screen\n"
			elif inp.split()[0] == 'setpass':
				try:
					setPass(inp.split()[1])
				except:
					print "Invalid input for password"
			elif inp == 'return':
				print password
			else:
				print "Invalid command"

def setPass(pswrd): #set password
	global password
	global passwordSet
	password = sha1(pswrd).hexdigest()[-10:-1]
	passwordSet = True

def pingallrepeat(): #ping all seeds every set period of time
	while 1:
		pingall()
		sleep(10)

def pingall(): #ping all seeds on list to determine what seeds are online
	with open(__location__+'/resources/programparts/master/seeds.txt', "r") as seeds:
		for line in seeds:
			if line.startswith('||'):
				try:
					print ping(line.split("||")[1])
				except:
					print "line is poorly formatted"
	print ''

def connectall(): #initialize all seeds by sending/starting files
	with open(__location__+'/resources/programparts/master/seeds.txt', "r") as seeds:
		for line in seeds:
			if line.startswith('||'):
				try: #connect to ip, save data, issue command
					print connectip(line.split("||")[1],line.split("||")[2:-1],'receive')
				except Exception,e:
					print str(e) + "\n"
	print ''

def ping(ip): #attempt to connect to ip to determine if server is online
	try:
		host = ip.split(':')[0]
		port = int(ip.split(':')[1])
	except:
		return 'invalid host/port provided'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	try:
		s.connect((host, port))
	except:
		s.close
		return ip + " seed NOT online"
	s.close
	return ip + " seed online"

def connectip(ip,data,command): #connect to ip
	try:
		host = ip.split(':')[0]
		port = int(ip.split(':')[1])
	except:
		return 'invalid host/port provided\n'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	try:
		s.connect((host, port))
	except:
		s.close
		return "Seed at " + ip + " not available\n"
	print "\nConnection successful to " + ip
	return connectprotocolclient(s,data,command)

def filetransfer_seed(s,data): #send file to seed

	seed = s
	print 'sending data'								   
	seed.sendall(data)
	print 'awaiting reply'
	seed.recv(2)

	file_name,destination = data.split("@@")

	uploads = __location__ + '/resources/uploads/'

	print os.path.join(uploads, file_name)
	if os.path.exists(os.path.join(uploads, file_name)):
		print file_name + " found"
		s.sendall('ok')
		s.recv(2)

		with open(os.path.join(uploads, file_name), 'rb') as f:
			data = f.read()
		s.sendall('%16d' % len(data))
		print file_name + " sending..."
		s.sendall(data)
		s.recv(2)
		print file_name + " sending successful"
		
	else:
		print file_name + " not found"
	return

def diagnosticsCommand(ser, data): #request diagnostics from seed
	pass

def receiveCommand(ser, data): #make seed receive all files from master
	for gene in data:
		ser.sendall('y')
		ser.recv(2)
		filetransfer_seed(ser,gene)
	ser.sendall('n')
	print 'sending query complete'

def distinguishCommand(ser, data, command): #interpret what to tell seed
	if command == 'receive':
		order = 'receive'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
			receiveCommand(ser, data)
		else:
			print 'command not understood by seed'
	if command == 'closeseed':
		order = 'closeseed'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
		else:
			print 'command not understood by seed'
	if command == 'diagnostics':
		order = 'diagnostics'
		ser.sendall(order)
		understood = ser.recv(2)
		if understood == 'ok':
			print 'command: %s understood by seed' % order
			diagnosticsCommand(ser, data)
		else:
			print 'command not understood by seed'


def connectprotocolclient(s, data, command): #communicate via protocol to command seed
	global password
	ser = s
	identity = ser.recv(1024)
	compat = 'n'
	scriptname,function = identity.split(':')
	if scriptname == 'seedtransfer' and function == 'seedtransfer_client':
		compat = 'y'
	if compat == 'y':
		ser.sendall(compat)
		print 'success initiated'
		passrqst = ser.recv(4)
		ser.sendall(password)
		status = ser.recv(1)
		if status != 'y':
			ser.close
			return 'failure: invalid password'
		else:
			print 'success complete: password match'
			distinguishCommand(ser, data, command)

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