import socket
import sys
import Message

CHUNK_SIZE = 1024

class sendMail:

    def send(self,msg):

        self.conn = self.connectToMailServer()
        self.sayHeloToServer()
        self.login()
        self.mailFrom()
        self.mailRecipient()
        self.sendData(msg)
        self.sayByeToServer()
        self.conn.close()
    def connectToMailServer(self):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect((b'mail.ut.ac.ir', 587))
            recv = sock.recv(CHUNK_SIZE)
            # print(recv.decode())
            return sock
        except socket.error as identifier:
            print(identifier)
            sys.exit(1)

    def sayHeloToServer(self):
        heloCommand = b'HELO mail.ut.ac.ir\r\n'
        self.conn.send(heloCommand)
        recv = self.conn.recv(CHUNK_SIZE)
        # print(recv.decode())
    
    def login(self):
        auth2 = b'AUTH PLAIN AGthemVtaS5hbGkAMTM3NC5BbGlr\r\n'
        self.conn.send(auth2)
        recv = self.conn.recv(CHUNK_SIZE)
        # print(recv.decode())

    def mailFrom(self):
        mailFrom = b'MAIL FROM:<kazemi.ali@ut.ac.ir>\r\n'
        self.conn.send(mailFrom)
        recv = self.conn.recv(CHUNK_SIZE)
        # print(recv.decode())
    
    def mailRecipient(self):
        rcptTo = b'RCPT TO:<m.nourbakhsh75@hotmail.com>\r\n'
        self.conn.send(rcptTo)
        recv = self.conn.recv(CHUNK_SIZE)
        # print(recv.decode())

    def sendData(self,msg):
        data = b'DATA\r\n'
        self.conn.send(data)
        recv= self.conn.recv(CHUNK_SIZE)
        # print(recv.decode())
        self.conn.send(Message.mailSubject)
        self.conn.send(msg)
        self.conn.send(b'\r\n.\r\n')
        recv2 = self.conn.recv(CHUNK_SIZE)
        # print(recv2.decode())

    def sayByeToServer(self):
        bye = b'QUIT\r\n'
        self.conn.send(bye)
        recv = self.conn.recv(CHUNK_SIZE)
        # print(recv.decode())

