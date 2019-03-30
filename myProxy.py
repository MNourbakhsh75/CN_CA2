import os
import sys
import socket
import threading
import re
import config
import log
import logMessage

global_lock = threading.RLock()

def launch():
    
    try:
        mySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        log.log(logMessage.launch)
        log.log(logMessage.createServer)
        mySocket.bind(('',config.PORT))
        log.log(logMessage.binding + str(config.PORT))
        mySocket.listen(config.MAXCON)
        log.log(logMessage.listen)

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


def routine(conn,addr):

    file_contents = []
    file_contents.append(logMessage.accept) #0
    file_contents.append(logMessage.connectFromLocalHost + str(addr[1]) + '\n') #1
    request = conn.recv(999999)
    file_contents.append(logMessage.clientHeader) #2
    file_contents.append(request.decode('utf-8'))  #3
    request = request.replace(b'HTTP/1.1',b'HTTP/1.0')
    request = removePath(request)
    # request = removeProxyConnection(request)
    request = changeUserAgent(request)
    print("request : \n",request)

    hostName = getHostName(request)
    print ("hostName : ",hostName)
    isFirst = True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostName, 80))
        file_contents.append(logMessage.openConnection+hostName.decode('utf-8')) #4
        s.sendall(request)
        file_contents.append(logMessage.proxySendReq) #5
        file_contents.append(request.decode('utf-8')) #6
        while 1:
            data = s.recv(999999)
            if (len(data) > 0):
                conn.sendall(data)
                if isFirst:
                    file_contents.append(logMessage.serverSendResp) #7
                    header = findHeader(data)
                    file_contents.append(header.decode('utf-8')) #8
                    file_contents.append(logMessage.proxySendResp) #9
                    file_contents.append(header.decode('utf-8')) #10
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
