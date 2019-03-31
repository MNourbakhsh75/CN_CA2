import os
import sys
import socket
import threading
import re
import config
import log
import Message
import json
import sendMail

global_lock = threading.RLock()

def launch():
    
    try:
        mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        log.log(Message.launch)
        log.log(Message.createServer)
        mySocket.bind(('',config.PORT))
        log.log(Message.binding + str(config.PORT))
        mySocket.listen(config.MAXCON)
        log.log(Message.listen)

    except socket.error as se:
        if mySocket:
            mySocket.close()
        print (se)
        sys.exit(1)

    threads = []
    while 1:
        conn,addr = mySocket.accept()
        
        d = threading.Thread(name='d',
                            target=routine, args=(conn, addr))
        d.setDaemon(True)
        threads.append(d)
        d.start()
        
    mySocket.close()


def getPathName(req):
    splitLine = req.splitlines()
    pathName = ""
    if len(splitLine) != 0 :
        fl = splitLine[0].split()
        if len(fl) >= 2 :
            pathName = fl[1]
    return pathName

def getHostName(req):
    splitLine = req.splitlines()
    hostName = b''
    for s in splitLine:
        sl = s.split()
        if sl[0] == b'Host:':
            hostName = sl[1]
            break
    return hostName


def removeProxyConnection(req):
    splitLine = req.splitlines()
    for i in range(len(splitLine)):
        s1 = splitLine[i].split()
        if s1[0] == 'Proxy-Connection:':
            del splitLine[i]
            break

    return '\r\n'.join(splitLine)

def removePath(req):
    host = getHostName(req)
    # host = host.encode('utf-8')
    ds = b'http://' + host
    return req.replace(ds,b'',1)

def findHeader(data):
    header = ''
    index = data.find(b'\r\n\r\n')
    index += 4
    header = data[0:index]
    return header

def changeUserAgent(req):
    newReq = req
    if config.privacy_enable:
        baseIndex = req.find(b'User-Agent: ') + 12
        offsetIndex = req[baseIndex:len(req)-1].find(b'\r\n')
        agent = config.privacy_userAgent.encode('utf-8')
        newReq = req.replace(req[baseIndex:baseIndex+offsetIndex],agent,1)
    return newReq

def writeToFile(data):
    # while global_lock.locked():
    #     continue
    global_lock.acquire()
    for i in range(len(data)):
        if i == 3 or i == 6 or i == 8 or i == 10 :
            log.logHeader(data[i])
        else:
            log.log(data[i])
    global_lock.release()

def checkForRestriction(host):
    block = False
    notify = False
    for t in config.restriction_targets:
        tb = t['URL'].encode('utf-8')
        if tb == host:
            block = True
            notify = t['notify']
            
    return block,notify

def sendMailToAdmin(req):
    host = getHostName(req)
    msg = Message.accessToBlockSite.encode() + host + b':\r\n' + req
    # print(msg)
    mail = sendMail.sendMail()
    mail.send(msg)
def routine(conn,addr):

    file_contents = []
    file_contents.append(Message.accept) #0
    file_contents.append(Message.connectFromLocalHost + str(addr[1]) + '\n') #1
    request = conn.recv(999999)
    file_contents.append(Message.clientHeader) #2
    file_contents.append(request.decode())  #3
    request = request.replace(b'HTTP/1.1',b'HTTP/1.0')
    request = removePath(request)
    # request = removeProxyConnection(request)
    request = changeUserAgent(request)
    print("request : \n",request)
    hostName = getHostName(request)
    print ("hostName : ",hostName)

    if config.restriction_enable:
        block,notify = checkForRestriction(hostName)
        if block:
            conn.send(Message.blockSiteResp)
            log.log(Message.accessToBlockSite+hostName.decode())
            if notify:
                sendMailToAdmin(request)
            conn.close()
            sys.exit(1)

    isFirst = True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostName, 80))
        file_contents.append(Message.openConnection+hostName.decode()) #4
        s.sendall(request)
        file_contents.append(Message.proxySendReq) #5
        file_contents.append(request.decode()) #6
        while 1:
            data = s.recv(999999)
            if (len(data) > 0):
                conn.sendall(data)
                if isFirst:
                    file_contents.append(Message.serverSendResp) #7
                    header = findHeader(data)
                    file_contents.append(header.decode()) #8
                    file_contents.append(Message.proxySendResp) #9
                    file_contents.append(header.decode()) #10
                    writeToFile(file_contents)
                    isFirst = False
            else:
                break

        
        s.close()
        conn.close()
    except socket.error as e:
        if s:
            s.close()
        if conn:
            conn.close()
        print("exception:",e)
        sys.exit(1)


launch()
