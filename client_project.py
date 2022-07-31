# Client side script of socket programming
# import necessary libraries
import socket
import threading
import sys
import os
import tqdm
# You will be asked for a username and please note that Admin username is reserved for Admin only
user_id = input("Enter Username: ") # Enter user name
if user_id == 'Admin':# If username is Admin, you will be asked to enter the password which other users donot know.
    password=input("Enter your Admin password: ")
buffer = 1024 # Its the size of chunks during file transfer
sepe = "<SEPARATOR>"
server_ip='127.0.0.1' # Give ip address of server you want to connect with
port=55555 # Port
# Connecting To Server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip,port))
st_flag = False # Global variable to track if thread has to stop or keep running
def message_from_server(): # Function which receives message from server and interprets it.
    while True:            # While there is no exception and the client stays in chat, continue.
        global st_flag
        if st_flag:        # If stop thread flag is True, implies it is time to close this client.
            os._exit(1)
            break
        try:
            # Receive Message From Server
            chat_m = client_socket.recv(1024).decode('ascii')
            x=chat_m.split(' ',1)[0]
            y=x.split(':',1)[0]
            if chat_m=="Left":    # If server sends Left, it means that you sent Bye and you quit
                client_socket.close() # Close the socket as you quit the chat
                print("You Quit")
                st_flag = True # Set the stop flag to true
            elif chat_m=="Yk": # If server send Yk, it means that you were kicked out of chat
                client_socket.close() # Close the socket after you being kicked out by Admin
                print("You were removed by admin")
                st_flag = True # set the stop flag to true
            elif chat_m == 'USER': # If the server sends USER it means it is requesting username of client
                client_socket.send(user_id.encode('ascii'))
                follow_message=client_socket.recv(1024).decode('ascii')
                if follow_message == 'PASS': # If the username message is followed by PASS message it means it is Admin that is logging in
                    client_socket.send(password.encode('ascii')) # Send the password entered by admin
                    if client_socket.recv(1024).decode('ascii') == 'REFUSE':# If you enter wrong password, server refuses the connection
                        print("Wrong Admin Password!!")
                        client_socket.close()
                        st_flag = True
                elif follow_message == 'BLOCK': # If you are in the banned list of Admin, your connection will be refused.
                    print("You are Blocked by admin. No connection possible.")
                    client_socket.close()
                    st_flag = True
            else:
                if(y!=user_id):
                 print(chat_m) # If its a normal message just print it out.
        except:
            # Close Connection When Error/Exception arises
            print("An error occured!")
            client_socket.close()
            break
# Sending Messages To Server
def message_to_server():
    while True:
        global st_flag
        if st_flag:
            os._exit(1)
            break
        inp=input() # Take input message from client
        chat_m = '{}: {}'.format(user_id,inp)
        if chat_m[len(user_id)+2:].startswith('/'): # if the message starts with / it means its a command and can be executed only by Admin
            if user_id == 'Admin':
             if chat_m[len(user_id) + 2:].startswith('/remove'):# if /kick command is executed, send a message to server notifying the same
                 client_socket.send(f'REMOVE {chat_m[len(user_id)+2+8:]}'.encode('ascii'))
             elif chat_m[len(user_id) + 2:].startswith('/block'):# if /ban command is executed, send a message to server notifying the same
                 client_socket.send(f'BLOCK {chat_m[len(user_id)+2+7:]}'.encode('ascii'))
            else:# If someone other than admin tries to execute the commands
             print("Commands can be executed only by Admin") # Notify that only admin can execute these commands
        elif inp == "File": # If the message is File, then it means that the client wants to send a file next.
            client_socket.send(chat_m.encode('ascii'))
            filename = r"/Users/harshithasagiraju/Library/Mobile Documents/com~apple~TextEdit/Documents/test_file.txt" # Path of the file to transfer
            size = os.path.getsize(filename)
            client_socket.send(f"{filename}{sepe}{size}".encode()) # Send the name and size of file to server
            progress = tqdm.tqdm(range(size), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "rb") as f:
                totalb=0
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(buffer) # Read bytes from the file
                    totalb=totalb+len(bytes_read)
                    if totalb==int(size): # Break out of reading if the entire file is read
                        client_socket.sendall(bytes_read)
                        progress.update(len(bytes_read))
                        print(progress)
                        break
                    # we use sendall to assure transmission in
                    # busy networks
                    client_socket.sendall(bytes_read)
                    progress.update(len(bytes_read))
            print("Done")
        else: # if some other normal message is typed, send it to server and the server broadcasts it to all the group members
         if(st_flag==False): # Only if thread is still running
          client_socket.send(chat_m.encode('ascii'))
recv_th = threading.Thread(target=message_from_server)# create thread1 for receiving from server
recv_th.start() # start the receiving thread
send_th = threading.Thread(target=message_to_server)# create thread2 for sending to server
send_th.start() # start the sending thread
recv_th.join() # Join the threads
send_th.join()
exit(0) # Finally exit.
