import socket
import getpass

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5555

def run_client():
    print("--- LAB 3 AUTHENTICATION CLIENT ---")

    # Asks user for credentials
    username = input("Enter Username: ")

    # Hides password
    password = getpass.getpass("Enter Password: ")

    otp = input("Enter 6-digit OTP: ")

    # Connects to server (used from previous labs)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_IP, SERVER_PORT))

        # Sends authentication data to the server
        payload = f"{username},{password},{otp}"
        client.send(payload.encode())

        # Response message
        response = client.recv(1024).decode()
        print("\n-----------------------------")
        print(f"SERVER RESPONSE: {response}")
        print("-----------------------------")

    except ConnectionRefusedError:
        print("Error: Could not connect to server.")
    finally:
        client.close()

if __name__ == "__main__":
    run_client()
