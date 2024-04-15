import socket

SERVER_IP = '192.168.225.1'
TCP_PORT = 49153

def main():
    try:
        # Create a TCP socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, TCP_PORT))

        # Send a message to the server
        player_name = "Alice"  # Change this to the desired player name
        client_socket.send(player_name.encode('utf-8'))
        print(f"Sent player name: {player_name}")

        # Receive a response from the server (optional)
        response = client_socket.recv(1024).decode('utf-8')
        print("Response from server:", response)

        # Close the socket
        client_socket.close()
    except ConnectionRefusedError:
        print("Failed to connect to the server. Make sure the server is running.")

if __name__ == "__main__":
    main()