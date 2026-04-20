import argparse
import getpass
import json
import socket
import struct
from pathlib import Path

from cryptography.fernet import Fernet


BUFFER_SIZE = 4096
DEFAULT_PORT = 5000
FERNET_KEY = b"BfzpofXxB261lFbVjqz0jldtKtowEoYrE0S-kE2DjQU="


def recv_line(sock: socket.socket) -> str:
    # read one full response line from the server
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            raise ConnectionError("Server closed the connection unexpectedly.")
        data += chunk
    return data.decode("utf-8").strip()


def main():
    # terminal options for server ip, port, and input file
    parser = argparse.ArgumentParser(
        description="Client-side MFA + Fernet sender for the FSCT 8561 final exam."
    )
    parser.add_argument("--server-ip", required=True, help="Server IP address or hostname.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port. Default: 5000")
    parser.add_argument(
        "--input",
        default="architect_manifesto.txt",
        help="Path to the plaintext manifesto. Default: architect_manifesto.txt",
    )
    args = parser.parse_args()

    # read the manifesto and encrypt it before sending
    input_path = Path(args.input)
    plaintext_bytes = input_path.read_bytes()
    encrypted_payload = Fernet(FERNET_KEY).encrypt(plaintext_bytes)

    # ask for the mfa login details
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")
    otp = input("Enter 6-digit OTP: ").strip()

    auth_payload = {
        "username": username,
        "password": password,
        "otp": otp,
        "filename": input_path.name,
    }

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect first, then wait for auth approval
        client.connect((args.server_ip, args.port))
        client.sendall((json.dumps(auth_payload) + "\n").encode("utf-8"))

        response = recv_line(client)
        print(f"Server response: {response}")
        if response != "AUTH_OK":
            return

        # send payload length first, then the encrypted bytes
        client.sendall(struct.pack("!Q", len(encrypted_payload)))
        client.sendall(encrypted_payload)

        final_response = recv_line(client)
        print(f"Transfer response: {final_response}")
    except ConnectionRefusedError:
        print("Error: Could not connect to the server.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
