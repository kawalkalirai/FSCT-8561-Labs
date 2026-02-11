import socket
# import uses pythons networking library

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 55457)) 
s.listen(1)
print("Lab 1 Stateful Server is listening on port 55457...")

# uses ipv4 and tcp, binds 127... ip and on same port as before

while True:
    conn, addr = s.accept()
    print(f"\nLOG: New connection established from {addr}")

# accepts connection and writes connection established
  
    user = None 

    try:
        while True:
            data = conn.recv(1024).decode().strip()
            if not data: 
                break
# while true creates the persistent connection, conn.rev(1024) -> server is listening and 1024 is the buffer size
          
            parts = data.split(' ', 1)
            cmd = parts[0].upper()
            payload = parts[1] if len(parts) > 1 else ""
          
# splits raw data into command and text
          
            if cmd == "HELLO" and not user:
                user = payload
                conn.send(f"OK Welcome {user}".encode())
                print(f"LOG: User '{user}' has authenticated.")
# stores username
            elif not user:
                conn.send("ERROR Please send HELLO [username] first".encode())
                print(f"LOG: Rejected message from {addr} - Authentication required.")
              
# client has to verify themselves first
          
            elif cmd == "MSG":
                if not payload:
                    conn.send("ERROR Message content cannot be empty".encode())
                    print(f"LOG: User '{user}' sent an empty MSG command.")
                else:
                    print(f"[{user}]: {payload}")
                    conn.send("OK".encode())

            elif cmd == "EXIT":
                conn.send("OK Goodbye".encode())
                print(f"LOG: User '{user}' requested EXIT.")
                break

            else:
                conn.send("ERROR Invalid Command Format".encode())
                print(f"LOG: Unknown command '{cmd}' received from {user}.")

  # server accepts text, catches errors and invalid commands and requests exit
  
    except Exception as e:
        print(f"LOG ERROR: {e}")
        
    finally:
        conn.close()
        print(f"LOG: Connection with {addr} has been closed.")

  # closes connection
