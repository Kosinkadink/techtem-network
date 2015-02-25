#!/usr/bin/python2
import os
import sys
import socket
import select
from time import strftime

LOG=[""] #for tracking the conversation. currently is not limited in length. someone can limit this if they so choose.
servercommands = ["/pm", "/peoplecount"]

def save(): 
	print ("Save function not implemented yet.")
def timestamp():
	return "<" + strftime("%H:%M:%S") + "> "

def chat_client():

        name = None
        tripcode = None
        host = None
        port = None
        if os.path.isfile("settings.txt"):
                with open("settings.txt") as settingsfile:
                        for line in settingsfile:
                                if line.split()[0] == "name":
                                        name = line[5:].replace("\n","")
                                if line.split()[0] == "tripcode":
                                        tripcode = line[9:].replace("\n", "")
                                if line.split()[0] == "host":
                                        host = line[5:].replace("\n","")
                                if line.split()[0] == "port":
                                        port = int(line[5:].replace("\n",""))

	#request information
        if name == None:
	        name = raw_input("Name (optional): ")
	if name == "":
		name = "Anonymous" #keeping it simple. having another variable for dispname will only confuse.
        if tripcode == None:
	        tripcode = raw_input("Tripcode (also optional): ")
        if host == None:
                host = raw_input("Server IP: ")
        if port == None:
                while not port:
                        try:
                                port = int(raw_input("Server Port: "))
                        except:
                                print "Invalid port. Try again."

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	print host
        print port
	# connect to remote host
	try :
		s.connect((host, port))
	except :
		print 'Unable to connect'
		sys.exit()
	
	print 'Connected to remote host.'
	


	sys.stdout.write("\n[" + name + "] "); sys.stdout.flush()
 
	while 1:
		socket_list = [sys.stdin, s]
		 
		# Get the list sockets which are readable
		ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
		 
		for sock in ready_to_read:			 
			if sock == s:
				# incoming message from remote server, s
				data = sock.recv(4096)
				if not data :
					print '\nDisconnected from chat server'
					sys.exit()
				else :
					LOG.append(timestamp() + data) #defined at the beginning. adds the new data to the LOG.
					os.system('cls' if os.name == 'nt' else 'tput reset') #cross platform screen clearing. this just in, clears the ENTIRE SHELL
					sys.stdout.write('\n'.join(LOG[:])) #prints the entire log. alll of it.
					sys.stdout.write('\n\n[' + name + '] ') # skips to new first line, rewrites name.
					sys.stdout.flush()
					
			else :
				# user entered a message
				message = sys.stdin.readline().replace("\n", "")
				if message:
				        if message[0] == "/" and message.split()[0] not in servercommands:
					        #that message was a command
        					if message.split()[0] == "/changename": 
	        					name = message[len(message.split()[0])+1:].replace("\n","")
							if not name:
								name = "Anonymous"
		        			elif message.split()[0] == "/changetripcode":
							tripcode = message[len(message.split()[0])+1:].replace("\n","")
						elif message.split()[0] == "/quit" or message.split()[0] == "/leave":
							save() #dummy function for now. will implement an option to save a local copy of the recorded chat. otherwise, all variables are flushed. will be off by default.
        						quit()
						elif message.split()[0] == "/help" or message.split()[0] == "/?":
							sys.stdout.write("\nThanks for using the techtemchat client. Here are the commands you currently have available:\n/changename + new name: changes your name\n/changetripcode + new tripcode: changes your trip code.\n/quit OR /leave: exits gracefully\n/help OR /?: Displays this menu.\n")						
						else:
							print "Invalid command"
					else:
						data = message + "\n" + name + "\n" + tripcode
						s.send(data)
				sys.stdout.write('[' + name + '] ')
				sys.stdout.flush() 

if __name__ == "__main__":

	sys.exit(chat_client())
