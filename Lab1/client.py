import socket

#import uses pythons networking library 

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect(('127.0.0.1', 55457))

#using IPv4 and TCP connection like last lab and connecting to ip 127... and same port as before

username = input("Enter your username to login: ")
c.send(f"HELLO|{username}".encode())
print(f"Server response: {c.recv(1024).decode()}")

#the first prompt, and uses bytes

while True:
    print("\nAvailable Commands: MSG [text] or EXIT")
    user_input = input("> ")

#while true starts the persistent connection, and give options on what the client can say "MSG or EXIT"

    c.send(user_input.encode())

#uses the user input into the pipe

    response = c.recv(1024).decode()
    print(f"Server says: {response}")

#wait for the server to recieve the message

    if "Goodbye" in response:
        break

c.close()

#exit logic
