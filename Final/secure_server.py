import argparse
import hashlib
import hmac
import json
import socket
import struct
from pathlib import Path

import pyotp
from cryptography.fernet import Fernet


HOST = "0.0.0.0"
DEFAULT_PORT = 5000
BUFFER_SIZE = 4096
FERNET_KEY = b"BfzpofXxB261lFbVjqz0jldtKtowEoYrE0S-kE2DjQU="
USER_DB = {
    "kawal": {
        "salt": "FSCT8561_SALT_2026",
        "password_hash": "8c30c404988499fc8a5974746591779f940735c6363b17eda15539a0d358adfa",
        "otp_secret": "JBSWY3DPEHPK3PXP",
    }
}


def hash_password(salt: str, plaintext_password: str) -> str:
    # hash the password with the saved salt
    digest = hashlib.sha256()
    digest.update(f"{salt}{plaintext_password}".encode("utf-8"))
    return digest.hexdigest()


def verify_login(username: str, password_input: str, otp_input: str):
    # check username, password, and otp in order
    user_record = USER_DB.get(username)
    if not user_record:
        return False, "User not found."

    candidate_hash = hash_password(user_record["salt"], password_input)
    if not hmac.compare_digest(candidate_hash, user_record["password_hash"]):
        return False, "Incorrect password."

    totp = pyotp.TOTP(user_record["otp_secret"])
    if not totp.verify(otp_input, valid_window=1):
        return False, "Invalid or expired TOTP."

    return True, "MFA verification successful."


def recv_exact(sock: socket.socket, byte_count: int) -> bytes:
    # keep reading until all expected bytes arrive
    data = b""
    while len(data) < byte_count:
        chunk = sock.recv(min(BUFFER_SIZE, byte_count - len(data)))
        if not chunk:
            raise ConnectionError("Socket closed before all expected bytes were received.")
        data += chunk
    return data


def recv_json_line(sock: socket.socket):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            raise ConnectionError("Client disconnected before sending authentication data.")
        data += chunk
    return json.loads(data.decode("utf-8").strip())


def handle_client(client_socket: socket.socket, save_dir: Path):
    try:
        # first receive the auth details from the client
        auth_request = recv_json_line(client_socket)
        username = auth_request.get("username", "")
        password = auth_request.get("password", "")
        otp = auth_request.get("otp", "")
        original_filename = auth_request.get("filename", "architect_manifesto.txt")

        success, message = verify_login(username, password, otp)
        if not success:
            client_socket.sendall(f"AUTH_FAIL|{message}\n".encode("utf-8"))
            return

        # only receive the encrypted file if mfa passed
        client_socket.sendall(b"AUTH_OK\n")

        payload_size = struct.unpack("!Q", recv_exact(client_socket, 8))[0]
        encrypted_payload = recv_exact(client_socket, payload_size)
        decrypted_payload = Fernet(FERNET_KEY).decrypt(encrypted_payload)

        # save both the encrypted and decrypted results
        save_dir.mkdir(parents=True, exist_ok=True)
        encrypted_path = save_dir / "received_manifesto.encrypted"
        decrypted_path = save_dir / f"decrypted_{Path(original_filename).name}"

        encrypted_path.write_bytes(encrypted_payload)
        decrypted_path.write_bytes(decrypted_payload)

        print(f"[AUTH OK] {username} authenticated successfully.")
        print(f"[RECEIVED] Saved encrypted payload to: {encrypted_path.resolve()}")
        print(f"[DECRYPTED] Saved plaintext manifesto to: {decrypted_path.resolve()}")

        client_socket.sendall(f"TRANSFER_OK|Saved to {decrypted_path.name}\n".encode("utf-8"))
    except Exception as exc:
        error_message = f"SERVER_ERROR|{exc}\n"
        try:
            client_socket.sendall(error_message.encode("utf-8"))
        except OSError:
            pass
        print(error_message.strip())
    finally:
        client_socket.close()


def main():
    # terminal settings for host, port, and output folder
    parser = argparse.ArgumentParser(
        description="Server-side MFA gateway and Fernet decryption receiver for the FSCT 8561 final exam."
    )
    parser.add_argument("--host", default=HOST, help="Bind address. Default: 0.0.0.0")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Listening port. Default: 5000")
    parser.add_argument(
        "--output-dir",
        default="server_output",
        help="Directory to store encrypted and decrypted output. Default: server_output",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen(1)

    print(f"[LISTENING] Server running on {args.host}:{args.port}")
    print("[MFA USER] username: kawal")
    print("[MFA USER] password: test123")
    print("[MFA USER] OTP secret for Google Authenticator: JBSWY3DPEHPK3PXP")

    while True:
        client_sock, addr = server.accept()
        print(f"[NEW CONNECTION] {addr}")
        handle_client(client_sock, output_dir)


if __name__ == "__main__":
    main()
