# Library covered in lab 1.
import socket
# Library covered in lab 3.
import hashlib
import pyotp

# Lab 3 code
# Function: Stores user passwords as a hash and OTP secret key.
# Security Purpose: As said in Part D: Negative Space Decision, having only the hashed password reduces the attack surface incase an attack gets access to USER_DB information.
USER_DB = {
    "kawal": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", # hash for 'password'
    "kawal_secret": "JBSWY3DPEHPK3PXP" # base32 secret for Google Authenticator
}

# Lab 1 code
# Function: Sets up the TCP socket on port 5555, the port I picked in Lab 1.
# Security Purpose: Using a stateful TCP connection so the server can keep the connection up and remember the challenge_token when doing the multi-part verifcation
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen(1)
print("Server listening on port 5555...")

while True:
    # Lab 1 code
    # Function: Accepts incoming client connections.
    # Security Purpose: As said in Part A: The system acts as the gateway to accept the connection before any authentication begins.
    conn, addr = server.accept()
    print(f"Connection from {addr}")

    try:
        # Lab 5 code
        # Function: Receives first message and splits it into two parts.
        # Security Purpose: As said in Part B: Using split('|', 1) enforces parameter protections. It ensures attackers can't pipe additional commands to crash the server.
        data = conn.recv(1024).decode().strip()
        parts = data.split('|', 1)

        if parts[0] == "HELLO":
            username = parts[1]

            # Lab 3 code
            # Function: Generates a random token and sends it to the client.
            # Security Purpose: This challenge token stops replay attacks. As said in Part C: An attacker cannot reuse the same token as each login has its own generated token.
            challenge_token = pyotp.random_base32()
            conn.send(f"CHALLENGE|{challenge_token}".encode())

            # Lab 3 code
            # Function: Receives the hashed password and OTP from the client.
            # Security Purpose: The client has to verify it knows the hashed password and OTP before verifying them.
            auth_data = conn.recv(1024).decode().strip()
            auth_parts = auth_data.split('|', 1)

            if auth_parts[0] == "AUTH":
                # Function: Splitting the hash and OTP that are separated by a comma.
                # Security Purpose: Seperates the authentication methods before verifying them.
                hash_and_otp = auth_parts[1].split(',')
                client_hash = hash_and_otp[0]
                client_otp = hash_and_otp[1]

                if username in USER_DB:
                    # Lab 3 code
                    # Function: Re-calculates the hash on the server side to compare.
                    # Security Purpose: Combining the server stored hash with the token validates the password ensuring the client is authenticated.
                    stored_hash = USER_DB[username]
                    server_check_string = stored_hash + challenge_token
                    server_computed_hash = hashlib.sha256(server_check_string.encode()).hexdigest()

                    # Lab 3 code
                    # Function: Checks the time for the OTP code
                    # Security Purpose: As said in Part C: Giving 30 seconds to enter the OTP ensures that even if an attacker steals the final password hash, they still require the OTP to get access.
                    totp = pyotp.TOTP(USER_DB[username + "_secret"])

                    if server_computed_hash == client_hash and totp.verify(client_otp):
                        conn.send("WELCOME|Authorized".encode())
                    else:
                        conn.send("ERROR|Invalid Credentials".encode())
                else:
                    # Function: Users that are not in the database are given an error message.
                    # Security Purpose: Sends an error message so attacks cannot try to bruteforce with different logins
                    conn.send("ERROR|Invalid Credentials".encode())
    except Exception as e:
        # Lab 5 code
        # Function: Catches any errors that happen during the parsing block.
        # Security Purpose: Prevents the server from completely crashing if an attacker sends malicous data.
        print("Error parsing data.")
    finally:
        conn.close()
