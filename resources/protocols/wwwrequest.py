#!/usr/bin/python2
import socket, os, sys
from time import sleep

variables = ['website']
standalone = False

def initialize(location):
    if not os.path.exists(location + '/resources/cache/wwwrequest'):
        os.makedirs(location + '/resources/cache/wwwrequest') #used to store info for protocols and client

def wwwrequest_client(s,data,location):

    initialize(location)
    filename = data[0]
    status = recv_file(s,filename,location)
    s.close
    return status

    #s.sendall('end\n')

def recv_file(s, name, location):
    cmd = 'get\n%s\n' % (name)
    s.sendall(cmd)
    r = s.recv(2)
    if r != 'ok':
        print "server says no"
        return '404\n'
    size = s.recv(16)
    size = int(size.strip())
    recvd = 0

    downloadslocation = location +'/resources/cache/wwwrequest/'

    newname = ''
    skippedchars = '/.:'
    for character in name:
        if character not in skippedchars:
            newname += character

    q = open(os.path.join(downloadslocation, newname),"wb")
    while size > recvd:
        sys.stdout.write(str((float(recvd)/size)*100)[:4]+ '%' + '\r')
        sys.stdout.flush()
        #print(str((float(recvd)/size)*100)[:4]+ '%' + '\r')
        data = s.recv(1024)
        if not data: 
            break
        recvd += len(data)
        q.write(data)
    s.sendall('ok')
    q.close()
    sys.stdout.write('100.0%\n')
    return '111\n'