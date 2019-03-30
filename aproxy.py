import os
import sys
import socket
import re
import config
import asyncio

async def launch(loop):

    try:
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        mySocket.bind(('', config.PORT))

        mySocket.listen(config.MAXCON)
        mySocket.setblocking(False)
        print("Proxy is launched on port", config.PORT)

    except socket.error as se:
        if mySocket:
            mySocket.close()
        print(se)
        sys.exit(1)

    while 1:
        conn, addr = await loop.sock_accept(mySocket)
        loop.create_task(routine(conn,loop))


def getHostName(req):
    splitLine = req.splitlines()
    hostName = ""
    for s in splitLine:
        sl = s.split()
        if sl[0] == b'Host:':
            hostName = sl[1]
            break
    return hostName

def removePath(req):
    host = getHostName(req)
    # host = host.encode('utf-8')
    ds = b'http://' + host
    return req.replace(ds,b'')

async def routine(conn,loop):

    request = await loop.sock_recv(conn,999999)
    print ("request :\n",request)
    request = request.replace(b'HTTP/1.1', b'HTTP/1.0')
    # request = removeProxyConnection(request)
    request = removePath(request)
    print("request : \n", request)

    hostName = getHostName(request)
    print("hostName : ", hostName)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        await loop.sock_connect(s,(hostName,80))
        await loop.sock_sendall(hostName,request)
        # s.connect((hostName, 80))
        # s.sendall(request)
        while 1:
            # receive data from web server
            data = await loop.sock_recv(999999)
            if (len(data) > 0):
                #print (data)
                await loop.sock_sendall(conn,data)  # send to browser/client
            else:
                break
        s.close()
        conn.close()
    except socket.error as e:
        if s:
            s.close()
        if conn:
            conn.close()
        print("exception:", e)
        sys.exit(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(launch(loop))
