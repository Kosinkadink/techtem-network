#!/usr/bin/python2
import sys, socket, select, os

#initialization of the client
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran

if not os.path.exists(__location__+'/resources'): os.makedirs(__location__+'/resources')
if not os.path.exists(__location__+'/resources/protocols'): os.makedirs(__location__+'/resources/protocols') #for protocol scripts
if not os.path.exists(__location__+'/resources/cache'): os.makedirs(__location__+'/resources/cache') #used to store info for protocols and client
if not os.path.exists(__location__+'/resources/programparts'): os.makedirs(__location__+'/resources/programparts') #for storing protocol files
if not os.path.exists(__location__+'/resources/uploads'): os.makedirs(__location__+'/resources/uploads') #used to store files for upload
if not os.path.exists(__location__+'/resources/downloads'): os.makedirs(__location__+'/resources/downloads') #used to store downloaded files

if not os.path.exists(__location__+'/resources/programparts/name'): os.makedirs(__location__+'/resources/programparts/name')
if not os.path.exists(__location__+'/resources/programparts/name/nameservers.txt'):
	with open(__location__+'/resources/programparts/name/nameservers.txt', "a") as makeprot: #file used for listing network name servers for /connect functionality
		makeprot.write("")


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
	print "Welcome to the TechTem Network Client"
	print "Version 0.1"
	print "Type /help for command list"

#function for client splash screen
def net_client():
	boot()
	while 1:
		inp = raw_input(">")
		if inp:
			if inp[0] == '/':
				if inp.split()[0] == '/connect':
					try:
						data = inp.split()[1:]
					except: 
						data = None
					receivedip = makenameconnection(data)
					print receivedip
					print connectip(receivedip,data[1:])

				elif inp.split()[0] == '/dconnect':
					try:
						ip = inp.split()[1]
						data = inp.split()[2:]
					except:
						ip = None 
						data = None
					print connectip(ip,data)
				elif inp.split()[0] == '/start':
					try:
						data = inp.split()[1:]
					except: 
						data = None
					print startstandalone(data)
				elif inp.split()[0] == '/quit' or inp.split()[0] == '/leave' or inp.split()[0] == '/exit':
					quit()
				elif inp.split()[0] == '/clear':
					boot()
				elif inp.split()[0] == '/help' or inp.split()[0] == '/?':
					print "TechTem Network Client Commands:\n/connect + URL: retrieve address and connect\n/dconnect + IP: directly connect to IP\n/quit OR /leave: exits gracefully\n/help OR /?: displays this menu"
				else:
					print "Invalid command"

def clear(): #clear screen, typical way
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

def startstandalone(data): #used to start protocols not requiring connecting
	
	scriptname = data[1]
	compat = 'n'
	with open(__location__+'/resources/protocols/protlist.txt') as protlist:
		for line in protlist:
			if line == scriptname or line == scriptname + '\n' :
				compat = 'y'
	if compat == 'y':
		script = sys.modules[scriptname]
		varcheck = getattr(script,'variables')
		if len(varcheck) <= len(data):
			use = getattr(script,function)
			print 'success'
		else:
			print 'incorrect argument[s]'
	else:
		return 'failure - protocol not found'

	query = use(data,__location__)
	return query

def connectip(ip,data):
	try:
		host = ip.split(':')[0]
		port = int(ip.split(':')[1])
	except:
		return 'no host/port provided\n'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
	except:
		return "Server at " + ip + " not available\n"
	print "connection successful"
	return connectprotocolclient(s,data)

def makenameconnection(data):
	with open(__location__+'/resources/programparts/name/nameservers.txt', "r") as nservelist:
		for line in nservelist:
			if line.startswith('||'):
				try:
					host = line.split('||')[1].split(':')[0]
					port = int(line.split('||')[1].split(':')[1])
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.settimeout(2)
					s.connect((host,port))
					print "connection to name server successful"
					return connectprotocolclient(s,data)
				except Exception,e:
					print e

	#host = 'localhost'
	#port = 9010

	#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#s.settimeout(2)
	#try:
	#	s.connect((host, port))
	#except:
	#	return "Name server[s] not available"
	#print "Connection successful"
	#return connectprotocolclient(s,data)

def connectprotocolclient(s, data):

	ser = s
	identity = ser.recv(1024)
	compat = 'n'
	scriptname,function = identity.split(':')
	with open(__location__+'/resources/protocols/protlist.txt') as protlist:
		for line in protlist:
			if line == scriptname or line == scriptname + '\n' :
				compat = 'y'
	if compat == 'y':
		script = sys.modules[scriptname]
		varcheck = getattr(script,'variables')
		if len(varcheck) <= len(data):
			use = getattr(script,function)
			ser.sendall(compat)
			print 'success'

		else:
			print 'incorrect argument[s]'
			ser.sendall('no')
			resp = ser.recv(1024)
			ser.close
			return resp
	else:
		ser.sendall(compat)
		resp = ser.recv(1024)
		print resp
		ser.close
		return 'failure'

	query = use(ser,data,__location__)
	ser.close
	return query

net_client()