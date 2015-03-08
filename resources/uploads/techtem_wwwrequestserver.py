#!/usr/bin/python2
import sys, socket, select, os, threading, urllib2
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
if not os.path.exists(__location__+'/resources/programparts/wwwrequest'): os.makedirs(__location__+'/resources/programparts/wwwrequest')
if not os.path.exists(__location__+'/resources/programparts/wwwrequest/approvedfiles.txt'):
	with open(__location__+'/resources/programparts/wwwrequest/approvedfiles.txt', "a") as makeprot:
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
			elif inp == '?':
				print 'www request online at 9012'


def wwwrequest_server(s):

	clientsocket = s									   

	data = s.recv(1024)
	cmd = data[:data.find('\n')]

	try:
		if cmd == 'get':
			x, file_name, x = data.split('\n', 2)
			print file_name

			website = urllib2.urlopen(file_name) #look up website

			print "website found"
			s.sendall('ok')

			data = website.read()
			s.sendall('%16d' % len(data))
			s.sendall(data)
			s.recv(2)

			print 'success'
		return
	except Exception,e:
		print str(e)
		s.sendall('no')
		return

def servergen():
	print 'server started\n'
	# create a socket object
	serversocket = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM) 

	# get local machine name
	host = ""				   
	port = 9012

	# bind to the port
	serversocket.bind((host, port))								  

	# queue up to 10 requests
	serversocket.listen(10)										   

	while 1:
		# establish a connection
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))
		try:
			clientsocket.sendall('wwwrequest:wwwrequest_client')
			compat = clientsocket.recv(1)
			if compat != 'y':
				clientsocket.sendall('need *wwwrequest* protocol\n')
				print 'does not have protocol'
				clientsocket.close
			else:
				print 'HAS protocol'

				wwwrequestthread = threading.Thread(target=wwwrequest_server,args=(clientsocket,))
				wwwrequestthread.daemon = True
				wwwrequestthread.start()

				clientsocket.close
				print threading.activeCount()
			print("Disconnection by %s with data received\n" % str(addr))
		except Exception,e:
			print str(e) + '\n'
	
	print 'closing now'		
	serversocket.close()

threads = []
serverprocess = threading.Thread(target=servergen)
threads.append(serverprocess)
serverprocess.daemon = True
serverprocess.start() #starts server process in another thread
serverterminal() #starts command input