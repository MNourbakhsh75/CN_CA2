import config
import datetime
File = open(config.logging_logFile, 'w+')

def currentTime():
        ct = datetime.datetime.now()
        return '[' + ct.strftime("%d/%b/%Y:%H:%M:%S") + '] '

def log(data):
        if config.logging_enable:
                File.write(currentTime() + data + '\n')

def logHeader(data):
        time = currentTime()
        dash = "----------------------------------------------------------------------"
        if config.logging_enable:
                File.write(time + '\n' + dash + '\n' + data + dash + '\n')