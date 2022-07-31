# Server side script of socket programming
# Import all the necessary libraries
import socket
import threading
import time
import os
import tqdm
# Ip address of server
server_ip = '127.0.0.1'
port = 55555 # Port to connect the sockets
buffer = 1024 # This is buffer size, the size of chunks while reading a file
sepe = "<SEPARATOR>" # seperator while reading a file
# Starting Server
# Initializing server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the server socket with already provided server ip and port
server_socket.bind((server_ip, port))
# Start listening for connections on server_socket
server_socket.listen()
# Keep listening and wait for clients to join the server
print(f'Waiting for clients to join on server, {server_ip}:{port}...')
client_id = []# list of clients joined the server
user_names = []# List of user_names chosen by the clients
def send_all(chat_m): # Send all function broadcasts the message to entire group
    for client in client_id:
        client.send(chat_m) # send to all clients in client list
def admin_kick(name): # Function which allows admin to kick out other clients.This can be executed only by Admin
    if name in user_names: # if the name given to kick is present in client list, remove him from the list, notify the client and others and close the client socket.
        user_index=user_names.index(name)
        client_kicked=client_id[user_index]
        client_kicked.send('Yk'.encode('ascii'))
        client_id.remove(client_kicked)
        client_kicked.close()
        user_names.remove(name)
        send_all(f'{name} was removed by Admin!'.encode('ascii'))
        print(f'{name} was removed by Admin')
def interpret_client(client): # interpreting the messages sent by clients
    while True: # Until an exception arises keep on running the server
        try:
            # Broadcasting Messages
            msg= chat_m = client.recv(1024) # Receive message from client
            localtime = time.asctime(time.localtime(time.time())) # Note the time at which the client sent the message
            m2 = chat_m.decode('ascii')# decode the message sent by client
            if(m2.split(' ',1)[1]=="File"):# In case the message by client is File, it means that the client wants to send a file to the server and we must prepare the server to receive file
                recv_message = client.recv(buffer).decode() # First you will receive the file name and size from the client
                filename, size = recv_message.split(sepe)
                filename = os.path.basename(filename)
                size = int(size)
                progress = tqdm.tqdm(range(size), f"Receiving {filename}", unit="B", unit_scale=True,
                                     unit_divisor=1024) # tqdm for tracking the progress of file transfer
                with open('Transfer.txt', "wb") as f:
                    totalb=0
                    while True:
                        # read 1024 bytes from the socket (receive)
                        bytes_read = client.recv(1024)
                        totalb = totalb+len(bytes_read)
                        if totalb==size:
                            f.write(bytes_read)
                            # update the progress bar
                            progress.update(len(bytes_read))
                            print(progress)
                            # nothing is received
                            # file transmitting is done
                            break
                        # write to the file the bytes we just received
                        f.write(bytes_read)
                        # update the progress bar
                        progress.update(len(bytes_read))
                print("Done")
            elif(m2.split(' ',1)[1]=="Bye"): # If the message is Bye, it means that the client quit and broadcast this message to all group members
                print(m2.split(' ',1)[0]," has left the chat!",","," Time: ",localtime)
                index = client_id.index(client)
                client.send('Left'.encode('ascii')) # send and encoded Left to client who put Bye message
                client_id.remove(client) # Remove the client who quit the chat
                client.close() # close the client
                user_name = user_names[index]
                # Broadcast about left client to all other clients in the chat
                send_all('{} left!'.format(user_name).encode('ascii'))
                user_names.remove(user_name)
                break
            else:
                if msg.decode('ascii').startswith('REMOVE'):  # removing a user
                 if user_names[client_id.index(client)]=='Admin': # remove and block commands can be executed only by Admin
                    user_kicked=msg.decode('ascii')[7:]
                    admin_kick(user_kicked) # remove the user out with admin_kick function we defined earlier
                 else:
                    pass
                elif msg.decode('ascii').startswith('BLOCK'):  # Blocking a user
                 if user_names[client_id.index(client)] == 'Admin':
                    user_banned=msg.decode('ascii')[6:]
                    admin_kick(user_banned) # First we kick out the user we want to block
                    # Write the blocked username to the blocked.txt file
                    # so that when the user tries to login again it would not allow
                    with open('block_list.txt','a') as f:
                        f.write(f'{user_banned}\n')
                    print(f'{user_banned} is blocked!.')
                 else:
                     pass
                else:
                 send_all(chat_m) # if the message is a normal one, broadcast the message to all group members
                 print("Message from ", m2, " ,", "Time:", localtime)
        except:
            # Removing And Closing Clients
            if client in client_id:
             index = client_id.index(client)
             client_id.remove(client)
             client.close()
             user_name = user_names[index]
             send_all('{} left!'.format(user_name).encode('ascii'))
             user_names.remove(user_name)
             break
def recv_request():
    while True:
        # Accept Connection from a client
        client, ip = server_socket.accept()
        # Request And Store User name
        client.send('USER'.encode('ascii'))
        user_name = client.recv(1024).decode('ascii')
        with open('block_list.txt','r') as f:  # Check if the user name requesting connection is in admin's blocked list
            bans=f.readlines()
        if user_name+'\n' in bans: # If the user is in blocked list, donot accept the connection.
            client.send('BLOCK'.encode('ascii'))
            client.close()
            continue
        if user_name == 'Admin': # In case the user is not in blocked list, continue and if user is admin
            client.send('PASS'.encode('ascii')) # Ask him for a password, which is checked by server
            password=client.recv(1024).decode('ascii') # receive password from admin
            if password != 'computer-networks': # Password is 'computer-networks', if password is wrong
                client.send('REFUSE'.encode('ascii')) # Refuse the connection and close the client
                client.close()
                continue
        user_names.append(user_name) # If connection is accepted add the client to clients list
        client_id.append(client)
        print('Accepted new connection from {}:{}, username: {}'.format(*ip,user_name))
        # Print And Broadcast that a new user/client joined the chat, which notifies every one in chat
        send_all("{} joined!".format(user_name).encode('ascii'))
        client.send('Connected to server!'.encode('ascii')) #Notify the client that it successfully connected to server
        # Start Handling Thread For Client
        thread = threading.Thread(target=interpret_client, args=(client,))
        thread.start()
recv_request()   # The server receives a request and then the thread started interprets the client