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
import time
from gzip import GzipFile
from bs4 import BeautifulSoup
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import zlib
CHUNK_SIZE = 1000000
global_lock = threading.RLock()
users = []
for u in config.accounting_users:
    users.append(u)

myCache = {}
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
    pathName = b''
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


# def removeProxyConnection(req):

#     print("s::::\n\n",s)
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

def isHttp(req):
    index = req.find(b'https')
    if index == -1 :
        return True
    else:
        return False
def changeResponseBody(conn,data):
    File = open('kha.txt','w+')
    print("changeResponseBody")
    z = b''
    for d in data:
        z +=d
    k =''
    index = 0
    index = z.find(b'<html')
    print (index)
    if index == -1 :
        body = z.split(b'\r\n\r\n', 1)[1]
        decompressed_data=zlib.decompress(body, 16+zlib.MAX_WBITS)
        index = decompressed_data.find(b'<html')
        soup = BeautifulSoup(decompressed_data[index:len(decompressed_data)], 'html.parser')
        new_div = soup.new_tag('div')
        new_div.string = config.HTTPInjection_body
        soup.body.insert(0, new_div)
        k = z.split(b'\r\n\r\n', 1)[0].decode() +'\r\n\r\n'+  str(soup.html)
    else:
        soup = BeautifulSoup(z[index:len(z)], 'html.parser')
        new_div = soup.new_tag('div')
        new_div.string = config.HTTPInjection_body
        soup.body.insert(0, new_div)
        k = z[0:index].decode() + str(soup.html)
    File.write(k)
    conn.send(k.encode())    
    

def checkVolume(user):

    if user['volume'] <= 0:
        return False

    return True
def checkIp(addr):
    allow = False
    user = ''
    for u in users:
        if u['IP'] == str(addr[0]):
            allow = True
            user = u
            break
    return allow,user
def sendMailToAdmin(req):
    host = getHostName(req)
    msg = Message.accessToBlockSite.encode() + host + b':\r\n' + req
    # print(msg)
    mail = sendMail.sendMail()
    mail.send(msg)
    log.log(Message.sendMailToAdmin)

def changeEncoding(req):
    newReq = req
    i = req.find(b'accept-encoding:')
    if i != -1:
        newReq = req.replace(b'accept-encoding: gzip,', b'accept-encoding:', 1)
    else:
        newReq = req.replace(b'Accept-Encoding: gzip,', b'Accept-Encoding:', 1)
    # print ("rrrr:\n\n\n",newReq)
    return newReq
def checkIndexpage(host,path):

    index = b'http://' + host + b'/'
    if index == path:
        return True

    return False

def checkForPragma(data):
    pIndex = data.find(b'\r\nPragma:')
    if pIndex != -1 :
        return True
    return False

def createCacheData(data,path):
    c = b''
    for d in data:
        c += d
    myCache[path] = c
    # print (myCache)
def routine(conn,addr):
    allow,user = checkIp(addr)
    if not allow:
        conn.send(Message.permissionDenied)
        conn.close()
        sys.exit(1)
    else:
        if not checkVolume(user):
            conn.send(Message.notEnoughVolume)
            conn.close()
            sys.exit(1)

    file_contents = []
    file_contents.append(Message.accept) #0
    file_contents.append(Message.connectFromLocalHost + str(addr[1]) + '\n') #1
    request = conn.recv(CHUNK_SIZE)
    http = isHttp(request)
    file_contents.append(Message.clientHeader) #2
    try:
        file_contents.append(request.decode())  #3
    except UnicodeDecodeError:
        file_contents.append(str(request))  #3
    request = request.replace(b'HTTP/1.1',b'HTTP/1.0')
    pathName = getPathName(request)
    request = removePath(request)
    request = changeEncoding(request)
    request = changeUserAgent(request)
    print("request : \n",request)
    hostName = getHostName(request)
    print ("hostName : ",hostName)
    print ('path :',pathName)
    if config.restriction_enable:
        block,notify = checkForRestriction(hostName)
        if block:
            conn.send(Message.blockSiteResp)
            log.log(Message.accessToBlockSite+hostName.decode())
            if notify:
                sendMailToAdmin(request)
            conn.close()
            sys.exit(1)
    if pathName in myCache:
        print ("hit")
        conn.sendall(myCache[pathName])
        conn.close()
        return
    else:
        print ("miss")
    isFirst = True
    oo = True
    ooo = True
    cachedAllow = False
    cachedData = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostName, 80))
        file_contents.append(Message.openConnection+hostName.decode()) #4
        s.sendall(request)
        file_contents.append(Message.proxySendReq) #5
        try:
            file_contents.append(request.decode())  # 6
        except UnicodeDecodeError:
            file_contents.append(str(request))  # 6
        while 1:
            data = s.recv(CHUNK_SIZE)
            if (len(data) > 0):
                # user['volume'] = user['volume']-CHUNK_SIZE
                # if not checkVolume(user):
                #     data = Message.notEnoughVolume
                #     print('ooopppppsss\n\n\n')
                    # if ooo:
                        # conn.sendall(data)
                        # ooo = False
                # time.sleep(10)
                # print(data)
                if not checkIndexpage(hostName,pathName):
                    conn.sendall(data)
                # else:
                if oo:
                    oo = False
                    p = checkForPragma(data)
                    if not p:
                        cachedAllow = True
                if cachedAllow:
                    cachedData.append(data)

                if isFirst:
                    file_contents.append(Message.serverSendResp) #7
                    header = findHeader(data)
                    # print(header)
                    file_contents.append(header.decode()) #8
                    file_contents.append(Message.proxySendResp) #9
                    file_contents.append(header.decode()) #10
                    writeToFile(file_contents)
                    isFirst = False
            else:
                print('bbb')
                break

        if http and checkIndexpage(hostName,pathName) and config.HTTPInjection_enable:
            print ("kha")
            changeResponseBody(conn,cachedData)
    
    
        createCacheData(cachedData,pathName)
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
