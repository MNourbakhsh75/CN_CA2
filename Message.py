launch = "Proxy launched"
createServer = "Creating server socket..."
binding = "Binding socket to port "
listen = "Listening for incoming requests...\n"
accept = "Accepted a request from client!"
clientHeader = "Client sent request to proxy with headers:\n"
connectFromLocalHost = "connect to [127.0.0.1] from localhost [127.0.0.1] "
openConnection = "Proxy opening connection to server "
proxySendReq = "Proxy sent request to server with headers:\n"
serverSendResp = "Server sent response to proxy with headers:\n"
proxySendResp = "Proxy sent response to client with headers:\n"
accessToBlockSite = "Client try to access a block site "
blockSiteResp = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n<!DOCTYPE html><html lang="en"><body>This site is blocked by proxy</body></html>'
mailSubject = b'Subject: Proxy Alert!\r\n\r\n'
sendMailToAdmin = "Proxy sending email to admin"
navbar = b'<div style="overflow: hidden;background-color: #333;height: 30px;font-size: 25px;">hello</div>\r\n'
permissionDenied = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n<!DOCTYPE html><html lang="en"><body style="color:red">permission denied</body></html>'
notEnoughVolume=b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n <!DOCTYPE html > <html lang = "en" ><body> You dont have enough volume </body ></html >'
