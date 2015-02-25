import socket

variables = ['url']

def name(client, url, none):

	rqst = str(url[0])
	s = client
	print 'requesting ip'
	s.send(rqst)
	# Receive no more than 1024 bytes
	ip = s.recv(1024)

	return ip

def name_server(s):

	clientsocket = s									   

	rqst = clientsocket.recv(1024)
	print rqst
	message = searchurls(rqst)
	print message[:-1]
	clientsocket.sendall(message)

def searchurls(rqst):
	ip = '404\n'
	with open(__location__+'/resources/programparts/name/techtemurls.txt') as file:
		for line in file:
			url = line.split("||")
			if url[0] == rqst:
				ip = url[1]
				break
	return ip