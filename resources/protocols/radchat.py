#!/usr/bin/python2
import os,sys,socket,select
from time import strftime

variables = ['name','tripcode']
servercommands = ["/pm", "/peoplecount"]

def date():
 	return strftime(".%Y-%m-%d")

def chat_client(inputsocket,data,location):

 	#initialize radchat client files
 	if not os.path.exists(location+'/resources/programparts/radchat'): os.makedirs(location+'/resources/programparts/radchat')
 	if not os.path.exists(location+'/resources/programparts/radchat/logs'): os.makedirs(location+'/resources/programparts/radchat/logs')
	if not os.path.exists(location+'/resources/programparts/radchat/settings.txt'):
		with open(location+'/resources/programparts/radchat/settings.txt', "a") as settingsfile:
			settingsfile.write("")

 	#introduce variables
	name = data[0]
 	tripcode = data[1]

	#if there is a settings file, read it
	if os.path.isfile(location + '/resources/programparts/radchat/settings.txt'):
		with open(location + '/resources/programparts/radchat/settings.txt') as settingsfile:
			for line in settingsfile:
				if line.split()[0] == "name":
					name = line[5:].replace("\n","")
				if line.split()[0] == "tripcode":
					tripcode = line[9:].replace("\n", "")
				if line.split()[0] == "host":
					host = line[5:].replace("\n","")
				if line.split()[0] == "port":
					port = int(line[5:].replace("\n",""))

	s = inputsocket

	sys.stdout.write("\n[{}] ".format(name)); sys.stdout.flush()
 
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
					return
				else :
					with open(location+'/resources/programparts/radchat/logs/client'+date(), "a") as log:
						log.write(data + "\n")
					os.system('cls' if os.name == 'nt' else 'tput reset') #cross platform screen clearing. this just in, clears the ENTIRE SHELL
					with open(location+'/resources/programparts/radchat/logs/client'+date(), "r") as log:
						sys.stdout.write(log.read()) #prints the entire log. alll of it.
					sys.stdout.write('\n\n[{}] '.format(name)) # skips to new first line, rewrites name.
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
						elif message.split()[0] == "/exit" or message.split()[0] == "/quit" or message.split()[0] == "/leave":
							print "Leaving chat server."
							return
						elif message.split()[0] == "/help" or message.split()[0] == "/?":
							sys.stdout.write("\nThanks for using the radchat client. Here are the commands you currently have available:\n/changename + new name: changes your name\n/changetripcode + new tripcode: changes your trip code.\n/quit OR /leave: exits gracefully\n/help OR /?: Displays this menu.\n")
						else:
							print "Invalid command"
					else:
						#format all the data and send it
						s.send("{}\n{}\n{}".format(message, name, tripcode))
				sys.stdout.write('[{}] '.format(name))
				sys.stdout.flush()