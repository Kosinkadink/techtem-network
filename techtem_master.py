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

def setPass(pswrd):
	global password
	global passwordSet
	password = sha1(pswrd).hexdigest()[-10:-1]
	passwordSet = True

def pingallrepeat():
	with open(__location__+'/resources/programparts/master/seeds.txt', "r") as seeds:
		for line in seeds:
			while 1:
				sleep(10)
				if line:
					if line in pingseeds:
						if line.startswith('||'):
							print ping(line.split("||")[1])

def pingall():
	with open(__location__+'/resources/programparts/master/seeds.txt', "r") as seeds:
		for line in seeds:
			if line.startswith('||'):
				try:
					print ping(line.split("||")[1])
				except:
					print "line is poorly formatted"
	print ''

def connectall():
	with open(__location__+'/resources/programparts/master/seeds.txt', "r") as seeds:
		for line in seeds:
			if line.startswith('||'):
				try:
					print connectip(line.split("||")[1],line.split("||")[2:-1])
				except Exception,e:
					print str(e) + "\n"
	print ''

def ping(ip):
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

def connectip(ip,data):
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
	return connectprotocolclient(s,data)

def filetransfer_seed(s,data):

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

def connectprotocolclient(s, data):
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
			for gene in data:
				ser.sendall('y')
				ser.recv(2)
				filetransfer_seed(ser,gene)
			ser.sendall('n')
			print 'sending query complete'

	else:
		ser.sendall(compat)
		resp = ser.recv(1024)
		print resp
		ser.close
		return 'failure'

	ser.close
	return 'success'

def clear(): #clear screen, typical way
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

serverterminal()